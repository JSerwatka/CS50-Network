# Backend

## ~~Models~~
### ~~User~~
* ~~Create new user -> create new profile test~~

### ~~User Profile~~
* ~~new profile created -> create default image test~~

### ~~Like~~
* ~~multiple likes on one comment/post by the same user test~~


## Forms
### CreateUserProfileForm
* form z image > 5MB -> after cleaned_data -> Validation Error occurs?


## Views
### ~~login~~
* ~~GET~~
    * ~~status_code = 200~~
    * ~~check redirection to *index* for logged users~~

* ~~POST~~
    * ~~create user and try to login with its data~~
        * ~~check if user logged in~~
        * ~~test *next* redirection~~
    * ~~check invalid password behaviour -> context with correct error msg (force language setting first)~~

### ~~logout~~
* ~~status_code = 302~~
* ~~check user logged-in? -> logout -> user logged-out?~~
* ~~check redirection to index after logout~~

### ~~Register~~
* ~~GET~~
    * ~~status_code = 200~~
    * ~~check redirection to *index* for logged users~~
* ~~POST~~
    * ~~status_code = 200~~
    * ~~username, email, password empty test -> correct error msg~~
    * ~~password != confirmation test -> correct error msg~~
    * ~~user already exists~~
        1. ~~create user~~
        2. ~~try to create user with the same username~~
        3. ~~check if correct error msg~~
    * ~~correct register~~
        * ~~status_code = 302~~
        * ~~check redirection to *index*~~
        * ~~check if new user exists~~

### ~~index~~
* ~~status_code = 200~~
* ~~no posts -> 1 page available~~
* ~~11 posts -> 2 pages available~~

### ~~post-comment~~
* ~~login-required test~~
* ~~GET method not allowed test -> status_code = 405~~

* ~~POST~~
    * ~~post post/comment~~
        1. ~~post to post-comment/post v post-comment/comment~~
        2. ~~check if post exists~~
        3. ~~check if redirection url and status code is correct~~
    * ~~check comment on non-existing post status code (404)~~
* ~~PUT~~
    * ~~status_code = 201~~
    * ~~edit post/comment~~
        1. ~~send request with new data~~
        2. ~~check if post's or comment's content has changed~~
    * ~~incorrect post/comment id~~
        1. ~~send incorrect post's or comment's id~~
        2. ~~check if status_code is 404 and error msg is correct~~
* ~~DELETE~~
    * ~~status_code = 204~~
    * ~~delete post/comment~~
        1. ~~send request with post's or comment's id~~
        2. ~~check if post or comment got deleted~~
    * ~~incorrect id~~
        1. ~~send incorrect post's or comment's id~~
        2. ~~check if status_code is 404 and error msg is correct~~

### ~~user-profile~~
* ~~login-required test~~
* ~~status_code = 200~~
* ~~no posts ->  1 page available~~
* ~~11 posts ->  2 pages available~~
* ~~2 posts: by this user and another -> make sure only current is visible~~
* ~~follow by 5 users -> make sure that correct number is send as a context~~
* ~~follow 5 users -> make sure that correct number is send as a context~~

### ~~edit-profile~~
* ~~login-required test~~
* ~~GET~~
    * ~~status_code = 200~~
* ~~POST~~
    * ~~send form and check if user profile got updated~~
    * ~~status_code = 302~~
    * ~~check if redirection works correctly~~


### like
* ~~login-required test~~
* ~~GET~~
    * ~~check correct like get~~
        1. ~~create a post/comment~~
        2. ~~create a like ~~
        3. ~~send GET request~~
        4. ~~check if:~~
            * ~~status_code = 200~~
            * ~~*like* = *True*~~
            * ~~*emojiType* is correct~~
    * ~~send correct action but like doesn't exist~~
        * ~~check if status_code = 200~~
        * ~~check if *like* = *False*~~
    * ~~send unknown action~~
        * ~~check if status_code = 400~~
        * ~~check if error msg correct~~
    * ~~send correct action but post/comment doesn't exist~~
        * ~~check if status_code = 400~~
        * ~~check if error msg correct~~

* POST
    * send unknown action and correct id
        * check if status_code = 400
        * check if error msg correct
    * send correct action but post/comment doesn't exist
        * check if status_code = 400
        * check if error msg correct
    * check correct like creation
        * status_code = 201
        * like exists with proper emoji_type

* PUT
    * send unknown action and correct id
        * check if status_code = 400
        * check if error msg correct
    * send correct action but post/comment doesn't exist
        * check if status_code = 400
        * check if error msg correct
    * check correct like editing
        * status_code = 201
        * like exists with proper emoji_type
            1. creat a like with one emoji_type
            2. request for emoji_type change
            3. check if correct emoji type saved

### following
* login-required test
* status_code = 200
* no posts -> page_obj context = <page 1 of 1>
* 11 posts -> page_obj context = <page 1 of 2>
* 2 posts: by followed user and another -> make sure only followed is visible

### follow-unfollow
* login-required test
* status_code = ?
* follow user that doesn't exist -> 404 response
* follow user that doesn exist
    * check if new following exist
    * check if redirection is corrent
    * check status_code
* try to follow for the second time
    * check if new following deleted
    * check if redirection is corrent
    * check status_code

# Frontend

## post
**Setup**
1. create user 
2. populate user-profile with data
3. login user
4. create post
5. create several comments to this post

### index view
* create post with short text with form and send it -> check if exists
* check if posts in correct order (from newest to oldest)

#### index view, following, user_profile
* Posts
    * check post's content -> equal to post created

    * click on post's creator text test
        1. click on post's creator
        2. check if redirection to correct user profile works

    * edit post tests
        * post's creator = current user
            1. check if edit/delete panel is not hidden
            2. click on edit post
            3. change text
            4. check if post's content has changed
        * post's creator != current user
            1. check if edit/delete panel is hidden
        
    * delete post tests
        1. check if edit/delete panel is not hidden
        2. click on delete post
        3. check if post's content got deleted

    * long text post test
        1. create second post with long text
        2. check if short text post's *show more* button is hidden
        3. check if long text post's *show more* button is not hidden

    * one like post test
        1. like post
        2. check if new like exists and have correct emoji (database)
        3. check if new like exists and have correct emoji (like-data)
        4. check if new like has data-count = 1
        5. check if like-counter is empty
    
    * change like post test
        1. like post
        2. change like to different emoji
        3. check if old like doesn't exist (database)
        4. check if old like doesn't exist (like-data)
        5. check if new like exists and have correct emoji (database)
        6. check if new like exists and have correct emoji (like-data)
        7. check if new like has data-count = 1

    * the same emoji twice test
        1. like post
        2. like post with the same emoji from a different accout
        3. make sure emoji has has data-count = 2
        4. check if like-counter = +1
    
    * emoji in correct order
        1. like post
        2. like post with different emoji
        3. like post with the same emoji (2.) 
        4. make sure that emoji (2.) is first in like-data panel
    
    * comment-data test
        1. check if comment-count = Comments: 3 (force english)

    * comment button test
        1. click comment button
        2. check if comment-section has show class

* Comments
    * create comment with form -> check if comment exists

    * check comment's content -> equal to comment created

    * click on comment's creator text test
        1. click on comment's creator
        2. check if redirection to correct user profile works

    * click on comment's creator image test
        1. click on comment's creator
        2. check if redirection to correct user profile works

    * edit comment tests
        * comment's creator = current user
            1. check if edit/delete panel is not hidden
            2. click on edit comment
            3. change text
            4. check if comment's content has changed
        * comment's creator != current user
            1. check if edit/delete panel is hidden
        
    * delete comment tests
        1. check if edit/delete panel is not hidden
        2. click on delete comment
        3. check if comment's content got deleted

    * long text comment test
        1. create second comment with long text
        2. check if short text comment's *show more* button is hidden
        3. check if long text comment's *show more* button is not hidden

    * one like comment test
        1. like comment
        2. check if new like exists and have correct emoji (database)
        3. check if new like exists and have correct emoji (like-data)
        4. check if new like has data-count = 1
        5. check if like-counter is empty
    
    * change like comment test
        1. like comment
        2. change like to different emoji
        3. check if old like doesn't exist (database)
        4. check if old like doesn't exist (like-data)
        5. check if new like exists and have correct emoji (database)
        6. check if new like exists and have correct emoji (like-data)
        7. check if new like has data-count = 1

    * the same emoji twice test
        1. like comment
        2. like comment with the same emoji from a different accout
        3. make sure emoji has has data-count = 2
        4. check if like-counter = +1
    
    * emoji in correct order
        1. like comment
        2. like comment with different emoji
        3. like comment with the same emoji (2.) 
        4. make sure that emoji (2.) is first in like-data panel

### user-profile
* check if following data is correct
    1. follow user by 5 users
    2. follow 2 users
    3. check if user following data is correct

* check if bio info is correct (force english)

* check if follow/unfollow logic works
    1. create new user
    2. follow the user
    3. check if user followed
    4. unfollow the user
    5. check if user is unfollowed

### edit-profile
    * auto populate form with user data
        1. add user profile info
        2. make a request
        3. check if form has correct info 