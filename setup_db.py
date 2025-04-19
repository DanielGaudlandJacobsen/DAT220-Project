import sqlite3
from sqlite3 import Error

database = r"./database.db"


sql_create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username VARCHAR(15) UNIQUE NOT NULL,
    password VARCHAR(30) NOT NULL,
    email VARCHAR(40) UNIQUE NOT NULL,
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


def setup():
    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_users_table)
        create_table(conn, sql_create_posts_table)
        create_table(conn, sql_create_comments_table)
        create_table(conn, sql_create_likes_table)
        create_table(conn, sql_create_followers_table)
        conn.close()


if __name__ == '__main__':
    setup()