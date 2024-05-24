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
        return foods
    except Error as error:
        print("Error retrieving user foods:", error)
    finally:
        cursor.close()
        connection.close()


def get_food_data(food_id, user_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT f.Name, f.Proteins, f.Carbs, f.Fats, lf.Quantity FROM Food f JOIN LogFood lf ON f.FoodID = lf.FoodID JOIN Logs l ON lf.LogID = l.LogID WHERE l.UserID = %s AND f.FoodID = %s"

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
            "quantity": foods[4],
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


def update_food_data(
    food_name, proteins, carbohydrates, fats, quantity, food_id, user_id
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Update food item in Food table
        cursor.execute(
            "UPDATE Food SET Name = %s, Proteins = %s, Carbs = %s, Fats = %s WHERE UserID = %s AND FoodID = %s",
            (food_name, proteins, carbohydrates, fats, user_id, food_id),
        )

        # Update quantity in LogFood table
        cursor.execute(
            "UPDATE LogFood SET Quantity = %s WHERE FoodID = %s",
            (quantity, food_id),
        )

        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for("add"))

    except Error as e:
        print(f"Error updating food item: {e}")
        return "An error occurred while updating the food item", 500


def get_food_list(foods):
    food_list = {}
    for food in foods:
        food_data = f"{food[1]} ({food[2]}P, {food[3]}C, {food[4]}F) "
        food_list[food[0]] = food_data
    return food_list


# Routes
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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
            food_id = request.form.get("food-id")

            if food_id:
                update_food_data(
                    food_name, proteins, carbohydrates, fats, quantity, food_id, g.user
                )
            else:
                add_food_item_and_log(
                    g.user, food_name, proteins, carbohydrates, fats, quantity=quantity
                )

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


@app.route("/view/<int:log_ID>", methods=["GET", "POST"])
def view(log_ID):
    if g.user:
        if request.method == "POST":
            connection = get_db_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT f.*
                FROM LogFood lf
                JOIN Food f ON lf.FoodID = f.FoodID
                WHERE lf.LogID = %s AND f.UserID = %s
                """
                cursor.execute(query, (log_ID, g.user["UserID"]))
                foods = cursor.fetchall()
                cursor.close()
                connection.close()

                totals = {"protein": 0, "carbs": 0, "fat": 0, "calories": 0}
                for food in foods:
                    totals["protein"] += food["Proteins"]
                    totals["carbs"] += food["Carbs"]
                    totals["fat"] += food["Fats"]
                    totals["calories"] += food["Calories"]

                return render_template(
                    "view.html", foods=foods, user=g.user, log_ID=log_ID, totals=totals
                )
    return redirect(url_for("signin"))


@app.route("/create_log", methods=["POST"])
def create_log():
    if g.user:
        date = request.form.get("date")
        date = datetime.strptime(date, "%Y-%m-%d")
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "INSERT INTO Logs (UserID, Date) VALUES (%s, %s)"
            cursor.execute(query, (g.user["UserID"], date))
            connection.commit()

            query2 = "SELECT LogID FROM Logs WHERE UserID = %s AND Date = %s"
            cursor.execute(query2, (g.user["UserID"], date))
            result = cursor.fetchone()
            log_ID = result["LogID"]

        except Error as error:
            print("Error inserting Log:", error)
        finally:
            cursor.close()
            connection.close()
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
            cursor.execute(query, (log_ID, selected_food, quantity))
            connection.commit()
        except Error as error:
            print("Error adding food to log:", error)
        finally:
            cursor.close()
            connection.close()
        return redirect(url_for("view", log_ID=log_ID))
    return redirect(url_for("signin"))


@app.route("/remove_food_from_log/<int:log_ID>/<int:food_ID>", methods=["POST"])
def remove_food_from_log(log_ID, food_ID):
    if g.user:
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            query = "DELETE FROM LogFood WHERE LogID = %s AND FoodID = %s"
            cursor.execute(query, (log_ID, food_ID))
            connection.commit()
        except Error as error:
            print("Error removing food from log:", error)
        finally:
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
