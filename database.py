import os
import mysql.connector as sqlc
from dotenv import load_dotenv

load_dotenv()


# COMMAND TO CONNECT THE DATABASE
connection = sqlc.connect(
    host=os.getenv("db_host"),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    db=os.getenv("db_name"),
)

# COMMAND TO CREATE A CURSOR
cursor = connection.cursor()

# COMMAND TO CREATE DATABASE (ALREADY EXECUTED IN THE MYSQL SHELL)
# mycursor.execute("CREATE DATABASE freedb_MacroTrack")

# COMMAND TO USE THE CREATED DATABASE
cursor.execute("USE freedb_MacroTrack")
