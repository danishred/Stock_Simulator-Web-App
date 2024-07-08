from app import app
from flask import json, jsonify, flash, redirect, render_template, request, session
# from model.user_model import user_model
from helpers import apology, login_required, lookup, usd
import re
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash

# Load JSON content to a dictionary
with open("output_file.json") as file:
    data = json.load(file)

# Custom filter
app.jinja_env.filters["usd"] = usd

db = SQL("sqlite:///stocks.db")

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

    # Fetching cash in list and storing in variable
    cash = db.execute("SELECT cash FROM users WHERE id = ?",
                      session["user_id"])
    usrcsh = float(cash[0]["cash"])

    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]

    # Conditions for GET
    if request.method == "GET":

        # Fetching liveindex in list
        liveindexes = db.execute(
            "select * from liveindex where id = ?", session["user_id"])

        # Storing latest data in list
        currentlooks = []
        for liveindex in liveindexes:
            currentlooks.append(lookup(liveindex["symbol"]))

        # Updating latest for liveindex
        for currentlook in currentlooks:
            db.execute("UPDATE liveindex SET liveprice = ?  WHERE id = ? AND symbol = ?",
                       currentlook["price"], session["user_id"], currentlook["symbol"])

        # Calculation total cash possesion in the form of shares
        ttlshr = 0
        for liveindex in liveindexes:
            ttlshr = ttlshr + (liveindex["liveprice"]*liveindex["liveshares"])

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
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   usrcsh + float(addcash), session["user_id"])

        # Redirecting
        flash('Cash Added !!!')
        return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Fetching cash value of user
    cash = db.execute("SELECT cash FROM users WHERE id = ?",
                      session["user_id"])
    usrcsh = float(cash[0]["cash"])

    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]

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

        if shares.isnumeric() != True:
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
        prevshr = db.execute("select sum(liveshares) from liveindex where id = ? AND\
                              symbol = ?", session["user_id"], symbol.upper())

        # Total previously bought share of the stock
        liveshares = prevshr[0]["sum(liveshares)"]

        # Inserting stock details if bought first time
        if liveshares == None:
            liveshares = 0
            db.execute("INSERT INTO liveindex(id, symbol, liveshares, liveprice) \
                    VALUES(?, ?, ?, ?)", session["user_id"], symbol.upper(),
                       shares, buystks["price"])

        # Updating history table for the current share bought
        db.execute(
            "INSERT INTO history(id, symbol, shares, price, date) \
            VALUES(?, ?, ?, ?, (SELECT DATETIME('now','localtime')))",
            session["user_id"], symbol.upper(), shares, buystks["price"])

        # Updating total shares bought
        liveshares += int(shares)
        db.execute("UPDATE liveindex SET liveshares = ? where id = ? and symbol = ?",
                   liveshares, session["user_id"], symbol.upper())

        # Debiting cash
        db.execute("UPDATE users SET cash = ?  WHERE id = ?",
                   usrcsh - float(shares)*(buystks["price"]), session["user_id"])

        flash('Share/s Bought Successfully !!!')
        return redirect("/")

    # Condition for GET
    if request.method == "GET":
        return render_template("buy.html", usrcsh=usrcsh, currentuser=currentuser)


@ app.route("/history")
@ login_required
def history():
    """Show history of transactions"""

    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]

    # Fetching and passing history table
    histories = db.execute(
        "SELECT * FROM history where id = ?", session["user_id"])
    return render_template("history.html", histories=histories, currentuser=currentuser)


@ app.route("/login", methods=["GET", "POST"])
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
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@ app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@ app.route("/quote", methods=["GET", "POST"])
@ login_required
def quote():
    """Get stock quote."""
    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]

    # Condtion for GET
    if request.method == "GET":
        return render_template("quote.html", currentuser=currentuser)

    # Condtion for POST
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # Performing checks
        if not symbol:
            return apology("provide input")

        lookstks = lookup(symbol.upper())
        if lookstks == None:
            return apology("invalid symbol provided")

        return render_template("quoted.html", lookstks=lookstks, currentuser=currentuser)


@ app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Conditions for POST
    if request.method == "POST":

        # Fetching info provided by user
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Performing checks
        user = db.execute("SELECT * from users WHERE username = ?",
                          request.form.get("username"))
        if len(user) == 1:
            return apology("username already exists")

        if not username:
            return apology("must provide username")

        if not password:
            return apology("must provide password")

        if not confirmation:
            return apology("must provide confirmation password")

        if password != confirmation:
            return apology("Passwords do not match (case sensitive)")

        # Inserting user details in table
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)",
                   username, generate_password_hash(password))

        return redirect("/")
    # Conditions for GET
    if request.method == "GET":
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]

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
        sharescnt = db.execute(
            "SELECT liveshares from liveindex WHERE id = ? AND symbol = ?",
            session["user_id"], symbol.upper())
        if not sharescnt:
            return apology("you don't own any shares of this stock")

        if int(shares) > int(sharescnt[0]["liveshares"]):
            return apology("you don't possess that many shares")

        # Updating no. of shares possesed after selling
        sellstks = lookup(symbol.upper())
        db.execute("UPDATE liveindex SET liveshares = ?  WHERE id = ? AND symbol = ?",
                   int(sharescnt[0]["liveshares"]) - int(shares), session["user_id"], symbol.upper())

        # Updating history table for the current share sold
        db.execute(
            "INSERT INTO history(id, symbol, shares, price, date) \
            VALUES(?, ?, ?, ?, (SELECT DATETIME('now','localtime')))",
            session["user_id"], symbol.upper(), -int(shares), sellstks["price"])

        # Crediting cash in users account
        cash = db.execute("SELECT cash FROM users WHERE id = ?",
                          session["user_id"])
        usrcsh = float(cash[0]["cash"])
        db.execute("UPDATE users SET cash = ?  WHERE id = ?",
                   usrcsh + float(shares)*(sellstks["price"]), session["user_id"])

        # Deleting shares that have 0 stocks
        db.execute("DELETE FROM liveindex WHERE liveshares = 0")

        # Redirectinf to homepage
        flash('Share/s Sold Successfully !!!')
        return redirect("/")

    # Condtions for GET
    if request.method == "GET":

        # fetching and passing stock symbols possessed by user
        symbols = db.execute(
            "SELECT * FROM liveindex WHERE id = ?", session["user_id"])
        return render_template("sell.html", symbols=symbols, currentuser=currentuser)


@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():
    """Add your notes"""

    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]

    if request.method == "GET":

        notesdicts = db.execute(
            "SELECT * FROM notes where id = ? ORDER BY serial DESC", session["user_id"])

        return render_template("notes.html", notesdicts=notesdicts, currentuser=currentuser)

    if request.method == "POST":

        notes = request.form.get("notes")

        db.execute("INSERT INTO notes(id, data, date) \
            VALUES(?, ?, (SELECT DATETIME('now','localtime')))",
                   session["user_id"], notes)

        notesdicts = db.execute("SELECT * FROM notes")

        flash('Note Added !!!')
        return redirect("/notes")


@app.route("/delnotes", methods=["POST"])
@login_required
def delnotes():
    serial = request.form.get("serial")
    db.execute("DELETE FROM notes WHERE serial = ?", serial)
    flash('Note Deleted !!!')
    return redirect("/notes")


@app.route("/motivation", methods=["GET"])
@login_required
def motivation():

    # Fetching name of current user
    currentuser = db.execute(
        "SELECT username FROM users WHERE id = ?", session["user_id"])
    currentuser = currentuser[0]["username"]

    """Show user motivational quotes"""
    random_num = random.choice(data)
    dict = random_num
    return render_template("motivation.html", dict=dict, currentuser=currentuser)


@app.route("/reset", methods=["POST"])
@login_required
def reset():
    """Reset all current user data"""

    db.execute("UPDATE users SET cash = 10000 WHERE id = ?",
               session["user_id"])
    db.execute("DELETE FROM history WHERE id = ?",
               session["user_id"])
    db.execute("DELETE FROM liveindex WHERE id = ?",
               session["user_id"])
    db.execute("DELETE FROM notes WHERE id = ?",
               session["user_id"])

    flash('Reset Successful !!!')
    return redirect("/")


@app.route("/changepass", methods=["POST"])
@login_required
def changepass():

    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    if not password:
        return apology("must provide password")

    if not confirmation:
        return apology("must provide confirmation password")

    if password != confirmation:
        return apology("Passwords do not match (case sensitive)")

     # Inserting user details in table
    db.execute("UPDATE users set hash = ? where id = ?",
               generate_password_hash(password), session["user_id"])

    session.clear()

    return redirect("/")