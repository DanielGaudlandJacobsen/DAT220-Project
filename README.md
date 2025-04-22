# Problem Analysis
Creating a social media platform involves managing how users interact with each other and the content they share, such as posts, likes, comments, and follows. The main challenges in designing the database are making sure the data is accurate, avoiding unnecessary repetition, and ensuring that actions like searching and user interactions can be done efficiently. This project will include CRUD functionality (Create, Read, Update, Delete), SQL queries with at least five tables, and search/filter options, all developed using while Flask.

## Key entities and relationships for the Database:
### User table
> A registered individual on the platform, can follow other users, post content, like posts, and comment on posts.
- `user_id (PK)`
- `username`
- `email`
- `password`
- `role`
- `date`
### Follower table
> The relationship between a user that follow another user, can follow multiple users.
- `user_id (PK, FK)`: User being followed 
- `follower_user_id (PK, FK)`: User who is following
### Post table
> Content shared by users on the platform, can receive comments and likes on it.
- `post_id (PK)`
- `user_id (FK)`
- `content`
- `date`
### Comment table
> User reply to posts. Each comment is linked to a post and a user.
- `comment_id (PK)`
- `post_id (FK)`
- `user_id (FK)`
- `content`
- `date`
### Like table
> A record of a user liking a post. Each like is linked to a specific post and a user.
- `like_id (PK)`
- `user_id (FK)`
- `post_id (FK)`

## ER diagram
![image](https://github.com/user-attachments/assets/a6544965-4ee5-48e0-92ba-5266f7d24eae)



