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
import os

app = Flask(__name__)
app.debug = True
# Configure session
app.config["SECRET_KEY"] = "12345"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

embedding_model = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
base_data_path = os.path.join(os.getcwd(), "data")

cognitive_path = os.path.join(base_data_path, "cognitive_therapyDATA")
act_path = os.path.join(base_data_path, "act_therapyDATA")
physical_path = os.path.join(base_data_path, "physical_therapyDATA")
diagnosis_path = os.path.join(base_data_path, "diagnosisDATA")

# Cognitive Therapy DB
cognitive_db_path = "./chroma_db/cognitive"
if os.path.exists(cognitive_db_path):
    cognitive_vector_db = Chroma(persist_directory=cognitive_db_path, embedding_function=embedding_model)
else:
    loader = DirectoryLoader(cognitive_path, glob="*.pdf", loader_cls=PyPDFLoader)
    texts = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(loader.load())
    cognitive_vector_db = Chroma.from_documents(texts, embedding_model, persist_directory=cognitive_db_path)
    cognitive_vector_db.persist()

# ACT Therapy DB
act_db_path = "./chroma_db/act"
if os.path.exists(act_db_path):
    act_vector_db = Chroma(persist_directory=act_db_path, embedding_function=embedding_model)
else:
    loader = DirectoryLoader(act_path, glob="*.pdf", loader_cls=PyPDFLoader)
    texts = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(loader.load())
    act_vector_db = Chroma.from_documents(texts, embedding_model, persist_directory=act_db_path)
    act_vector_db.persist()

# Physical Therapy DB
physical_db_path = "./chroma_db/physical"
if os.path.exists(physical_db_path):
    physical_vector_db = Chroma(persist_directory=physical_db_path, embedding_function=embedding_model)
else:
    loader = DirectoryLoader(physical_path, glob="*.pdf", loader_cls=PyPDFLoader)
    texts = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(loader.load())
    physical_vector_db = Chroma.from_documents(texts, embedding_model, persist_directory=physical_db_path)
    physical_vector_db.persist()

# Diagnosis DB
diagnosis_db_path = "./chroma_db/diagnosis"
if os.path.exists(diagnosis_db_path):
    diagnosis_vector_db = Chroma(persist_directory=diagnosis_db_path, embedding_function=embedding_model)
else:
    loader = DirectoryLoader(diagnosis_path, glob="*.pdf", loader_cls=PyPDFLoader)
    texts = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(loader.load())
    diagnosis_vector_db = Chroma.from_documents(texts, embedding_model, persist_directory=diagnosis_db_path)
    diagnosis_vector_db.persist()


# Shared LLM
llm = ChatGroq(
    temperature=0,
    groq_api_key="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",
    model_name="llama-3.3-70b-versatile"
)

# Now we import chat modules with access to shared models
from diagnosis import get_diagnosis_response
from cognitive_therapy import get_cognitive_response
from acceptance_commitment import get_act_response
from physical_activity import get_physical_response

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
@app.route("/profile", methods=["GET"])
def get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, age, email, bot_name, chat_password FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        cur.close()
        conn.close()

        if user:
            return jsonify({
                "username": user[0],
                "age": user[1],
                "email": user[2],
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
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    data = request.json
    username = data.get("username")
    age = data.get("age")
    email = data.get("email")
    password = data.get("password")  # plaintext
    bot_name = data.get("bot_name")
    chat_password = data.get("chat_password")

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Only update fields that are provided
        updates = []
        values = []

        if username:
            updates.append("username = %s")
            values.append(username)
        if age:
            updates.append("age = %s")
            values.append(age)
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
    user_id = session.get("user_id")  # Use session to get current user

    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    data = request.get_json()
    entered_password = data.get("chat_password")

    if not entered_password or len(entered_password) != 6:
        return jsonify({"error": "Invalid password format"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT chat_password FROM users WHERE id = %s", (user_id,))
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
    user_id = session.get("user_id")  # get user id from session
    #user_id = request.args.get("user_id")  # get user_id from query parameters
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
    #user_id = request.args.get("user_id")  # get user_id from query parameters
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

@app.route('/diagnosis', methods=['POST'])
def diagnosis_route():
    try:
        data = request.get_json()
        message = data.get("message")
        user_id = data.get("user_id")

        result = get_diagnosis_response(user_id, message, diagnosis_vector_db, llm)

        return jsonify({
            "response": result["reply"],
            "mood_analysis": result["mood"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cognitive', methods=['POST'])
def cognitive_route():
    try:
        data = request.get_json()
        message = data.get("message")
        user_id = data.get("user_id")

        response = get_cognitive_response(user_id, message, cognitive_vector_db, llm)

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/act', methods=['POST'])
def act_route():
    try:
        data = request.get_json()
        message = data.get("message")
        user_id = data.get("user_id")

        response = get_act_response(user_id, message, act_vector_db, llm)

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/physical', methods=['POST'])
def physical_route():
    try:
        data = request.get_json()
        message = data.get("message")
        user_id = data.get("user_id")

        response = get_physical_response(user_id, message, physical_vector_db, llm)

        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)