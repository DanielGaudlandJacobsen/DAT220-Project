import sqlite3
from sqlite3 import Error


database = r"./database.db"


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"Error: {e}")
    return conn


def add_user(conn, username, password_hash, email, role="user"):
    sql = ''' INSERT INTO users(username, password, email, role, date)
              VALUES(?,?,?,?,datetime('now','localtime'));
              '''
    try:
        cur = conn.cursor()
        cur.execute(sql, (username, password_hash, email, role))
        conn.commit()
        cur.close()
    except Error as e:
        print(f"Error: {e}")


def select_users(conn):
    try:
        cur = conn.cursor()
        cur.execute("SELECT username FROM users")
        users = []
        for username in cur:
            users.append(username[0])
        cur.close()
        return users
    
    except Error as e:
        print(f"Error: {e}")
        return []
    

def select_user(conn, email):
    try:
        cur = conn.cursor()
        sql = "SELECT * FROM users WHERE email = ?"
        cur.execute(sql, (email,))
        result = cur.fetchone()

        if result is None:
            print(f"No user found with email: {email}")
            return None
        
        user = {"email": email,
                "user_id": result[0],
                "username": result[1],
                "password": result[2],
                "role": result[4],
                "date": result[5]}
        cur.close()
        return user
    
    except Error as e:
        print(f"Error: {e}")
        return None
    

def get_stats(conn, username):
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = """
        SELECT u.username, u.email, u.date,
        COUNT(DISTINCT p.post_id) AS total_posts,
        COUNT(DISTINCT f.follower_user_id) AS total_followers,
        COUNT(DISTINCT l.like_id) AS total_likes
        FROM users u
        LEFT JOIN posts p ON u.user_id = p.user_id
        LEFT JOIN followers f ON u.user_id = f.user_id
        LEFT JOIN 
        likes l ON u.user_id = l.user_id
        WHERE u.username = ?
        GROUP BY u.user_id;
        """
        cur.execute(sql, (username,))
        result = cur.fetchone()

        if result is None:
            print(f"No user found with email: {username}")
            return None
        
        cur.close()
        return result

    except Error as e:
        print(f"Error: {e}")
        return None
    

def select_posts(conn, username, sort="date"):
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if sort == "likes":
            order_by = "like_count DESC"
        elif sort == "date_asc":
            order_by = "p.date ASC"
        else:
            order_by = "p.date DESC"

        sql = f"""
        SELECT p.post_id, u.username, p.title, p.content, p.date,
        COUNT(l.like_id) AS like_count
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        LEFT JOIN likes l ON p.post_id = l.post_id
        WHERE 
        p.user_id = (SELECT user_id FROM users WHERE username = ?)
        OR p.user_id IN (
            SELECT user_id
            FROM followers
            WHERE follower_user_id = (SELECT user_id FROM users WHERE username = ?)
        )
        GROUP BY p.post_id
        ORDER BY {order_by};
        """

        cur.execute(sql, (username, username))
        result = cur.fetchall()
        return result

    except Error as e:
        print(f"Error: {e}")
        return None
    
    
def select_post_by_id(conn, post_id):
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = """
        SELECT p.post_id, p.title, p.content,
        p.date AS post_date,
        u.username AS post_author,
        (
            SELECT COUNT(*)
            FROM likes l
            WHERE l.post_id = p.post_id
        ) AS like_count
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        WHERE p.post_id = ?
        """
        cur.execute(sql, (post_id,))
        return cur.fetchone()
    except Exception as e:
        print("Error fetching post by ID:", e)
        return None
    

def select_comments_by_post_id(conn, post_id, sort="newest"):
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        if sort == "oldest":
            order_by = "c.date ASC"
        else:
            order_by = "c.date DESC"

        sql = f"""
        SELECT c.comment_id, c.content, c.date AS comment_date, u.username AS comment_author, c.post_id
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.post_id = ?
        ORDER BY {order_by}
        """
        cur.execute(sql, (post_id,))
        return cur.fetchall()
    except Exception as e:
        print("Error fetching comments:", e)
        return []
    

def select_comment(conn, comment_id):
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = "SELECT * FROM comments WHERE comment_id = ?;"
        cur.execute(sql, (comment_id,))
        return cur.fetchone()

    except Error as e:
        print(f"Error: {e}")
        return None
    

def add_post(conn, user_id, title, content):
    try:
        cur = conn.cursor()
        sql = "INSERT INTO posts (user_id, title, content) VALUES (?,?,?);"
        cur.execute(sql, (user_id, title, content))
        conn.commit()
        conn.close()

    except Error as e:
        print(f"Error: {e}")
        return None
    

def add_comment(conn, post_id, user_id, content):
    try:
        cur = conn.cursor()
        sql = "INSERT INTO comments (post_id, user_id, content) VALUES (?,?,?);"
        cur.execute(sql, (post_id, user_id, content))
        conn.commit()
        conn.close()

    except Error as e:
        print(f"Error: {e}")
        return None
    

def update_post(conn, post_id, content):
    try:
        cur = conn.cursor()
        sql = "UPDATE posts SET content = ? WHERE post_id = ?;"
        cur.execute(sql, (content, post_id))
        conn.commit()
        conn.close()

    except Error as e:
        print(f"Error: {e}")
        return None
    

def update_comment(conn, comment_id, content):
    try:
        cur = conn.cursor()
        sql = "UPDATE comments SET content = ? WHERE comment_id = ?;"
        cur.execute(sql, (content, comment_id))
        conn.commit()
        conn.close()

    except Error as e:
        print(f"Error: {e}")
        return None
    

def get_user_id(conn, username):
    cur = conn.cursor()
    sql = "SELECT user_id FROM users WHERE username = ?"
    cur.execute(sql, (username,))
    result = cur.fetchone()
    if result:
        return result[0]
    else:
        return None


def already_following(conn, follower_id, user_id):
    cur = conn.cursor()
    sql = "SELECT 1 FROM followers WHERE user_id = ? AND follower_user_id = ?"
    cur.execute(sql, (user_id, follower_id))
    result = cur.fetchone()
    return result is not None


def follow_user(conn, follower_id, user_id):
    try:
        cur = conn.cursor()
        sql = "INSERT INTO followers (user_id, follower_user_id) VALUES (?, ?)"
        cur.execute(sql, (user_id, follower_id))
        conn.commit()
        conn.close()

    except Error as e:
        print(f"Error: {e}")
        return None


def unfollow_user(conn, follower_id, user_id):
    try:
        cur = conn.cursor()
        sql = "DELETE FROM followers WHERE user_id = ? AND follower_user_id = ?"
        cur.execute(sql, (user_id, follower_id))
        conn.commit()
        conn.close()

    except Error as e:
        print(f"Error: {e}")
        return None