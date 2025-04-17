# DAT220-Project


## Problem Analysis
A social media platform requires managing user information, interactions, and content. Here are the key entities and their relationships:
<br/>
User: A registered individual on the platform.<br/>
Attributes: user_id, username, email, password, bio, created_date<br/>
A user can follow other users, post content, like posts, and comment on posts.<br/>
<br/>
Follower: The relationship between a user that follow another user.<br/>
Attributes: follower_id (foreign key), followee_id (foreign key)<br/>
A user can follow multiple users.<br/>
<br/>
Post: Content shared by users on the platform.<br/>
Attributes: post_id, user_id (foreign key), content, created_date<br/>
Each post is created by a user and can receive comments and likes.<br/>
<br/>
Comment: User reply to posts.<br/>
Attributes: comment_id, post_id (foreign key), user_id (foreign key), content, created_date<br/>
Each comment is linked to a post and a user.<br/>
<br/>
Like: A record of a user liking a post.<br/>
Attributes: like_id, user_id (foreign key), post_id (foreign key)<br/>
Each like is linked to a specific post and a user.<br/>
