from flask import Flask, request, jsonify
import random
import string
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        dbname="aneesdatabase",
        user="aneesdatabase_user",
        password="C4wxOis8WgGT3zPXTgcdh8vpycpmqoCt",
        host="dpg-cuob70l6l47c73cbtgqg-a"
    ) 

# Helper function to generate a random 5-digit reset code
def generate_reset_code():
    return ''.join(random.choices(string.digits, k=5))  # Generates a 5-digit number

# Function to send reset email using Gmail SMTP
def send_reset_email(email, code):
    sender_email = "aneeschatbot@gmail.com"  
    sender_password = "ieax yvmp isgv bsqi"  

    subject = "Password Reset Code"
    body = f"Your password reset code is: {code}"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = subject

    # Add the body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Create the SMTP session
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)

        # Send email
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()  # Terminate the session

        print(f"Reset code sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")

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
    
    # Basic email format validation
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
        return jsonify({"message": "Login successful", "user_id": user[0]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401


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


if __name__ == "__main__":
    app.run(debug=True)
