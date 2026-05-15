import io
import base64
import requests
import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask import redirect, render_template, session, abort
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
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print(
            "Error: Alpha Vantage API key not found. Set it as an environment variable."
        )
        return None

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol.upper()}&apikey={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Check if API response contains a rate limit message
        if (
            isinstance(data, dict)
            and "Information" in data
            and "rate limit" in data["Information"].lower()
        ):
            abort(429)  # Abort and trigger the error handler

        quote_data = data["Global Quote"]
        return {
            "name": symbol.upper(),
            "price": float(quote_data["05. price"]),
            "symbol": symbol.upper(),
        }
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
    return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


def _fetch_news_articles(stock_ticker):
    """Fetch up to 100 news articles for the given ticker via NewsAPI."""
    api_key = os.environ.get("NEWS_API_KEY")
    if not api_key:
        return []
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={stock_ticker}&pageSize=100&apiKey={api_key}"
    )
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    news_data = response.json()
    return [
        article
        for article in news_data.get("articles", [])
        if article.get("description")
    ]


def _analyze_sentiment_vader(text):
    """Return 'positive', 'negative', or 'neutral' for a piece of text."""
    analyzer = SentimentIntensityAnalyzer()
    compound = analyzer.polarity_scores(text)["compound"]
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    return "neutral"


def _summarize_sentiments(sentiments):
    """Return percentage breakdown of positive/negative/neutral sentiments."""
    total = len(sentiments)
    if total == 0:
        return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
    return {
        "positive": round(sentiments.count("positive") / total * 100, 1),
        "negative": round(sentiments.count("negative") / total * 100, 1),
        "neutral": round(sentiments.count("neutral") / total * 100, 1),
    }


def get_sentiment_data(stock_ticker):
    """
    Fetch recent news for *stock_ticker*, run VADER sentiment analysis, and
    generate a pie chart.

    Returns a tuple (summary_dict, base64_png_str, articles_list) on success,
    or (None, None, []) if the News API is unreachable or returns no articles.
    Each item in articles_list is a dict with keys: title, description, url,
    source, published_at, sentiment.
    """
    try:
        raw_articles = _fetch_news_articles(stock_ticker)
        if not raw_articles:
            return None, None, []

        descriptions = [a["description"] for a in raw_articles]
        sentiments = [_analyze_sentiment_vader(d) for d in descriptions]
        summary = _summarize_sentiments(sentiments)

        articles = [
            {
                "title": a.get("title") or "No title",
                "description": a.get("description", ""),
                "url": a.get("url") or "#",
                "source": (a.get("source") or {}).get("name", "Unknown"),
                "published_at": (a.get("publishedAt") or "")[:10],
                "sentiment": sentiment,
            }
            for a, sentiment in zip(raw_articles, sentiments)
        ]

        df = pd.DataFrame(sentiments, columns=["Sentiment"])
        df = df["Sentiment"].value_counts().reset_index()
        df.columns = ["Sentiment", "Count"]

        colors = {"positive": "#4CAF50", "negative": "#F44336", "neutral": "#9E9E9E"}
        chart_colors = [colors.get(s, "#9E9E9E") for s in df["Sentiment"]]

        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(
            df["Count"],
            labels=df["Sentiment"].str.capitalize(),
            autopct="%1.1f%%",
            startangle=140,
            colors=chart_colors,
        )
        ax.set_title(
            f"Sentiment Distribution — {stock_ticker.upper()}'s Latest News",
            fontsize=13,
            pad=14,
        )
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120)
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close(fig)

        return summary, img_b64, articles

    except Exception:
        return None, None, []
