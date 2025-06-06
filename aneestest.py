from flask import Flask, request, jsonify, session
import random
import string
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_session import Session
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from flask import render_template
from datetime import date
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from psycopg2.extras import RealDictCursor
import os
import re
from flask_cors import CORS
from langdetect import detect

def build_flexible_prompt(username, message, role_context):
    try:
        lang = detect(message)
        if lang == "ar":
            style = "رد كأنك صديق يفهم، بكلمات قصيرة وطبيعية، بدون رسمية."
        else:
            style = "Reply like a caring friend in short, natural English."

        return build_context_prompt(
            username,
            message,
            f"{role_context} {style}"
        )
    except:
        # fallback to English if language can't be detected
        return build_context_prompt(
            username,
            message,
            f"{role_context} Reply in short, natural English like a friend."
        )


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.debug = True
# Configure session
app.config["SECRET_KEY"] = "12345"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def get_db_connection():
    return psycopg2.connect(
        dbname="aneesdatabase",
        user="aneesdatabase_user",
        password="C4wxOis8WgGT3zPXTgcdh8vpycpmqoCt",
        host="dpg-cuob70l6l47c73cbtgqg-a"
    )

llm = ChatGroq(
    temperature=0,
    groq_api_key="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",
    model_name="LLaMA3-8B-8192"
)
DB_CONFIG = {
    "dbname": "neondb",
    "user": "neondb_owner",
    "password": "npg_5jbqJcQnrk7K",
    "host": "ep-small-snowflake-a59tq9qy-pooler.us-east-2.aws.neon.tech",
    "port": "5432"
}

def save_message(username, message, role):
    conn, cur = None, None
    try:
        conn = psycopg2.connect(**DB_CONFIG, sslmode='require')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversations (username, message, role) VALUES (%s, %s, %s)",
            (username, message, role)
        )
        conn.commit()
    except Exception as e:
        print("DB Save Error:", e)
    finally:
        if cur: cur.close()
        if conn: conn.close()

def get_conversation_history(username, limit=10):
    conn, cur = None, None
    try:
        conn = psycopg2.connect(**DB_CONFIG, sslmode='require')
        cur = conn.cursor()
        cur.execute("""
            SELECT role, message FROM conversations
            WHERE username = %s ORDER BY timestamp DESC LIMIT %s
        """, (username, limit))
        return cur.fetchall()
    except Exception as e:
        print("DB Read Error:", e)
        return []
    finally:
        if cur: cur.close()
        if conn: conn.close()


# generate a random 5-digit reset code
def generate_reset_code():
    return ''.join(random.choices(string.digits, k=5))

# send reset email using gmail smtp
def send_reset_email(email,code):
    sender_email = "aneeschatbot@gmail.com"
    sender_password = "ieax yvmp isgv bsqi"

 # HTML email content
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
            }}
            .container {{
                background: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
                max-width: 500px;
                margin: auto;
                text-align: center;
            }}
            .logo {{
                width: 100px;
                margin-bottom: 20px;
            }}
            .button {{
                display: inline-block;
                background-color: #007BFF;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            .code {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }}
            .footer {{
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <img class="logo" src="https://example.com/logo.png" alt="Company Logo">
            <h2>Password Reset Request</h2>
            <p>Hey buddy,</p>
            <p>Uh-oh! Did you forget your password? No worries, I got your back! 🎒</p>
            <p>Just enter this code in the app, and you'll be good to go:</p>
            <p class="code">{code}</p>
            <p>Hurry! it wont last forever</p>
            <p>Need help? I'm always here for you. 💙</p>
        <div class="footer">
            <p>Your friend 🤖</p>
            <p>&copy; 2025 Anees. Always here for you! 🫂</p>
        </div>
        </div>
    </body>
    </html>
    """

    subject = "🔐 Your Reset Code!"
    

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        print(f"Reset code sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")

# Request Password Reset Route
@app.route("/request_reset_password", methods=["POST"])
def request_reset_password():
    data = request.json
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the email exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user:
            reset_code = generate_reset_code()

            # Save the reset code in the database
            cur.execute(
                "INSERT INTO password_reset_codes (user_id, code, expires_at) VALUES (%s, %s, NOW() + INTERVAL '10 minutes')", 
                (user[0], reset_code)
            )
            conn.commit()

            # Send the reset code via email
            send_reset_email(email, reset_code)

            cur.close()
            conn.close()

            return jsonify({"message": "Password reset email sent!"}), 200
        else:
            return jsonify({"error": "Email not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Reset Password Route
@app.route("/reset_password_with_code", methods=["POST"])
def reset_password_with_code():
    data = request.json
    code = data.get("code")
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get the user based on the reset code
        cur.execute("SELECT user_id FROM password_reset_codes WHERE code = %s", (code,))
        user_code = cur.fetchone()

        if user_code:
            user_id = user_code[0]
            hashed_password = generate_password_hash(new_password)

            # Update the user's password
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
            conn.commit()

            # Delete the used reset code
            cur.execute("DELETE FROM password_reset_codes WHERE code = %s", (code,))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({"message": "Password reset successfully!"}), 200
        else:
            return jsonify({"error": "Invalid or expired reset code"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Sign-up Route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request format"}), 400

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password or not email:
        return jsonify({"error": "All fields are required"}), 400

    if "@" not in email or "." not in email:
        return jsonify({"error": "Invalid email format"}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", 
                    (username, hashed_password, email))
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

# Sign-in Route
@app.route("/signin", methods=["POST"])
def signin():
    data = request.json
    username_or_email = data.get("username")  # This could be email or username
    password = data.get("password")

    if not username_or_email or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if it's an email or username and adjust the query accordingly
    if "@" in username_or_email:  # Assuming email contains "@"
        cur.execute("SELECT id, password FROM users WHERE email = %s", (username_or_email,))
    else:
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username_or_email,))
   
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user[1], password):
        # session["user_id"] = user[0]  # Store user ID in session
        user_id = user[0]
        session["user_id"] = user_id
        print(f"User {user_id} signed in.")
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

#profile page  
@app.route("/profile", methods=["POST"])
def get_profile():
    data = request.get_json()
    username = data.get("username")

    if not username:
        return jsonify({"error": "Username is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, email, password, bot_name, chat_password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            return jsonify({
            "username": user[0],
            "email": user[1],
            "password": user[2],
            "bot_name": user[3],
            "chat_password": user[4]
            }), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#update profile
@app.route("/update_profile", methods=["POST"])
def update_profile():
    data = request.get_json()
    username = data.get("username")  # نجيب اليوزرنيم من الريكوست

    if not username:
        return jsonify({"error": "Username is required"}), 400

    email = data.get("email")
    password = data.get("password")  # plaintext
    bot_name = data.get("bot_name")
    chat_password = data.get("chat_password")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # نحضر اليوزر ونتأكد انه موجود
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404

        user_id = result[0]  # نحصل الـ id من قاعدة البيانات

        # نجهز التحديثات
        updates = []
        values = []

        if email:
            updates.append("email = %s")
            values.append(email)
        if password:
            hashed = generate_password_hash(password)
            updates.append("password = %s")
            values.append(hashed)
        if bot_name:
            updates.append("bot_name = %s")
            values.append(bot_name)
        if chat_password:
            updates.append("chat_password = %s")
            values.append(chat_password)

        if not updates:
            return jsonify({"message": "No fields to update"}), 400

        update_query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
        values.append(user_id)

        cur.execute(update_query, tuple(values))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Profile updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
#chat password page
@app.route("/chat_password", methods=["POST"])
def verify_chat_password():
    data = request.get_json()
    username = data.get("username") 
    entered_password = data.get("password")

    if not username or not entered_password or len(entered_password) != 6:
        return jsonify({"error": "Missing or invalid input"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT chat_password FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and result[0] == entered_password:
            return jsonify({"message": "Password verified successfully"}), 200
        else:
            return jsonify({"error": "Incorrect chat password"}), 403

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Home Page Route
@app.route("/home", methods=["GET"])
def home():
    response = {  
        "choices": [
            {"title": "Talk to Me", "description": "Chat for diagnosis"},
            {"title": "Treatment", "description": "View recommended treatments"},
            {"title": "Emergency", "description": "Get emergency help"}
        ],
        "navigation": [
            "Home",
            "Social Space",
            "Progress Tracker",
            "Profile"
        ]
    }
    return jsonify(response), 200


# Emergency Contacts Route
@app.route("/emergency", methods=["GET"])
def get_emergency_contacts():
    username = session.get("username")  # Get username from session
    if not username:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        contacts = cur.fetchall()
        cur.close()
        conn.close()

        contacts = [{"name": row[0], "phone": row[1]} for row in contacts] if contacts else [{"name": "Father", "phone": "0000000"}]
        return jsonify({"contacts": contacts, "mental_health_center": "https://ncmh.org.sa/"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add Emergency Contact Route
@app.route("/add_emergency_contact", methods=["POST"])
def add_emergency_contact():
    username = session.get("username")  # Get username from session
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")

    if not username or not name or not phone:
        return jsonify({"error": "Username, name, and phone are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Step 1: Get user_id from username
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if not result:
            return jsonify({"error": "User not found"}), 404
        user_id = result[0]

        # Step 2: Insert emergency contact
        cur.execute("INSERT INTO emergency_contacts (user_id, name, phone) VALUES (%s, %s, %s)",
                    (user_id, name, phone))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Emergency contact added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/search_users", methods=["GET"])
def search_users():
    search_term = request.args.get("username", "")
#https://anees-rus4.onrender.com/search_users?username=kadi
    if not search_term:
        return jsonify({"error": "Username is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE username LIKE %s", (f"%{search_term}%",))
        users = cur.fetchall()

        if not users:
            return jsonify({"message": "No users found"}), 404
        
        user_list = [{"id": user[0], "username": user[1]} for user in users]
        return jsonify(user_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        cur.close()
        conn.close()

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content")
#https://anees-rus4.onrender.com/send_message
#{
#  "sender_id": 7,
#  "receiver_id": 6,
#  "content": "Hello, how are you?"
#``}

    if not sender_id or not receiver_id or not content:
        return jsonify({"error": "Sender ID, receiver ID, and content are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert the message into the database
        cur.execute(
            "INSERT INTO messages (sender_id, receiver_id, content) VALUES (%s, %s, %s)",
            (sender_id, receiver_id, content)
        )
        conn.commit()
        return jsonify({"message": "Message sent successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/chat_history/<int:username>", methods=["GET"])
def get_chat_history(username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get messages where the user is either the sender or receiver
        cur.execute("""
            SELECT sender_id, receiver_id, content, timestamp
            FROM messages
            WHERE sender_id = %s OR receiver_id = %s
            ORDER BY timestamp ASC
        """, (username, username))
        messages = cur.fetchall()

        if not messages:

            return jsonify({"message": "No chat history found"}), 404
        # Format the messages into a list of dictionaries
        chat_history = [

            {

                "sender_id": message[0],

                "receiver_id": message[1],

                "content": message[2],

                "timestamp": message[3].strftime("%Y-%m-%d %H:%M:%S")
            }
            for message in messages
        ]
        return jsonify(chat_history), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

def build_context_prompt(username, message, role_description):
    history = get_conversation_history(username, limit=10)
    context = ""
    for role, msg in reversed(history):
        context += f"{username}: {msg}\n"
    return f"""{role_description}

{context}
user: {message}
assistant:"""

def calculate_mood_level(text):
    keywords = {
        "stress": ["stress", "tension", "nervous", "anxiety", "الإجهاد", "التوتر", "العصبية", "القلق"],
        "anxiety": ["anxious", "worry", "fear", "قلق", "خوف"],
        "panic": ["panic", "attack", "overwhelmed", "ذعر", "هجوم", "مُثقل"],
        "loneliness": ["lonely", "isolated", "alone", "وحيد", "منعزل", "وحده"],
        "burnout": ["burnout", "exhausted", "tired", "الإرهاق", "التعب"],
        "depression": ["depressed", "down", "sad", "hopeless", "مكتئب", "حزين", "يائس"]
    }

    mood_scores = {}
    for mood, words in keywords.items():
        score = sum(word in text.lower() for word in words) * 25
        mood_scores[f"{mood}_level"] = min(score, 100)

    return mood_scores

def build_flexible_prompt(username, message, role_context):
    try:
        lang = detect(message)
        if lang == "ar":
            style = "رد كأنك صديق يفهم، بكلمات قصيرة وطبيعية، بدون رسمية."
        else:
            style = "Reply like a caring friend in short, natural English."

        return build_context_prompt(
            username,
            message,
            f"{role_context} {style}"
        )
    except:
        # fallback to English if language can't be detected
        return build_context_prompt(
            username,
            message,
            f"{role_context} Reply in short, natural English like a friend."
        )

@app.route("/diagnosis", methods=["POST"])
def diagnosis_route():
    try:
        data = request.get_json()
        username = data.get("username")
        message = data.get("message")

        if not username or not message:
            return jsonify({"error": "Missing username or message"}), 400

        print(">> Incoming /diagnosis")
        save_message(username, message, "user")

        mood = calculate_mood_level(message)

         # حفظ بيانات المزاج في قاعدة البيانات
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO progress_tracker (
                username, date, stress_level, anxiety_level, 
                panic_level, loneliness_level, 
                burnout_level, depression_level
            ) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s)
        """, (
            username,
            mood['stress_level'],
            mood['anxiety_level'],
            mood['panic_level'],
            mood['loneliness_level'],
            mood['burnout_level'],
            mood['depression_level']
        ))
        
        conn.commit()
    
        prompt = build_flexible_prompt(
            username,
             message,
             "You are a supportive mental wellness assistant."
        )

        llm_response = llm.invoke(prompt)
        response = getattr(llm_response, "content", str(llm_response)).strip()
        response = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9.,?!؛،\s\n]", "", response) 

        save_message(username, response, "assistant")

        return jsonify({
            "response": response,
            "mood_scores": mood
        })
    except Exception as e:
        print(">> Error in /diagnosis:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/cognitive", methods=["POST"])
def cognitive_route():
    try:
        data = request.get_json()
        username = data.get("username")
        message = data.get("message")

        if not username or not message:
            return jsonify({"error": "Missing username or message"}), 400

        print(">> Incoming /cognitive")
        save_message(username, message, "user")

        prompt = build_flexible_prompt(
            username,
            message,
             "You are a CBT chatbot that helps the user identify and reframe negative thoughts."
        )
        llm_response = llm.invoke(prompt)
        response = getattr(llm_response, "content", str(llm_response)).strip()
        response = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9.,?!؛،\s\n]", "", response) 
        save_message(username, response, "assistant")

        return jsonify({"response": response})
    except Exception as e:
        print(">> Error in /cognitive:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/act", methods=["POST"])
def act_route():
    try:
        data = request.get_json()
        username = data.get("username")
        message = data.get("message")

        if not username or not message:
            return jsonify({"error": "Missing username or message"}), 400

        print(">> Incoming /act")
        save_message(username, message, "user")

        prompt = build_flexible_prompt(
            username,
             message,
            "You are an ACT chatbot who helps the user accept their emotions and take value-based actions."
        )           

        llm_response = llm.invoke(prompt)
        response = getattr(llm_response, "content", str(llm_response)).strip()
        response = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9.,?!؛،\s\n]", "", response) 

        save_message(username, response, "assistant")

        return jsonify({"response": response})
    except Exception as e:
        print(">> Error in /act:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/physical", methods=["POST"])
def physical_route():
    try:
        data = request.get_json()
        username = data.get("username")
        message = data.get("message")

        if not username or not message:
            return jsonify({"error": "Missing username or message"}), 400

        print(">> Incoming /physical")
        save_message(username, message, "user")

        prompt = build_flexible_prompt(
             username,
             message,
             "You are a physical wellness chatbot that shares simple activity advice."
        )

        llm_response = llm.invoke(prompt)
        response = getattr(llm_response, "content", str(llm_response)).strip()
        response = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9.,?!؛،\s\n]", "", response) 

        save_message(username, response, "assistant")

        return jsonify({"response": response})
    except Exception as e:
        print(">> Error in /physical:", e)
        return jsonify({"error": str(e)}), 500
    
@app.route("/user_aggregated_mood_data/<username>", methods=["GET"])
def get_user_aggregated_mood_data(username):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # استعلام لجمع متوسط بيانات المزاج لمستخدم معين
        cur.execute("""
            SELECT 
                AVG(stress_level) as avg_stress,
                AVG(anxiety_level) as avg_anxiety,
                AVG(panic_level) as avg_panic,
                AVG(loneliness_level) as avg_loneliness,
                AVG(burnout_level) as avg_burnout,
                AVG(depression_level) as avg_depression
            FROM progress_tracker
            WHERE username = %s
        """, (username,))
        
        averages = cur.fetchone()
        
        if not any(averages):
            return jsonify({"message": "No data found for this user"}), 404
            
        response = {
            "username": username,
            "average_mood_levels": {
                "stress": round(float(averages[0]), 2),
                "anxiety": round(float(averages[1]), 2),
                "panic": round(float(averages[2]), 2),
                "loneliness": round(float(averages[3]), 2),
                "burnout": round(float(averages[4]), 2),
                "depression": round(float(averages[5]), 2)
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

# حفظ المزاج اليومي
@app.route("/save-daily-mood/", methods=["POST"])
def save_daily_mood():
    data = request.get_json()
    username = data.get("username")
    mood_value = data.get("mood_value")
    today = (datetime.utcnow() + timedelta(hours=3)).date()

    conn = get_db_connection()
    cur = conn.cursor()

    # التحقق من وجود المستخدم
    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # حذف أي بيانات مزاج موجودة لنفس اليوم
    cur.execute("""
        DELETE FROM daily_mood 
        WHERE username = %s AND mood_date = %s
    """, (username, today))

    # إدخال بيانات المزاج الجديدة
    cur.execute("""
        INSERT INTO daily_mood (username, mood_date, mood_value)
        VALUES (%s, %s, %s)
    """, (username, today, mood_value))

    conn.commit()
    conn.close()

    return {"message": "تم حفظ المزاج اليومي بنجاح ✅", "date": str(today)}

@app.route("/get-weekly-mood/<username>", methods=["GET"])
def get_weekly_mood(username):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # التحقق من وجود المستخدم
    cur.execute("SELECT username FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="المستخدم غير موجود")

    # جلب بيانات آخر 7 أيام
    cur.execute("""
        SELECT mood_date, mood_value 
        FROM daily_mood
        WHERE username = %s
        ORDER BY mood_date DESC
        LIMIT 7
    """, (username,))
    
    moods = cur.fetchall()
    conn.close()

   

    weekly_data = []
    for mood in moods:
        weekly_data.append({
            "date": mood['mood_date'],
            "mood_value": mood['mood_value']
        })

    # ترتيب حسب التاريخ (من الأقدم للأحدث)
    weekly_data_sorted = sorted(weekly_data, key=lambda x: x['date'])

    return {
        "username": username,
        "weekly_moods": weekly_data_sorted
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)