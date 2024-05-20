import os
import hashlib
import bcrypt
from flask import (
    Flask,
    request,
    make_response,
    redirect,
    url_for,
    render_template,
    session,
    g,
)
from database import get_db_connection

app = Flask(__name__)
app.secret_key = os.urandom(33)


# Generate a secure token
def generate_token():
    return hashlib.sha256(os.urandom(64)).hexdigest()


# Hash the password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


# Verify the password
def verify_password(stored_hash, entered_password):
    return bcrypt.checkpw(entered_password.encode("utf-8"), stored_hash.encode("utf-8"))


# Store a token in the database
def store_token(user_id, token):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO UserTokens (UserID, Token) VALUES (%s, %s)", (user_id, token)
    )
    connection.commit()
    cursor.close()
    connection.close()


# Set a remember me cookie
def set_remember_me_cookie(response, token):
    response.set_cookie(
        "remember_me_token", token, max_age=30 * 24 * 60 * 60, httponly=True
    )  # Cookie valid for 30 days


# Get user by token
def get_user_by_token(token):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT UserID FROM UserTokens WHERE Token = %s", (token,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        return result[0]  # Return the UserID
    return None


# Add a new user
def add_user(email, username, password):
    hashed_password = hash_password(password)
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO Users (Email, Username, PasswordHash) VALUES (%s, %s, %s)",
        (email, username, hashed_password),
    )
    connection.commit()
    cursor.close()
    connection.close()


# Authenticate user
def authenticate_user(username, entered_password):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT UserID, PasswordHash FROM Users WHERE Username = %s", (username,)
    )
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        user_id, stored_hash = result
        if verify_password(stored_hash, entered_password):
            return user_id
    return None


# Delete user token
def delete_token_for_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM UserTokens WHERE UserID = %s", (user_id,))
    connection.commit()
    cursor.close()
    connection.close()


# Routes
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("signin"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        session.pop("user", None)
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["re_pass"]

        if password != confirm_password:
            return "Passwords do not match", 400

        if not request.form.get("agree-term"):
            return "You must agree to the terms of service", 400

        add_user(email, username, password)
        return redirect(url_for("signin"))
    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        session.pop("user", None)
        username = request.form["username"]
        password = request.form["password"]
        remember_me = request.form.get("remember_me")

        user_id = authenticate_user(username, password)
        if user_id:
            session["user"] = user_id
            response = make_response(redirect(url_for("dashboard")))
            if remember_me:
                token = generate_token()
                store_token(user_id, token)
                set_remember_me_cookie(response, token)
            return response
        return "Invalid credentials", 401
    return render_template("signin.html")


@app.route("/dashboard")
def dashboard():
    token = request.cookies.get("remember_me_token")
    if token:
        user_id = get_user_by_token(token)
        if user_id:
            session["user"] = user_id
            return render_template("dashboard.html", user=user_id)
    return redirect(url_for("signin"))


@app.route("/logout")
def logout():
    if "user" in session:
        user_id = session["user"]
        delete_token_for_user(user_id)  # Delete token for the current user
        session.pop("user", None)
        response = make_response(render_template("logout.html"))
        response.delete_cookie("remember_me_token")
        return response
    return redirect(url_for("signin"))


@app.before_request
def before_request():
    g.user = None
    if "user" in session:
        g.user = session["user"]


@app.route("/<string:page_name>")
def page(page_name="/"):
    try:
        return render_template(page_name + ".html")
    except:
        return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
