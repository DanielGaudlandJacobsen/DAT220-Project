from flask import Flask, render_template, g, request, flash, session, redirect, url_for
from setup_db import database, create_connection
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = 'secret_key'


def get_db():
    if not hasattr(g, "_database"):
        print("Creating new database connection")
        g._database = create_connection(database)
    return g._database


@app.teardown_appcontext
def teardown_db(error):
    db = getattr(g, '_database', None)
    if db is not None:
        print("Closing database connection")
        db.close()


@app.route("/")
def index():
    return render_template("index.html")



if __name__ == "__main__":
    app.run(debug=True)