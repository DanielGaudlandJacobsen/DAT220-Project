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