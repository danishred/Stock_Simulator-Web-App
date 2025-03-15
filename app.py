import os
from redis import Redis
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta
from flask_session import Session

load_dotenv()

# Configure application
app = Flask(__name__)

os.environ.get('KV_URL')

app.config["SESSION_PERMANENT"] = True  # Make the session permanent
app.config["SESSION_TYPE"] = "redis"  # Use Redis for session storage

redis_url = os.environ.get('KV_URL')

if redis_url.startswith('redis://'):
    redis_url = 'rediss://' + redis_url[len('redis://'):]

app.config["SESSION_REDIS"] = Redis.from_url(redis_url)

# Initialize the session
Session(app)

# Implementing CORS
CORS(app)

@app.errorhandler(429)
def quota_exceeded_error(error):
    return render_template("quota_exceeded.html"), 429  # Render the page properly

from controller import *