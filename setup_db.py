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
    

def select_posts(conn, username):
    try:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        sql = """
        SELECT p.post_id, p.title, p.content,
        p.date AS post_date,
        post_user.username AS post_author,
        c.comment_id,
        c.content AS comment_content,
        c.date AS comment_date,
        comment_user.username AS comment_author,
        (
            SELECT COUNT(*)
            FROM likes l
            WHERE l.post_id = p.post_id
        ) AS like_count
        FROM posts p
        JOIN users post_user ON p.user_id = post_user.user_id
        LEFT JOIN comments c ON p.post_id = c.post_id
        LEFT JOIN users comment_user ON c.user_id = comment_user.user_id
        WHERE p.user_id = (SELECT user_id FROM users WHERE username = ?)
        OR p.user_id IN (
            SELECT user_id
            FROM followers
            WHERE follower_user_id = (SELECT user_id FROM users WHERE username = ?)
        )
        ORDER BY p.date DESC, c.date ASC;
        """

        cur.execute(sql, (username, username))
        result = cur.fetchall()
        return result

    except Error as e:
        print(f"Error: {e}")
        return None