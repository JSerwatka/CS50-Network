# CS50 - Network project
## Table of contents
- [Introduction](#introduction)
  * [Description and requirements](#description-and-requirements)
  * [Versions](#versions)
  * [Installation](#installation)
  * [Preview](#preview)
    + [Edit your profile](#edit-your-profile)
    + [Add posts](#add-posts)
    + [Add comments](#add-comments)
    + [Add likes](#add-likes)
    + [Edit a comment or a post](#edit-a-comment-or-a-post)
    + [Delete a comment or a post](#delete-a-comment-or-a-post)
    + [Follow](#follow)
    + [View profile](#view-profile)
    + [Change language](#change-language)
- [Implementation](#implementation)
  * [Models](#models)
    + [User Profile](#user-profile)
    + [Post](#post)
    + [Comment](#comment)
    + [Like](#like)
    + [Following](#following)
  * [Views](#views)
    + [index](#index)
    + [post_comment](#post-comment)
    + [user_profile](#user-profile)
    + [edit_profile](#edit-profile)
    + [like](#like)
    + [following](#following)
    + [follow_unfollow](#follow-unfollow)
    + [login_view](#login-view)
    + [logout_view](#logout-view)
    + [register](#register)
  * [Tests](#tests)

# Introduction
## Description and requirements
Using Python, JavaScript, HTML, and CSS, complete the implementation of a social network that allows users to make posts, follow other users, and *like* posts. 

All requirements can be viewed here: https://cs50.harvard.edu/web/2020/projects/4/network/

Live version can be viewed here: https://cs-50-network.herokuapp.com/ (it might take a second to load 😉)

You must be registered to use options such as commenting, profile picture, following and so on.

## Versions
On this repository you can find 2 versions of this project:
1. **master** branch: allows file uploads for user profile 
2. **live-server-version** branch: uses img url istead of file upload to avoid using s3 buckets for demonstration

## Installation
To set up this project on your computer:
1. Clone the project
2. Install all necessary dependencies
    ```python
        pip install -r requirements.txt
    ```
3. Make a migration
    ```python
        python manage.py migrate
    ```
## Preview
### Edit your profile
![edit-profile](https://user-images.githubusercontent.com/33938646/126470604-4b529bbe-0cf9-4e37-a4ee-7178eda8b775.gif)

### Add posts
![add-posts](https://user-images.githubusercontent.com/33938646/126471690-cd28c3e7-0cb3-409c-8fd7-90cb4e9f50d3.gif)

### Add comments
![add-comments](https://user-images.githubusercontent.com/33938646/126470665-4ef5cfe0-f2f5-4a7b-bc17-41a89f1b5810.gif)

### Add likes
![add-likes](https://user-images.githubusercontent.com/33938646/126470715-009a35c2-f09f-427e-84bc-fcad87ef56db.gif)

### Edit a comment or a post
![edit](https://user-images.githubusercontent.com/33938646/126470738-93feef82-e59d-4a01-8f19-a1145fa46350.gif)

### Delete a comment or a post
![delete](https://user-images.githubusercontent.com/33938646/126470799-35f708a5-26c1-4ddc-a20f-3e081fd64fef.gif)

### Follow
![follow-user](https://user-images.githubusercontent.com/33938646/126470862-d60713b6-3824-4569-a037-19d43c431c09.gif)

### View profile
![view-profile](https://user-images.githubusercontent.com/33938646/126470897-1ecb0afa-c43e-43cc-96cc-253f2279636e.gif)

### Change language
![change-language](https://user-images.githubusercontent.com/33938646/126470922-94043366-6a4a-49ad-b29d-0b8757930ec1.gif)

# Implementation
## Models
### User Profile
Contains User Model extension with additional fields.

Fields:
* name - user's name
* date_of_birth - user's birth date
* about - additional info about the user
* country - user's birth place
* image - user's profile photo

### Post 
Contains all post info.

Fields:
* user - who posted the post
* content - post's inner text
* date - post's publication date

### Comment
Contains all comment info.

Fields:
* user - who posted the comment
* post - the post which is being commented
* content - comment's inner text
* date - comment's publication date

### Like 
Contains all like info.

Fields:
* user - who liked a post/comment
* post - the post which has been liked
* comment - the comment which has been liked
* emoji_type - the emoji used as a like, available emojis:
    1. like
    2. dislike
    3. smile
    4. heart
    5. thanks

### Following 
Contains all who follows who info.

Fields:
* user - user who is following
* user_followed - user who is being followed

## Views
### index
Here you can:
* View all posts
* Edit posts (if you are the post's creator; only for logged-in users)
* Delete posts (if you are the post's creator; only for logged-in users)
* Like them (only for logged-in users)
* Create a new post (only for logged-in users)
* View all comments (only for logged-in users)
* Create a comment (only for logged-in users)
* Delete a comment (if you are the comment's creator; only for logged-in users)
* Edit a comment (if you are the comment's creator; only for logged-in users)

### post_comment 
(only for logged-in users)

Controls saving of a new post/comment (only POST method allowed).

### user_profile
(only for logged-in users)

Here you can:
* View user's bio
* View all user's posts
* Edit posts (if you are the post's creator)
* Delete posts (if you are the post's creator)
* Like them 
* View all comments on user's posts
* Create a comment
* Delete a comment (if you are the comment's creator)
* Edit a comment (if you are the comment's creator)
* Follow the user (if you are not this user)
* Click on edit profile button (if you are this user)

### edit_profile
(only for logged-in users)

Here you can:
* Change your *name*
* Change your *birthdate*
* Change your *about info*
* Change your *profile picture*
* Change your *country*

### like
(only for logged-in users)

Controls all actions regarding liking:
* Add a new like
* Change a like's emoji

### following
(only for logged-in users)

Here you can:
* View all posts created by followed users
* Like them
* View all comments
* Create a comment
* Delete a comment (if you are the comment's creator)
* Edit a comment (if you are the comment's creator)

### follow_unfollow
(only for logged-in users)

Controls following/unfollowing users (only POST method allowed).

### login_view
Controls logging in.

### logout_view
Controls logging out.

### register
Controls registration.

## Tests
There are 4 main test cases:
* ModelsTestCase - checks database integrity
* FormsTestCase - makes sure that forms work correctly
* ViewsTestCase - makes sure that all views work correctly and give proper responses
* FrontEndTestCase - uses Selenium to simulate user interaction with every element on the page

Test requirements can be viewed in [test requirents.md](https://github.com/serwatka-w-proszku/CS50-Network/blob/master/test%20requirements.md)

---
Special thanks to Brian and the entire CS50 team for making learning easy, engaging, and free.
