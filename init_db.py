from werkzeug.security import generate_password_hash
from setup_db import database, create_connection


conn = create_connection(database)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

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
    FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE,,
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
"""

sql_create_likes_table = """
CREATE TABLE IF NOT EXISTS likes (
    like_id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE,,
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

cursor.execute(sql_create_users_table)
cursor.execute(sql_create_posts_table)
cursor.execute(sql_create_comments_table)
cursor.execute(sql_create_likes_table)
cursor.execute(sql_create_followers_table)

users = [
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
cursor.executemany("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", users)

posts = [
    (1, 'Hello World', 'This is my first post!'),
    (2, 'My Thoughts', 'Just thinking out loud.'),
    (3, 'Interesting Facts', 'Did you know...'),
    (4, 'Food Diary', 'Had an amazing pizza today!'),
    (5, 'Vacation', 'Photos coming soon.'),
    (6, 'Tech Talk', 'Python is awesome.'),
    (7, 'Book Review', 'Loved the latest novel.'),
    (8, 'Workout Routine', 'Push-ups and squats!'),
    (9, 'Announcement', 'Launching something new.'),
    (10, 'Daily Life', 'Just another day.'),
    (1, 'Second Post', 'Back again with more.')
]
cursor.executemany("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", posts)

comments = [
    (1, 2, 'Nice one!'),
    (1, 3, 'Welcome!'),
    (2, 4, 'Interesting thoughts.'),
    (3, 5, 'Tell me more!'),
    (4, 6, 'Yummy!'),
    (5, 7, 'Looking forward to it.'),
    (6, 8, 'Totally agree.'),
    (7, 9, 'I’ll check it out.'),
    (8, 10, 'Respect!'),
    (9, 1, 'Cool.'),
    (10, 2, 'Keep sharing!')
]
cursor.executemany("INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)", comments)

likes = [
    (1, 2),
    (1, 3),
    (2, 1),
    (2, 4),
    (3, 5),
    (3, 6),
    (4, 7),
    (5, 8),
    (6, 9),
    (7, 10),
    (8, 1),
    (9, 2),
    (10, 3),
    (11, 4)
]
cursor.executemany("INSERT INTO likes (post_id, user_id) VALUES (?, ?)", likes)

followers = [
    (1, 2),
    (1, 3),
    (2, 1),
    (2, 4),
    (3, 5),
    (4, 1),
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 9),
    (9, 10),
    (10, 1),
    (3, 1),
    (4, 2),
    (5, 3),
    (6, 4)
]
cursor.executemany("INSERT INTO followers (user_id, follower_user_id) VALUES (?, ?)", followers)

conn.commit()
conn.close()

print("Test data inserted successfully.")