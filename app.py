import os
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

# Configure application
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# Implementing CORS
CORS(app)

@app.errorhandler(429)
def quota_exceeded_error(error):
    return render_template("quota_exceeded.html"), 429  # Render the page properly

from controller import *