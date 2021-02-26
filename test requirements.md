# ~~Backend~~

## ~~Models~~
### ~~User~~
* ~~Create new user -> create new profile test~~

### ~~User Profile~~
* ~~new profile created -> create default image test~~

### ~~Like~~
* ~~multiple likes on one comment/post by the same user test~~


## ~~Forms~~
### ~~CreateUserProfileForm~~
* ~~try to upload too big photo to the form~~
    * ~~check if the form is invalid~~
    * ~~check if the correct message is rendered~~

## ~~Views~~
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


### ~~like~~
* ~~login-required test~~
* ~~GET~~
    * ~~check correct like get~~
        1. ~~create a post/comment~~
        2. ~~create a like~~
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

* ~~POST~~
    * ~~send unknown action~~
        * ~~check if status_code = 400~~
        * ~~check if error msg correct~~
    * ~~send correct action but post/comment doesn't exist~~
        * ~~check if status_code = 400~~
        * ~~check if error msg correct~~
    * ~~check correct like creation~~
        * ~~status_code = 201~~
        * ~~like exists with proper emoji_type~~

* ~~PUT~~
    * ~~check correct like editing~~
        * ~~status_code = 201~~
        * ~~like exists with proper emoji_type~~
            1. ~~create a like with one emoji_type~~
            2. ~~request for emoji_type change~~
            3. ~~check if correct emoji type saved~~
    * ~~send unknown action and correct id~~
        * ~~check if status_code = 400~~
        * ~~check if error msg correct~~
    * ~~send correct action but post/comment doesn't exist~~
        * ~~check if status_code = 400~~
        * ~~check if error msg correct~~

### ~~following~~
* ~~login-required test~~
* ~~status_code = 200~~
* ~~no posts -> 1 page available~~
* ~~11 posts -> 2 pages available~~
* ~~Make sure only followed users posts are visible~~

### ~~follow-unfollow~~
* ~~login-required test~~
* ~~GET~~
    * ~~status_code = 405~~
* ~~POST:~~ 
    * ~~correct follow/unfollow user action~~
        * ~~make first follow request~~
        * ~~check if following exists ~~
        * ~~check if redirection is successful~~
        * ~~check status_code~~
        * ~~make second follow request (unfollow)~~
        * ~~make sure user doesn't exist~~
        * ~~check if redirection is successful~~
        * ~~check status_code~~
    * ~~follow a user that doesn't exist -> 404 response~~

# ~~Frontend~~

~~**Setup**~~
1. ~~create a browser handler~~
2. ~~create a user ~~
4. ~~populate the user-profile with data~~
5. ~~create a post~~
6. ~~create several comments to this post~~

### ~~index view~~
* ~~create a post using post form -> check if it exists~~
* ~~check if posts are in correct order (from newest to oldest)~~

#### ~~index, following, user_profile view~~
* ~~Posts~~
    * ~~check if post's content is equal to post created~~

    * ~~check if post creator's name button redirects correctly to user profile~~
        1. ~~click on post creator's name button~~
        2. ~~check if redirection to correct user profile works~~

    * ~~edit post tests~~
        * ~~post's creator != current user -> check if edit/delete panel doesn't exist~~
        * ~~post's creator == current user -> check if edit/delete panel exists~~
        * ~~post's creator == current user~~
            1. ~~click on delete-edit-panel icon~~
            2. ~~click on edit post button~~
            3. ~~change the text~~
            4. ~~check if post's content has changed~~
        
    * ~~delete post test~~
        1. ~~click on delete-edit-panel icon~~
        2. ~~click on delete post~~
        3. ~~check if post's content got deleted~~

    * ~~show more button test~~
        1. ~~create a second post with long text~~
        2. ~~check if the short text post's *show more* button is hidden~~
        3. ~~check if the long text post's *show more* button is not hidden~~

    * ~~like a post test~~
        1. ~~like the post~~
        2. ~~check if the new like exists and have correct emoji (database)~~
        3. ~~check if the new like exists and have correct emoji (like-data)~~
        4. ~~check if the new like has data-count = 1~~
        5. ~~check if the like-counter is empty~~
    
    * ~~change like post test~~
        1. ~~like the post~~
        2. ~~change the like to different emoji~~
        3. ~~check if the new like exists and have correct emoji (database)~~
        4. ~~check if the new like exists and have correct emoji (like-data)~~
        5. ~~check if the new like has data-count = 1~~

    * ~~the same emoji twice test~~
        1. ~~like the post~~
        2. ~~like the post with the same emoji from a different accout~~
        3. ~~make sure the emoji has has data-count = 2~~
        4. ~~check if the like-counter = +1~~
    
    * ~~emoji in correct order~~
        1. ~~like the post~~
        2. ~~like the post with the same emoji from a different accout~~
        3. ~~like the post with a different emoji from the third account~~
        4. ~~make sure that the first emoji is first in the like-data panel~~
    
    * ~~comment-data test~~
        1. ~~check if comment-count is correct~~

    * ~~comment button test~~
        1. ~~click comment button~~
        2. ~~check if comment-section has show class~~

* ~~Comments~~
    * ~~create a comment with form~~
        * ~~check if the comment exists~~
        * ~~check if its content equal to comment created~~

    * ~~click on comment's creator name test~~
        1. ~~click on comment's creator name~~
        2. ~~check if redirection to correct user profile works~~

    * ~~click on comment's creator picture test~~
        1. ~~click on comment's creator picture~~
        2. ~~check if redirection to correct user profile works~~

    * ~~edit comment tests~~
        * ~~comment's creator != current user -> check if edit/delete panel doesn't exist~~
        * ~~comment's creator == current user -> check if edit/delete panel exists~~
        * ~~comment's creator == current user~~
            1. ~~click on delete-edit-panel icon~~
            2. ~~click on edit comment button~~
            3. ~~change the text~~
            4. ~~check if comment's content has changed~~
        
    * ~~delete comment test~~
        1. ~~click on delete-edit-panel icon~~
        2. ~~click on delete comment~~
        3. ~~check if comment's content got deleted~~

    * ~~show more button test~~
        1. ~~create a comment with long text~~
        2. ~~check if the short text comment's *show more* button is hidden~~
        3. ~~check if the long text comment's *show more* button is not hidden~~

    * ~~like a comment test~~
        1. ~~like a comment~~
        2. ~~check if the new like exists and have correct emoji (database)~~
        3. ~~check if the new like exists and have correct emoji (like-data)~~
        4. ~~check if the new like has data-count = 1~~
        5. ~~check if the like-counter is empty~~
    
    * ~~change like comment test~~
        1. ~~like a comment~~
        2. ~~change the like to different emoji~~
        3. ~~check if the new like exists and have correct emoji (database)~~
        4. ~~check if the new like exists and have correct emoji (like-data)~~
        5. ~~check if the new like has data-count = 1~~

    * ~~the same emoji twice test~~
        1. ~~like a comment~~
        2. ~~like the comment with the same emoji from a different accout~~
        3. ~~make sure the emoji has has data-count = 2~~
        4. ~~check if the like-counter = +1~~
    
    * ~~emoji in correct order~~
        1. ~~like a comment~~
        2. ~~like the comment with the same emoji from a different accout~~
        3. ~~like the comment with a different emoji from the third account~~
        4. ~~make sure that the first emoji is first in the like-data panel~~

### ~~user-profile~~
* ~~check if following data is correct~~
    1. ~~follow user by 5 users~~
    2. ~~follow 2 users~~
    3. ~~check if user following data is correct~~

* ~~check if all bio info is correct (force english)~~

* ~~check if profile picture has correct src~~

* ~~check if follow/unfollow logic works~~
    1. ~~create new user~~
    2. ~~follow the user~~
    3. ~~check if user followed~~
    4. ~~unfollow the user~~
    5. ~~check if user is unfollowed~~

### ~~edit-profile~~
* ~~auto populate form with user data~~
    1. ~~open edit-profile page~~
    2. ~~check if the form has correct info~~

* ~~update profile info test~~
    1. ~~fill out the edit-profile form~~
    2. ~~submit it~~
    3. ~~check if user profile data has changed~~
