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
from mysql.connector import Error
from datetime import datetime


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


def add_food_item_and_log(user_id, name, proteins, carbs, fats, date=None, quantity=1):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Set date as current date if not provided explicitly
        if date is None:
            date = datetime.now().date()

        # Check if the food item already exists for the user
        check_food_query = """
        SELECT FoodID FROM Food WHERE UserID = %s AND Name = %s AND Proteins = %s AND Carbs = %s AND Fats = %s
        """
        check_food_data = (user_id, name, proteins, carbs, fats)
        cursor.execute(check_food_query, check_food_data)
        food_id = cursor.fetchone()

        if not food_id:
            # Food item doesn't exist, insert into Food table
            insert_food_query = """
            INSERT INTO Food (UserID, Name, Proteins, Carbs, Fats) VALUES (%s, %s, %s, %s, %s)
            """
            food_data = (user_id, name, proteins, carbs, fats)
            cursor.execute(insert_food_query, food_data)
            food_id = cursor.lastrowid
        else:
            food_id = food_id[0]

        # Ensure log entry exists for the user on the given date
        check_log_query = """
        SELECT LogID FROM Logs WHERE UserID = %s AND Date = %s
        """
        check_log_data = (user_id, date)
        cursor.execute(check_log_query, check_log_data)
        log_id = cursor.fetchone()

        if not log_id:
            # Log entry doesn't exist, insert into Logs table
            insert_log_query = """
            INSERT INTO Logs (UserID, Date) VALUES (%s, %s)
            """
            log_data = (user_id, date)
            cursor.execute(insert_log_query, log_data)
            log_id = cursor.lastrowid
        else:
            log_id = log_id[0]

        # Insert into LogFood table
        insert_log_food_query = """
        INSERT INTO LogFood (LogID, FoodID, Quantity) VALUES (%s, %s, %s)
        """
        log_food_data = (log_id, food_id, quantity)
        cursor.execute(insert_log_food_query, log_food_data)
        connection.commit()

        print("Food item added to log successfully!")

    except Error as e:
        print(f"Error adding food item and log: {e}")

    finally:
        cursor.close()
        connection.close()


def extract_existing_foods(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT f.FoodID, f.Name, f.Proteins, f.Carbs, f.Fats, f.Calories, lf.Quantity FROM Food f JOIN LogFood lf ON f.FoodID = lf.FoodID JOIN Logs l ON lf.LogID = l.LogID WHERE l.UserID = %s"

        cursor.execute(query, (user_id,))
        foods = cursor.fetchall()
        print(foods)
        return foods
    except Error as error:
        print("Error retrieving user foods:", error)
    finally:
        cursor.close()
        connection.close()


# Routes
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("dashboard"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if g.user:
        return redirect(url_for("dashboard"))
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
    if g.user:
        return redirect(url_for("dashboard"))
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
    if g.user:
        return render_template("dashboard.html", user=g.user)
    return redirect(url_for("signin"))


@app.route("/add", methods=["GET", "POST"])
def add():
    if g.user:
        if request.method == "POST":
            food_name = request.form["food-name"]
            quantity = request.form["quantity"]
            proteins = request.form["protein"]
            carbohydrates = request.form["carbohydrates"]
            fats = request.form["fat"]
            add_food_item_and_log(
                g.user, food_name, proteins, carbohydrates, fats, quantity=quantity
            )
            foods = extract_existing_foods(g.user)
            return render_template("add.html", foods=foods, user=g.user)
        foods = extract_existing_foods(g.user)
        return render_template("add.html", foods=foods, user=g.user)
    return redirect(url_for("signin"))


@app.route("/delete_food/<int:food_id>", methods=["POST"])
def delete_food(food_id):
    if g.user:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            # Delete from LogFood table
            cursor.execute(
                "DELETE lf FROM LogFood lf JOIN Food f ON lf.FoodID = f.FoodID WHERE f.UserID = %s AND f.FoodID = %s",
                (g.user, food_id),
            )

            # Delete from Food table
            cursor.execute(
                "DELETE FROM Food WHERE UserID = %s AND FoodID = %s",
                (g.user, food_id),
            )

            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for("add"))

        except Error as e:
            print(f"Error deleting food item: {e}")
            return "An error occurred while deleting the food item", 500

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
    else:
        token = request.cookies.get("remember_me_token")
        if token:
            user_id = get_user_by_token(token)
            if user_id:
                session["user"] = user_id
                g.user = user_id


@app.route("/<string:page_name>")
def page(page_name="/"):
    try:
        return render_template(page_name + ".html")
    except:
        return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
