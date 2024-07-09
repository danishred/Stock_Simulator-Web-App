import os
from redis import Redis
from flask import Flask 
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
app.config["SESSION_REDIS"] = Redis.from_url(os.environ.get('KV_URL')) # Configure redis connection

# Initialize the session
Session(app)

# Implementing CORS
CORS(app)

from controller import *