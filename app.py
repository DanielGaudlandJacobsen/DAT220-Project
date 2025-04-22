from flask import Flask, render_template, g, request, flash, session, redirect, url_for
from setup_db import database, create_connection, add_user, select_users, select_user
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from email_validator import validate_email, EmailNotValidError

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


@app.route("/register", methods=["POST"])
def register():
    username = escape(request.form.get("username")).strip()
    password_1 = request.form.get("password1")
    password_2 = request.form.get("password2")
    email = escape(request.form.get("email")).strip()


    if email and len(email) < 51:
        try:
            email = request.form.get("email", "").strip()
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError:
            flash("Invalid email address.", category="error")
            return redirect(url_for("index"))

    if username and password_1 and password_2:
        db = get_db()
        users = select_users(db)

        if username in users:
            flash("Username already exists.", category="error")
        elif len(username) < 2:
            flash("Username must be greater than 1 character.", category="error")
        elif len(username) > 15:
            flash("Username must be 15 characters or shorter.", category="error")
        elif password_1 != password_2:
            flash("Passwords must match.", category="error")
        elif len(password_1) < 8:
            flash("Password must be 8 characters or greater.", category="error")
        elif len(password_1) > 255:
            flash("Password must be 255 characters or shorter.", category="error")
        else:
            pwd_hash = generate_password_hash(password_1)
            add_user(db, username, pwd_hash, email)
            session["username"] = username
            session["role"] = "user"
            flash("Account created!", category="success")

            return redirect(url_for("index"))
    else:
        flash("You must enter the required information", category="error")
    
    return redirect(url_for("index"))


def valid_login(email, password):
    db = get_db()
    user = select_user(db, email)

    if user and check_password_hash(user["password"], password):
        return True
    return False


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    if valid_login(email, password):
        db = get_db()
        user = select_user(db, email)
        session["username"] = email
        session["role"] = user["role"]
        flash("Logged in", category="success")
        return redirect(url_for("index"))
    else:
        flash("Invalid login", category="error")
        return redirect(url_for("index"))
    

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username")
    session.pop("role")
    flash("Logged out", category="success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)