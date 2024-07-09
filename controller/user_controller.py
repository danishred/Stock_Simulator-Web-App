import re
import random
from app import app
from decimal import Decimal
from dotenv import load_dotenv # Allows loading environment variables
from model.user_model import user_model
from helpers import apology, login_required, lookup, usd
from werkzeug.security import check_password_hash, generate_password_hash
from flask import json, flash, redirect, render_template, request, session


# obj for user_model
obj = user_model()

# Loading environment variables
load_dotenv()

# Load JSON content to a dictionary
with open("output_file.json") as file:
    data = json.load(file)

# Custom filter
app.jinja_env.filters["usd"] = usd

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""

    # Create all tables if not exists
    obj.create_table()

    # Fetching user cash of current session 
    usrcsh = obj.fetch_total_cash(session["user_id"])

    # Fetching name of current user
    currentuser = obj.fetch_user_name(session["user_id"])

    # Conditions for GET
    if request.method == "GET":

        # Fetching liveindex in list
        liveindexes = obj.fetch_liveindex(session["user_id"])

        # Storing latest data in list
        currentlooks = []
        for liveindex in liveindexes:
            currentlooks.append(lookup(liveindex["symbol"]))

        # Updating latest for liveindex
        for currentlook in currentlooks:
            obj.update_liveindex(currentlook["price"], session["user_id"], currentlook["symbol"])

        # Calculation total cash possession in the form of shares
        ttlshr = 0
        for liveindex in liveindexes:
            ttlshr += liveindex["liveprice"] * liveindex["liveshares"]

        # Rendering page and passing variables
        return render_template("index.html", liveindexes=liveindexes,
                               usrcsh=usrcsh, ttlshr=ttlshr, currentuser=currentuser)


    # Conditions for POST
    if request.method == "POST":

        # Fetching user information
        addcash = request.form.get("cash")

        if addcash.isnumeric() != True:
            return apology("please enter cash amount")

        # Adding more cash to account
        usrcsh = Decimal(usrcsh)  # Ensure usrcsh is a Decimal
        addcash_decimal = Decimal(addcash)  # Convert addcash to Decimal
        obj.update_user_cash(usrcsh + addcash_decimal, session["user_id"])

        # Redirecting
        flash('Cash Added !!!')
        return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Fetching cash value of user
    usrcsh = obj.fetch_total_cash(session["user_id"])

    # Fetching name of current user
    currentuser = obj.fetch_user_name(session["user_id"])

    # Conditions for POST
    if request.method == "POST":

        # Fetching user input
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Performing checks
        if not symbol:
            return apology("Enter stock symbol")

        if not shares:
            return apology("No input in no. of shares")

        if not shares.isnumeric():
            return apology("Shares is not numeric")

        if int(shares) < 0:
            return apology("Shares can't be negative")

        # Fetching latest details of current stock
        buystks = lookup(symbol.upper())
        if buystks == None:
            return apology("invalid symbol")

        if usrcsh < float(shares)*(buystks["price"]):
            return apology("insufficient funds")


        # Fetching shares bought before
        prevshr = obj.fetching_shares_bought(session["user_id"], symbol.upper())

        # Total previously bought share of the stock
        liveshares = prevshr

        # Inserting stock details if bought first time
        if liveshares == 0:
            obj.insert_liveindex(session["user_id"], symbol.upper(), shares, buystks["price"])

        # Updating history table for the current share bought
        obj.insert_history(session["user_id"], symbol.upper(), shares, buystks["price"])

        # Updating total shares bought
        liveshares += int(shares)

        # Update the liveindex with the new total shares
        obj.update_liveindex_shares(liveshares, session["user_id"], symbol.upper())

        # Debiting cash
        obj.update_user_cash(usrcsh - Decimal(shares) * Decimal(buystks["price"]), session["user_id"])

        flash('Share/s Bought Successfully !!!')
        return redirect("/")

    # Condition for GET
    if request.method == "GET":
        return render_template("buy.html", usrcsh=usrcsh, currentuser=currentuser)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Fetching name of current user
    currentuser = obj.fetch_user_name(session["user_id"])

    # Fetching and passing history table
    histories = obj.fetch_history(session["user_id"])
    return render_template("history.html", histories=histories, currentuser=currentuser)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        user = obj.fetch_user_by_username(request.form.get("username"))

        # Ensure username exists and password is correct
        if len(user) != 1 or not check_password_hash(user[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # Fetching name of current user
    currentuser = obj.fetch_user_name(session["user_id"])

    # Condition for GET
    if request.method == "GET":
        return render_template("quote.html", currentuser=currentuser)

    # Condition for POST
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # Performing checks
        if not symbol:
            return apology("provide input")

        lookstks = lookup(symbol.upper())
        if lookstks is None:
            return apology("invalid symbol provided")

        return render_template("quoted.html", lookstks=lookstks, currentuser=currentuser)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Conditions for POST
    if request.method == "POST":

        # Fetching info provided by user
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Performing checks
        if obj.fetch_user_by_username(email):
            return apology("username already exists")

        if not email:
            return apology("must provide email")

        if not password:
            return apology("must provide password")

        if not confirmation:
            return apology("must provide confirmation password")

        if password != confirmation:
            return apology("Passwords do not match (case sensitive)")

        # Normalize Email    
        email = email.lower()# Email validation

        # Email validation
        if len(email) < 3:
            return apology("email must be at least 3 characters long")

        if " " in email:
            return apology("whitespace not allowed")
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):  
            return apology("Please enter a valid E-mail")  

        # Password Validation
        if " " in password:
            return apology("whitespace not allowed")

        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
            
        if not re.match(pattern, password):
            return apology("The password should contain at least one lowercase letter, one uppercase letter, one digit, and one special character")

        # Inserting user details in table
        obj.insert_user(email, generate_password_hash(password))
       
        flash('User Registered Successfully !!!')
        return redirect("/")
    
    # Conditions for GET
    if request.method == "GET":
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Fetching name of current user
    currentuser = obj.fetch_user_name(session["user_id"])

    # Conditions for POST
    if request.method == "POST":

        # Fetching user inputs
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Performing checks
        if not symbol:
            return apology("No symbol selected")
        if not shares:
            return apology("missing shares")

        # Total shares of current stock
        sharescnt = obj.fetch_user_shares(session["user_id"], symbol.upper())
        if not sharescnt:
            return apology("you don't own any shares of this stock")

        if int(shares) > int(sharescnt):
            return apology("you don't possess that many shares")

        # Updating no. of shares possessed after selling
        sellstks = lookup(symbol.upper())
        obj.update_liveindex_shares(int(sharescnt) - int(shares), session["user_id"], symbol.upper())

        # Updating history table for the current share sold
        obj.insert_history(session["user_id"], symbol.upper(), -int(shares), sellstks["price"])

        # Crediting cash in users account
        usrcsh = obj.fetch_total_cash(session["user_id"])
        sell_price = Decimal(sellstks["price"])
        obj.update_user_cash(usrcsh + Decimal(shares) * sell_price, session["user_id"])

        # Deleting shares that have 0 stocks
        obj.delete_zero_shares()

        # Redirecting to homepage
        flash('Share/s Sold Successfully !!!')
        return redirect("/")

    # Conditions for GET
    if request.method == "GET":

        # Fetching and passing stock symbols possessed by user
        symbols = obj.fetch_user_symbols(session["user_id"])
        print(symbols)
        return render_template("sell.html", symbols=symbols, currentuser=currentuser)


@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    """Add your notes"""

    # Fetching name of current user
    currentuser = obj.fetch_user_name(session["user_id"])

    if request.method == "GET":

        notesdicts = obj.fetch_notes(session["user_id"])

        return render_template("notes.html", notesdicts=notesdicts, currentuser=currentuser)

    if request.method == "POST":

        notes = request.form.get("notes")

        obj.insert_note(session["user_id"], notes)

        flash('Note Added !!!')
        return redirect("/notes")


@app.route("/delnotes", methods=["POST"])
@login_required
def delnotes():
    serial = request.form.get("serial")
    obj.delete_note_by_serial(serial)
    flash('Note Deleted !!!')
    return redirect("/notes")


@app.route("/motivation", methods=["GET"])
@login_required
def motivation():

    # Fetching name of current user
    currentuser = obj.fetch_user_name(session["user_id"])

    """Show user motivational quotes"""
    random_num = random.choice(data)
    dict = random_num
    return render_template("motivation.html", dict=dict, currentuser=currentuser)


@app.route("/reset", methods=["POST"])
@login_required
def reset():
    """Reset all current user data"""

    obj.reset_user_data(session["user_id"])

    flash('Reset Successful !!!')
    return redirect("/")


@app.route("/changepass", methods=["POST"])
@login_required
def changepass():

    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Password Validation
    if not password:
        return apology("must provide password")

    if not confirmation:
        return apology("must provide confirmation password")

    if password != confirmation:
        return apology("Passwords do not match (case sensitive)")
    
    if " " in password:
        return apology("whitespace not allowed")

    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        
    if not re.match(pattern, password):
        return apology("The password should contain at least one lowercase letter, one uppercase letter, one digit, and one special character")

    # Updating user password
    obj.update_user_password(generate_password_hash(password), session["user_id"])

    session.clear()

    return redirect("/")