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
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
import subprocess

app = Flask(__name__)

# Configure session
app.config["SECRET_KEY"] = "12345"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="aneesdatabase",
        user="aneesdatabase_user",
        password="C4wxOis8WgGT3zPXTgcdh8vpycpmqoCt",
        host="dpg-cuob70l6l47c73cbtgqg-a"
    )

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
@app.route("/reset_password/<code>", methods=["POST"])
def reset_password(code):
    data = request.json
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
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user[1], password):
        #session["user_id"] = user[0]  # Store user ID in session
        user_id = user[0] 
        session["user_id"] = user_id
        print(f"User {user_id} signed in.")
        subprocess.Popen(["python", "chatbot_gen_ai.py", str(user_id)])
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401
   

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"error": "You must be signed in to chat!"}), 401

    # Get query from user
    query = request.json.get("query")
    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Initialize LLM and Vector DB
    llm = initialize_llm()
    vector_db = create_vector_db()
    qa_chain = setup_qa_chain(vector_db, llm)

    # Get the response
    response = qa_chain.run(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)


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
    user_id = session.get("user_id")  # get user id from session
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, phone FROM emergency_contacts WHERE user_id = %s", (user_id,))
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
    user_id = session.get("user_id")
    data = request.get_json()
    name = data.get("name")
    phone = data.get("phone")

    if not user_id or not name or not phone:
        return jsonify({"error": "Name and phone are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
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

@app.route("/chat_history/<int:user_id>", methods=["GET"])
def get_chat_history(user_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get messages where the user is either the sender or receiver
        cur.execute("""
            SELECT sender_id, receiver_id, content, timestamp
            FROM messages
            WHERE sender_id = %s OR receiver_id = %s
            ORDER BY timestamp ASC
        """, (user_id, user_id))
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

if __name__ == "__main__":
    app.run(debug=True)
