import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_cors import CORS
from redis import Redis
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# Configure application
app = Flask(__name__)

redis_url = os.environ.get('KV_URL')

app.config["SESSION_PERMANENT"] = True  # Make the session permanent
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)  # Set session lifetime to 7 days
app.config["SESSION_TYPE"] = "redis"  # Use Redis for session storage
app.config["SESSION_REDIS"] = Redis.from_url(redis_url) # Configure redis connection

# Initialize the session
Session(app)

# Implementing CORS
CORS(app)

from controller import *