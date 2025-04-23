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
                "username": result[0],
                "password": result[1],
                "role": result[2],
                "date": result[3]}
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