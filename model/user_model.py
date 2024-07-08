import re # For regular expression
import os # For accessing environment variable
import psycopg2 # Driver to interact with PSQL
import psycopg2.extras # Allows referencing as dictionary
from dotenv import load_dotenv # Allows loading environment variables
from flask import jsonify, render_template 
from werkzeug.security import generate_password_hash, check_password_hash   

load_dotenv()

class user_model():

    # Fetching cash in list and storing in variable
    def fetch_user_cash(self, )
    cash = db.execute("SELECT cash FROM users WHERE id = ?",
                      session["user_id"])
    usrcsh = float(cash[0]["cash"])

    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]