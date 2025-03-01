from flask import Flask, request, jsonify
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database connection
def get_db_connection():
    return psycopg2.connect(
       dbname="aneestest",
        user="kadialrabah",
        password="C4wxOis8WgGT3zPXTgcdh8vpycpmqoCt",
        
        host="dpg-cuob70l6l47c73cbtgqg-a"
    ) 

# Sign-up Route
@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()  # Ensure request body is JSON
    
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
    
    # Helper function to generate a random reset token
def generate_reset_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=20))

# Simulated function to send reset email (replace with actual email service)
def send_reset_email(email, token):
    reset_link = f"https://anees-rus4.onrender.com/reset_password/{token}"
    print(f"Reset password link (send this to {email}): {reset_link}")

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
            reset_token = generate_reset_token()

            # Save the reset token in the database for this user
            cur.execute(
                "INSERT INTO password_reset_tokens (user_id, token) VALUES (%s, %s)", 
                (user[0], reset_token)
            )
            conn.commit()

            send_reset_email(email, reset_token)

            cur.close()
            conn.close()

            return jsonify({"message": "Password reset email sent!"}), 200
        else:
            return jsonify({"error": "Email not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    # Reset Password Route
@app.route("/reset_password/<token>", methods=["POST"])
def reset_password(token):
    data = request.json
    new_password = data.get("new_password")

    if not new_password:
        return jsonify({"error": "New password is required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Get the user based on the reset token
        cur.execute("SELECT user_id FROM password_reset_tokens WHERE token = %s", (token,))
        user_token = cur.fetchone()

        if user_token:
            user_id = user_token[0]
            hashed_password = generate_password_hash(new_password)

            # Update the user's password
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
            conn.commit()

            # Delete the used reset token
            cur.execute("DELETE FROM password_reset_tokens WHERE token = %s", (token,))
            conn.commit()

            cur.close()
            conn.close()

            return jsonify({"message": "Password reset successfully!"}), 200
        else:
            return jsonify({"error": "Invalid or expired token"}), 400

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
