import sqlite3
from sqlite3 import Error
from werkzeug.security import generate_password_hash

database = r"./database.db"


sql_create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

sql_create_posts_table = """
CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
"""

sql_create_comments_table = """
CREATE TABLE IF NOT EXISTS comments (
    comment_id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts (post_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
"""

sql_create_likes_table = """
CREATE TABLE IF NOT EXISTS likes (
    like_id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts (post_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
"""

sql_create_followers_table = """
CREATE TABLE IF NOT EXISTS followers (
    user_id INTEGER NOT NULL,
    follower_user_id INTEGER NOT NULL,
    PRIMARY KEY (user_id, follower_user_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (follower_user_id) REFERENCES users (user_id)
);
"""


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(f"Error: {e}")
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    """
    try:
        cur = conn.cursor()
        cur.execute(create_table_sql)
        cur.close()
    except Error as e:
        print(f"Error: {e}")


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
    """
    Returns a list of all existing usernames
    """
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
        sql = "SELECT username, password, role, date FROM users WHERE email = ?"
        cur.execute(sql, (email,))
        result = cur.fetchone()

        if result is None:
            print(f"No user found with username: {email}")
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

def init_users(conn):
    init = [
        ("admin", generate_password_hash("admin123"), "admin@example.com", "admin"),
        ("daniel", generate_password_hash("daniel123"), "daniel@example.com", "admin"),
        ("erik", generate_password_hash("erik123"), "erik@example.com", "admin"),
        ("alice", generate_password_hash("alice123"), "alice@example.com", "user"),
        ("bob", generate_password_hash("bob123"), "bob@example.com", "user"),
        ("charlie", generate_password_hash("charlie123"), "charlie@example.com", "user"),
        ("dave", generate_password_hash("dave123"), "dave@example.com", "user"),
        ("eve", generate_password_hash("eve123"), "eve@example.com", "user"),
        ("frank", generate_password_hash("frank123"), "frank@example.com", "user"),
        ("grace", generate_password_hash("grace123"), "grace@example.com", "user"),
        ]
    existing_users = select_users(conn)
    for user in init:
        if user[0] not in existing_users:
            add_user(conn, user[0], user[1], user[2], user[3])


def setup():
    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_posts_table)
        create_table(conn, sql_create_comments_table)
        create_table(conn, sql_create_likes_table)
        create_table(conn, sql_create_followers_table)
        init_users(conn)
        conn.close()


if __name__ == '__main__':
    setup()