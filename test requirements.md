# Backend

## Models
### User
* Create new user -> create new profile test

### User Profile
* new profile created -> create default image test

### Like
* multiple likes one one comment/post by the same user test
---

## Forms
### CreateUserProfileForm
* form z image > 5MB -> after cleaned_data -> Validation Error occurs?
---

## Views
### login
* status_code = 200
* create user and try to login with its data
    * check if user logged in
    * test *next* redirection
* check redirection to *index* for logged users
* check invalid password behaviour -> context with correct error msg (force language setting first)
* check user duplicate behaviour -> context with correct error msg

### logout
* status_code = ?
* check user logged-in? -> logout -> user logged-out?
* check redirection to index

### index
* status_code = 200
* no posts -> page_obj context = <page 1 of 1>
* 11 posts -> page_obj context = <page 1 of 2>
* 2 posts -> on frontend in correct order (from newest to oldest)

### post-comment
* login-required test
* POST
    * status_code = ?
    * post post/comment
        1. create a form
        2. post to post-comment/post v post-comment/comment
        3. check if post exists
        4. check if redirect to request source view occurs (comment only)
* PUT
    * status_code = 201
    * edit post/comment
        1. send request's body with new data
        2. check if post's or comment's content has changed
    * incorrect id
        1. send incorrect post's or comment's id
        2. check if status_code is dź 404 and error msg is correct
        3. make sure that the post/comment has not changed
* DELETE
    * status_code = 204
    * delete post/comment
        1. send request's body with post's or comment's id
        2. check if post's or comment's got deleted
    * incorrect id
        1. send incorrect post's or comment's id
        2. check if status_code is dź 404 and error msg is correct
        3. make sure that the post/comment has not been deleted

### user-profile
* status_code = 200
* no posts -> page_obj context = <page 1 of 1>
* 11 posts -> page_obj context = <page 1 of 2>
* 2 posts: by this user and another -> make sure only current is visible
* follow by 5 users -> make sure that correct number is visible on front end
* follow 5 users -> make sure that correct number is visible on front end

### edit-profile
* GET
    * status_code = 200?
    * auto populate form with user data
        1. add user profile info
        2. make a request
        3. check if form has correct info 
* POST
    * post form test
        * send form and check if user profile got updated
        * status_code = ?
        *  check if redirection is corrent


### like
* GET
    * send unknown action and correct id
        * check if status_code = 400
        * check if error msg correct
    * send correct action but like doesn't exist
        * check if status_code = 200
        * check if *like* = *False*
    * send correct action but post/comment doesn't exist
        * check if status_code = 400
        * check if error msg correct
    * check correct like get
        1. create a post/comment
        2. create a like 
        3. send get request
        4. check if:
            * status_code = 200
            * *like* = *True*
            * *emojiType* is correct

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
* status_code = 200
* no posts -> page_obj context = <page 1 of 1>
* 11 posts -> page_obj context = <page 1 of 2>
* 2 posts: by followed user and another -> make sure only followed is visible

### follow-unfollow
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