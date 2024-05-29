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
app.config["SESSION_PERMANENT"] = False


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
    max_age = 30 * 24 * 60 * 60  # Cookie valid for 30 days
    if session.get("remember_me"):
        response.set_cookie("remember_me_token", token, max_age=max_age, httponly=True)
    else:
        # Set a session cookie that expires when the browser is closed
        response.set_cookie("remember_me_token", token, httponly=True)


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


def add_food_item(user_id, name, proteins, carbs, fats):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert into Food table
        insert_food_query = """
        INSERT INTO Food (UserID, Name, Proteins, Carbs, Fats) VALUES (%s, %s, %s, %s, %s)
        """
        food_data = (user_id, name, proteins, carbs, fats)
        cursor.execute(insert_food_query, food_data)

        connection.commit()
        cursor.close()
        connection.close()

        print("Food item added successfully!")

    except Error as e:
        print(f"Error adding food item: {e}")


def extract_existing_foods(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT FoodID, Name, Proteins, Carbs, Fats, Calories FROM Food WHERE UserID = %s"

        cursor.execute(query, (user_id,))
        foods = cursor.fetchall()
        cursor.close()
        connection.close()
        return foods
    except Error as error:
        print("Error retrieving user foods:", error)


def get_food_data(food_id, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT Name, Proteins, Carbs, Fats FROM Food WHERE UserID = %s AND FoodID = %s"

        cursor.execute(
            query,
            (
                user_id,
                food_id,
            ),
        )

        foods = cursor.fetchone()
        food_data = {
            "food_id": food_id,
            "food_name": foods[0],
            "proteins": foods[1],
            "carbohydrates": foods[2],
            "fats": foods[3],
        }

        connection.commit()
        cursor.close()
        connection.close()

        return food_data

    except Error as e:
        print(f"Error finding food item: {e}")
        return "An error occurred while finding the food item", 500


def update_food_data(food_name, proteins, carbohydrates, fats, food_id, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Update food item in Food table
        cursor.execute(
            "UPDATE Food SET Name = %s, Proteins = %s, Carbs = %s, Fats = %s WHERE UserID = %s AND FoodID = %s",
            (food_name, proteins, carbohydrates, fats, user_id, food_id),
        )

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("add"))

    except Error as e:
        print(f"Error updating food item: {e}")
        return "An error occurred while updating the food item", 500


def get_logs(user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = """
            SELECT Logs.LogID, Logs.Date, SUM(LogFood.Quantity * Food.Proteins) AS TotalProteins,
                SUM(LogFood.Quantity * Food.Carbs) AS TotalCarbs,
                SUM(LogFood.Quantity * Food.Fats) AS TotalFats,
                SUM(LogFood.Quantity * Food.Calories) AS TotalCalories
            FROM Logs
            LEFT JOIN LogFood ON Logs.LogID = LogFood.LogID
            LEFT JOIN Food ON LogFood.FoodID = Food.FoodID
            WHERE Logs.UserID = %s
            GROUP BY Logs.LogID
            ORDER BY Logs.Date DESC
        """
        cursor.execute(query, (user_id,))
        logs = cursor.fetchall()
        cursor.close()
        connection.close()
    except Error as error:
        print("Error inserting Log:", error)

    return logs


def disp_food_list(foods):
    food_list = {}
    for food in foods:
        food_list[food[0]] = f"{food[1]} - ({food[2]} P, {food[3]} C, {food[4]} F)"
    return food_list


# Routes
@app.route("/", methods=["GET"])
def index():
    if g.user:
        logs = get_logs(g.user)

        log_dates = []

        for log in logs:
            log_dates.append(
                {
                    "log_ID": log[0],
                    "log_date": log[1],
                    "proteins": log[2] or 0,  # Use 0 if NULL
                    "carbs": log[3] or 0,
                    "fats": log[4] or 0,
                    "calories": log[5] or 0,
                }
            )
        return render_template("index.html", log_dates=log_dates)
    return redirect(url_for("signin"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if g.user:
        return redirect(url_for("index"))
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
        return redirect(url_for("index"))
    if request.method == "POST":
        session.pop("user", None)
        username = request.form["username"]
        password = request.form["password"]
        remember_me = request.form.get("remember_me")

        user_id = authenticate_user(username, password)
        if user_id:
            session["user"] = user_id
            response = make_response(redirect(url_for("index")))
            if remember_me:
                session["remember_me"] = True
                token = generate_token()
                store_token(user_id, token)
                set_remember_me_cookie(response, token)
            else:
                session.pop("remember_me", None)
            return response
        return "Invalid credentials", 401
    return render_template("signin.html")


@app.route("/add", methods=["GET", "POST"])
def add():
    if g.user:
        if request.method == "POST":
            food_name = request.form["food-name"]
            proteins = request.form["protein"]
            carbohydrates = request.form["carbohydrates"]
            fats = request.form["fat"]
            food_id = request.form.get("food-id")

            if food_id:
                update_food_data(
                    food_name, proteins, carbohydrates, fats, food_id, g.user
                )
            else:
                add_food_item(g.user, food_name, proteins, carbohydrates, fats)

        foods = extract_existing_foods(g.user)
        return render_template("add.html", foods=foods, user=g.user, food_data=None)
    return redirect(url_for("signin"))


@app.route("/edit_food/<int:food_id>", methods=["GET", "POST"])
def edit_food(food_id):
    if g.user:
        if request.method == "POST":
            food_data = get_food_data(food_id, g.user)
            foods = extract_existing_foods(g.user)
            return render_template(
                "add.html", foods=foods, user=g.user, food_data=food_data
            )
    return redirect(url_for("signin"))


@app.route("/delete_food/<int:food_id>", methods=["POST"])
def delete_food(food_id):
    if g.user:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

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


@app.route("/view/<int:log_ID>")
def view(log_ID):
    if g.user:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            # Query to get the log details including the date
            query = "SELECT * FROM Logs WHERE LogID = %s"
            cursor.execute(query, (log_ID,))
            log = cursor.fetchone()

            foods = (
                query
            ) = """
                SELECT FoodID, Name, Proteins, Carbs, Fats, Calories FROM Food WHERE UserID=%s
            """
            cursor.execute(query, (g.user,))
            foods = cursor.fetchall()
            foods = disp_food_list(foods)

            # Query to get all food items associated with the log
            query = """
                SELECT
                Food.FoodID AS FoodID,
                Food.Name AS FoodName,
                Food.Proteins AS Proteins,
                Food.Carbs AS Carbs,
                Food.Fats AS Fats,
                Food.Calories AS Calories,
                LogFood.Quantity AS Quantity
            FROM 
                Logs
            JOIN 
                LogFood ON Logs.LogID = LogFood.LogID
            JOIN 
                Food ON LogFood.FoodID = Food.FoodID
            WHERE 
                Logs.UserID = %s
                AND Logs.Date = %s
            """
            cursor.execute(query, (g.user, log[2].strftime("%Y-%m-%d")))
            log_foods = cursor.fetchall()

            # Calculate totals for proteins, carbs, fats, and calories
            totals = {"protein": 0, "carbs": 0, "fat": 0, "calories": 0}

            for food in log_foods:
                totals["protein"] += food[2] * food[6]
                totals["carbs"] += food[3] * food[6]
                totals["fat"] += food[4] * food[6]
                totals["calories"] += food[5] * food[6]

            cursor.close()
            connection.close()

            return render_template(
                "view.html",
                foods=foods,
                user=g.user,
                log=log,
                totals=totals,
                log_foods=log_foods,
            )
        except Error as error:
            print("Error inserting Log:", error)

    return redirect(url_for("signin"))


@app.route("/create_log", methods=["POST"])
def create_log():
    if g.user:
        date = request.form.get("date")
        date = datetime.strptime(date, "%Y-%m-%d")
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            query = "INSERT INTO Logs (UserID, Date) VALUES (%s, %s)"
            cursor.execute(query, (g.user, date))
            connection.commit()

            query2 = "SELECT LogID FROM Logs WHERE UserID = %s AND Date = %s"
            cursor.execute(query2, (g.user, date))
            result = cursor.fetchone()
            log_ID = result[0]
            cursor.close()
            connection.close()

        except Error as error:
            print("Error inserting Log:", error)

        return redirect(url_for("view", log_ID=log_ID))
    return redirect(url_for("signin"))


@app.route("/add_food_to_log/<int:log_ID>", methods=["POST"])
def add_food_to_log(log_ID):
    if g.user:
        selected_food = request.form.get("food-select")
        quantity = request.form.get("quantity")
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "INSERT INTO LogFood (LogID, FoodID, Quantity) VALUES (%s, %s, %s)"
            cursor.execute(query, (log_ID, int(selected_food), quantity))
            connection.commit()
            cursor.close()
            connection.close()
        except Error as error:
            print("Error adding food to log:", error)

        return redirect(url_for("view", log_ID=log_ID))
    return redirect(url_for("signin"))


@app.route("/remove_food_from_log/<int:log_ID>/<int:food_ID>", methods=["POST", "GET"])
def remove_food_from_log(log_ID, food_ID):
    if g.user:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()
            query = "DELETE FROM LogFood WHERE LogID = %s AND FoodID = %s"
            cursor.execute(query, (log_ID, food_ID))
            connection.commit()
            cursor.close()
            connection.close()
        except Error as error:
            print("Error removing food from log:", error)

            cursor.close()
            connection.close()
        return redirect(url_for("view", log_ID=log_ID))
    return redirect(url_for("signin"))


@app.route("/logout")
def logout():
    if "user" in session:
        user_id = session["user"]
        delete_token_for_user(user_id)  # Delete token for the current user
        session.pop("user", None)
        session.pop("remember_me", None)  # Clear the remember me session variable
        response = make_response(redirect(url_for("signin")))
        response.delete_cookie("remember_me_token")
        return response
    return redirect(url_for("signin"))


@app.before_request
def before_request():
    g.user = None
    if "user" in session:
        g.user = session["user"]
    elif "remember_me_token" in request.cookies:
        token = request.cookies.get("remember_me_token")
        user_id = get_user_by_token(token)
        if user_id:
            session["user"] = user_id
            g.user = user_id
    else:
        session.pop("user", None)


@app.route("/<string:page_name>")
def page(page_name="/"):
    try:
        return render_template(page_name + ".html")
    except:
        return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
