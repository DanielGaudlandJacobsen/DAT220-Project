# DAT220-Project


## Problem Analysis
A social media platform requires managing user information, interactions, and content. Here are the key entities and their relationships:

User: A registered individual on the platform.
Attributes: user_id, username, email, password, bio, created_date
A user can follow other users, post content, like posts, and comment on posts.

Follower: The relationship between a user that follow another user.
Attributes: follower_id (foreign key), followee_id (foreign key)
A user can follow multiple users.

Post: Content shared by users on the platform.
Attributes: post_id, user_id (foreign key), content, created_date
Each post is created by a user and can receive comments and likes.

Comment: User reply to posts.
Attributes: comment_id, post_id (foreign key), user_id (foreign key), content, created_date
Each comment is linked to a post and a user.

Like: A record of a user liking a post.
Attributes: like_id, user_id (foreign key), post_id (foreign key)
Each like is linked to a specific post and a user.