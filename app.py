from flask import Flask, render_template, g, request, flash, session, redirect, url_for, abort
from setup_db import database, create_connection, add_user, select_users, select_user, get_stats, select_posts, select_post_by_id, select_comments_by_post_id
from werkzeug.security import generate_password_hash, check_password_hash
from markupsafe import escape
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
import sqlite3

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

            return redirect(url_for("feed"))
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
        session["username"] = user["username"]
        session["email"] = email
        session["role"] = user["role"]
        flash("Logged in", category="success")
        return redirect(url_for("feed"))
    else:
        flash("Invalid login", category="error")
        return redirect(url_for("index"))
    

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("username")
    session.pop("role")
    flash("Logged out", category="success")
    return redirect(url_for("index"))


@app.route("/profile/<username>")
def profile(username):
    db = get_db()
    user = get_stats(db, username)
    date = user["date"]
    date = datetime.fromisoformat(user["date"])
    if not user:
        abort(404)
    return render_template('profile.html', user=user, date=date)


@app.route("/feed")
def feed():
    db = get_db()
    username = session.get("username")
    
    posts = select_posts(db, username)
    #print(posts)

    return render_template('feed.html', posts=posts)


@app.route("/like_post", methods=["POST"])
def like_post():
    return


@app.route("/comment_post", methods=["POST"])
def comment_post():
    return


@app.route("/create_post", methods=["POST"])
def create_post():
    return


@app.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    db = get_db()
    db.row_factory = sqlite3.Row
    username = session.get("username")
    role = session.get("role")

    cur = db.cursor()
    cur.execute("SELECT post_id, user_id FROM posts WHERE post_id = ?", (post_id,))
    post = cur.fetchone()

    if not post:
        abort(404)

    cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id = cur.fetchone()["user_id"]

    if role == "admin" or post["user_id"] == user_id:
        cur.execute("DELETE FROM comments WHERE post_id = ?", (post_id,))
        cur.execute("DELETE FROM likes WHERE post_id = ?", (post_id,))
        cur.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        db.commit()
        flash("Post deleted successfully.", "success")
    else:
        flash("You don't have permission to delete this post.", "error")
    return redirect(url_for("feed"))


@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    db = get_db()
    db.row_factory = sqlite3.Row
    username = session.get("username")
    role = session.get("role")

    cur = db.cursor()
    cur.execute("SELECT comment_id, user_id FROM comments WHERE comment_id = ?", (comment_id,))
    comment = cur.fetchone()

    if not comment:
        abort(404)

    cur.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id = cur.fetchone()["user_id"]

    if role == "admin" or comment["user_id"] == user_id:
        cur.execute("DELETE FROM comments WHERE comment_id = ?", (comment_id,))
        db.commit()
        flash("Comment deleted successfully.", "success")
    else:
        flash("You don't have permission to delete this comment.", "error")

    return redirect(request.referrer or url_for("feed"))

@app.route("/post/<int:post_id>", methods=["GET"])
def post(post_id):
    db = get_db()
    post = select_post_by_id(db, post_id)
    if not post:
        abort(404)
    comments = select_comments_by_post_id(db, post_id)
    return render_template('post.html', post=post, comments=comments)

if __name__ == "__main__":
    app.run(debug=True)