from flask import render_template, request, redirect, url_for
from setup_db import database, create_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret_key" 