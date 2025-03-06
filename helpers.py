import requests
import os
from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up live quote for symbol using Alpha Vantage API."""
    # You'll need to get a free API key from https://www.alphavantage.co/support/#api-key
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Error: Alpha Vantage API key not found. Set it as an environment variable.")
        return None
        
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol.upper()}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP error responses
        data = response.json()
        
        # Check if we got valid data
        if "Global Quote" not in data or not data["Global Quote"]:
            print(f"Error: No data found for symbol {symbol}")
            return None
        
            # Check if we've exceeded the API limit
        if "Note" in data and "call frequency" in data["Note"]:
            print("Error: Daily API call limit exceeded")
            # Perhaps implement a fallback method here
            return None
                
        quote_data = data["Global Quote"]
        return {
            "name": symbol.upper(),  # Alpha Vantage Global Quote doesn't include company name
            "price": float(quote_data["05. price"]), 
            "symbol": symbol.upper()
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
