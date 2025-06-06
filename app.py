from flask import Flask, render_template, g, request, flash, session, redirect, url_for, abort
from setup_db import database, create_connection, add_user, select_users, select_user, get_stats, select_posts, select_post_by_id, select_comments_by_post_id, add_post, add_comment, update_post, update_comment, select_comment, get_user_id, already_following, follow_user, unfollow_user, email_exists
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
    if session.get("username"):
        return redirect(url_for("feed"))
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
        elif email_exists(db, email):
            flash("Email is already registered.", category="error")
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
        session["user_id"] = user["user_id"]
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
    session.pop("user_id")
    session.pop("email")
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
    sort = request.args.get("sort", "date")

    posts = select_posts(db, username, sort)
    return render_template('feed.html', posts=posts)


@app.route("/like_post", methods=["POST"])
def like_post():
    user_id = session.get("user_id")
    print(user_id)
    post_id = request.form.get("post_id")
    db = get_db()
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    cur.execute("SELECT post_id FROM posts WHERE post_id = ?", (post_id,))
    post = cur.fetchone()

    if not post:
        abort(404)
    
    cur.execute("SELECT * FROM likes WHERE post_id = ? AND user_id = ?", (post_id, user_id))
    like = cur.fetchone()

    if not like:
        cur.execute("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", (post_id, user_id))
        flash("Post liked successfully.", "success")
    else:
        cur.execute("DELETE FROM likes WHERE post_id = ? AND user_id = ?", (post_id, user_id))
        flash("Post unliked successfully.", "success")
    db.commit()
    return redirect(request.referrer or url_for("feed"))


@app.route("/post/<int:post_id>/comment", methods=["POST"])
def comment_post(post_id):
    user_id = session.get("user_id")
    content = escape(request.form.get("content"))

    if content and len(content) <= 255:
        db = get_db()
        add_comment(db, post_id, user_id, content)
        flash("Comment created successfully.", "success")
    else: 
        flash("Text too long or missing.", "error")
    return redirect(url_for("post", post_id = post_id))


@app.route("/create_post", methods=["POST"])
def create_post():
    user_id = session.get("user_id")
    title = escape(request.form.get("title"))
    content = escape(request.form.get("content"))

    if (title and content) and (len(title) <= 30 and len(content) <= 255):
        db = get_db()
        add_post(db, user_id, title, content)
        flash("Post created successfully.", "success")
    else:
        flash("Title or text too long or missing.", "error")
    return redirect(url_for("feed"))


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
    sort = request.args.get("sort", "newest")

    post = select_post_by_id(db, post_id)
    if not post:
        abort(404)
    comments = select_comments_by_post_id(db, post_id, sort)
    return render_template("post.html", post=post, comments=comments)


@app.route("/edit_post/<int:post_id>", methods=["POST"])
def edit_post(post_id):
    content = escape(request.form.get("content"))

    if not content or len(content) > 255:
        flash("Post content id empty or too long.", "error")
        return redirect(url_for("post", post_id=post_id))
    
    db = get_db()
    update_post(db, post_id, content)
    flash("Post updated successfully.", "success")

    return redirect(url_for("post", post_id=post_id))


@app.route("/edit_comment/<int:comment_id>", methods=["POST"])
def edit_comment(comment_id):
    db = get_db()
    content = escape(request.form.get("content"))
    comment = select_comment(db, comment_id)
    post_id = comment["post_id"]

    if not content or len(content) > 255:
        flash("PoComment content is empty or too long.", "error")
        return redirect(url_for("post", post_id=post_id))
    
    update_comment(db, comment_id, content)

    flash("Comment updated successfully.", "success")
    return redirect(url_for("post", post_id=post_id))


@app.route("/follow_unfollow", methods=["POST"])
def follow_unfollow():
    db = get_db()

    target_username = escape(request.form.get("username", "").strip())
    action = request.form.get("action")

    if not target_username:
        flash("Username cannot be empty.", "error")
        return redirect(url_for("feed"))

    current_username = session.get("username")
    if not current_username or target_username == current_username:
        flash("You can't follow yourself.", "error")
        return redirect(url_for("feed"))

    target_user_id = get_user_id(db, target_username)
    current_user_id = get_user_id(db, current_username)

    if not target_user_id:
        flash("User not found.", "error")
        return redirect(url_for("feed"))

    if action == "follow":
        if already_following(db, current_user_id, target_user_id):
            flash("You're already following this user.", "info")
        else:
            follow_user(db, current_user_id, target_user_id)
            flash(f"You are now following {target_username}.", "success")

    elif action == "unfollow":
        if already_following(db, current_user_id, target_user_id):
            unfollow_user(db, current_user_id, target_user_id)
            flash(f"You unfollowed {target_username}.", "info")
        else:
            flash("You're not following this user.", "info")

    return redirect(url_for("feed"))


if __name__ == "__main__":
    app.run(debug=True)