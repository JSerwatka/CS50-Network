from django.test import TestCase, Client
from django.contrib import auth
from django.conf import settings
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile

from selenium import webdriver
import json
import os
from datetime import datetime

from .models import *
from .forms import CreateUserProfileForm

# Create your tests here.
#TODO: Models test
#TODO: Post - editied by somebody else test
#TODO: Post - incorrect id test

class ModelsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="test")
        self.post = Post.objects.create(user=self.user, content="test")
        self.comment = Comment.objects.create(user=self.user, post=self.post, content="test")

    def test_auto_profile_create(self):
        """ Create new user -> create new profile test """
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_default_image_create(self):
        """ New profile created -> create default image test """
        image_path = UserProfile.objects.first().image.path[-11:]
        self.assertEqual(image_path, "default.png")
    
    def test_multiple_likes(self):
        """ Multiple likes on one post by the same user test """
        Like.objects.create(user=self.user, post=self.post, emoji_type=1)

        # Check if IntegrityError raised
        with self.assertRaises(IntegrityError):
            Like.objects.create(user=self.user, post=self.post, emoji_type=2)

class FormsTestCase(TestCase):
    def test_user_profile_form_img_too_big(self):
        """ Check if error occures for too big photo """
        # Get test image path
        test_img_path = os.path.join(settings.MEDIA_ROOT, 'profile_pics', 'test_too_big.jpg')

        # Open the image
        with open(test_img_path, "rb") as infile:
            # create SimpleUploadedFile object from the image
            img_file = SimpleUploadedFile("test_too_big.jpg", infile.read())

            form = CreateUserProfileForm(files={"image": img_file})
        
        self.assertFalse(form.is_valid())
        # Make sure that the correct error msg is in form's errors
        self.assertIn(f"Image file exceeds {settings.MAX_UPLOAD_SIZE} MB size limit", form.errors["image"])


class ViewsTestCase(TestCase):
    def setUp(self):
        # Force english translation
        settings.LANGUAGE_CODE = 'en'

        self.user = User.objects.create_user(username="test", password="test")
        self.c = Client()

    # Login view - GET
    def test_GET_login_status_code(self):
        """ Make sure status code for GET login is 200 """
        response = self.c.get("/login")
        self.assertEqual(response.status_code, 200)
    
    def test_GET_login_correct_redirection(self):
        """ Check redirection to index for logged users """
        # Login user
        self.c.login(username='test', password="test")
        # Get the response
        response = self.c.get('/login')
        # Check redirect status code and redirection url
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    # Login view - POST
    def test_POST_login_correct_user(self):
        """ Check login basic behaviour - status code, redirection, login status """
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)
        # Try to login
        response = self.c.post('/login', {'username': 'test', 'password': 'test'})
        # Get user logged in info
        c_logged_in = auth.get_user(self.c)

        self.assertFalse(c_logged_out.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertTrue(c_logged_in.is_authenticated)

    def test_POST_login_invalid_password(self):
        """ Check invalid password login behaviour """
        response = self.c.post('/login', {'username': 'test', 'password': '123'})

        self.assertEqual(response.context["message"], "Invalid username and/or password.")

    # Logout view
    def test_logout_view(self):
        """ Check all logout behaviour - status code, redirection, login status """
        # Login user
        self.c.login(username='test', password="test")
        # Get user logged in info
        c_logged_in = auth.get_user(self.c)
        # Try to logout
        response = self.c.get('/logout')
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)

        self.assertTrue(c_logged_in.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertFalse(c_logged_out.is_authenticated)

    # Register view - GET
    def test_GET_register_status_code(self):
        """ Make sure status code for GET register is 200 """
        response = self.c.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_GET_register_correct_redirection(self):
        """ Check redirection to index for logged users """
        # Login user
        self.c.login(username='test', password="test")
        # Get response
        response = self.c.get('/register')
        # Check redirect status code and redirection url
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    # Register view - POST
    def test_POST_register_correct(self):
        """ Check register basic behaviour - status code, redirection, login status, new profile created """   
        # Get user logged out info
        c_logged_out = auth.get_user(self.c)
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': 'correct',
            'confirmation': 'correct'
            })
        # Get user registered info
        c_registered = auth.get_user(self.c)
        # Get the new user
        new_user = User.objects.filter(username='correct')

        self.assertFalse(c_logged_out.is_authenticated)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')
        self.assertTrue(c_registered.is_authenticated)
        self.assertEqual(new_user.count(), 1)

    def test_POST_register_empty_username(self):
        """ If username empty -> make sure error msg is correct """ 
        # Try to register
        response = self.c.post('/register', {
            'username': '',
            'email': 'correct@gmail.com',
            'password': 'correct',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_empty_email(self):
        """ If email empty -> make sure error msg is correct """ 
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': '',
            'password': 'correct',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_empty_password(self):
        """ If password empty -> make sure error msg is correct """ 
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': '',
            'confirmation': ''
            })

        self.assertEqual(response.context['message'], "You must fill out all fields.")

    def test_POST_register_passwords_dont_match(self):
        """ If password != confirmation -> make sure error msg is correct """ 
        # Try to register
        response = self.c.post('/register', {
            'username': 'correct',
            'email': 'correct@gmail.com',
            'password': 'test',
            'confirmation': 'correct'
            })

        self.assertEqual(response.context['message'], "Passwords must match.")

    def test_POST_register_username_taken(self):
        """ If user already exists -> make sure error msg is correct """ 
        # Try to register
        response = self.c.post('/register', {
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'test',
            'confirmation': 'test'
            })

        self.assertEqual(response.context['message'], "Username already taken.")

    # Index view
    def test_index_1_page(self):
        """ Make sure status code is correct and 1 page is displayed """
        response = self.c.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)

    def test_index_2_pages(self):
        """ Make sure status code is correct and 2 pages are displayed """
        for _ in range(11):
            Post.objects.create(user=self.user, content="test")

        response = self.c.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)

    # Post-comment view 
    def test_post_comment_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.post('/post-comment/post')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/post-comment/post")

    def test_GET_post_comment(self):
        """ Make sure reponse status code for GET request is 405 (method not allowed) """
        self.c.login(username="test", password="test")
        response = self.c.get('/post-comment/post')

        self.assertEqual(response.status_code, 405)

    # Post-comment view - POST
    def test_POST_post_comment_create_post(self):
        """ Create a post -> check if post exists and if user is redirected to HTTP_REFERER url """
        # Login user
        self.c.login(username="test", password="test")

        # Post a post
        response = self.c.post('/post-comment/post', {"content": "post create test"}, HTTP_REFERER='/')

        self.assertEqual(Post.objects.filter(content="post create test").count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_POST_post_comment_create_comment(self):
        """ Create a comment -> check if comment exists and if user is redirected to HTTP_REFERER url """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")

        # Post a comment on this post
        response = self.c.post('/post-comment/comment', {
            "content": "comment create test",
            'postId': post.id
        }, HTTP_REFERER='/')

        self.assertEqual(Comment.objects.filter(content="comment create test").count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/')

    def test_POST_post_comment_post_doesnt_exist(self):
        """ Create a comment on post that doesn't exist -> check response_status and make sure that it is not in db"""
        # Login user
        self.c.login(username="test", password="test")

        # Post a comment on this post
        response = self.c.post('/post-comment/comment', {
            "content": "comment create test",
            "postId": 1
        }, HTTP_REFERER='/')

        self.assertEqual(Comment.objects.filter(content="comment create test").count(), 0)
        self.assertEqual(response.status_code, 404)

    # Post-comment view - PUT
    def test_PUT_post_comment_edit_post(self):
        """ Test editing of a post """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        old_post = Post.objects.create(user=self.user, content="old content")
        # Edit post's content
        response = self.c.put('/post-comment/post', json.dumps({
            "id": old_post.id,
            "content": "new content"
        }))
        # Get the post after editing
        new_post = Post.objects.get(pk=old_post.id)

        self.assertEqual(old_post.content, "old content")
        self.assertEqual(new_post.content, "new content")
        self.assertEqual(response.status_code, 201)

    def test_PUT_post_comment_edit_comment(self):
        """ Test editing of a comment """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Create a comment
        old_comment = Comment.objects.create(user=self.user, post=post, content="old content")
        # Edit comment's content
        response = self.c.put('/post-comment/comment', json.dumps({
            "id": old_comment.id,
            "content": "new content"
        }))
        # Get the comment after editing
        new_comment = Comment.objects.get(pk=old_comment.id)

        self.assertEqual(old_comment.content, "old content")
        self.assertEqual(new_comment.content, "new content")
        self.assertEqual(response.status_code, 201)

    def test_PUT_post_comment_post_doesnt_exist(self):
        """ Test an attempt to edit a post that doesn't exist -> error and 404 status code """
        # Login user
        self.c.login(username="test", password="test")

        # Try to edit post's content
        response = self.c.put('/post-comment/post', json.dumps({
            "id": 1,
            "content": "new content"
        }))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")
    
    def test_PUT_post_comment_comment_doesnt_exist(self):
        """ Test an attempt to edit a comment that doesn't exist -> error and 404 status code """
        # Login user
        self.c.login(username="test", password="test")

        # Try to edit comment's content
        response = self.c.put('/post-comment/comment', json.dumps({
            "id": 1,
            "content": "new content"
        }))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")

    # Post-comment view - DELETE
    def test_DELETE_post_comment_delete_post(self):
        """ Test deleting of a post """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Get posts count before delete request
        posts_count_before_delete = Post.objects.all().count()

        # Delete the post
        response = self.c.delete('/post-comment/post', json.dumps({"id": post.id}))

        # Get posts count after delete request
        posts_count_after_delete = Post.objects.all().count()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(posts_count_before_delete, 1)
        self.assertEqual(posts_count_after_delete, 0)

    def test_DELETE_post_comment_delete_comment(self):
        """ Test deleting of a comment """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Create a comment
        Comment.objects.create(user=self.user, post=post, content="test")
        # Get comments count before delete request
        comments_count_before_delete = Comment.objects.all().count()

        # Delete the post
        response = self.c.delete('/post-comment/post', json.dumps({"id": post.id}))

        # Get comments count after delete request
        comments_count_after_delete = Comment.objects.all().count()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(comments_count_before_delete, 1)
        self.assertEqual(comments_count_after_delete, 0)

    def test_DELETE_post_comment_post_doesnt_exist(self):
        """ Test an attempt to delete a post that doesn't exist -> error and 404 status code """
        # Login user
        self.c.login(username="test", password="test")

        # Try to delete a post
        response = self.c.delete('/post-comment/post', json.dumps({"id": 1}))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")
    
    def test_DELETE_post_comment_comment_doesnt_exist(self):
        """ Test an attempt to delete a comment that doesn't exist -> error and 404 status code """
        # Login user
        self.c.login(username="test", password="test")

        # Try to delete a comment
        response = self.c.delete('/post-comment/comment', json.dumps({"id": 1}))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")

    # User-profile view
    def test_user_profile_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.post(f'/user-profile/{self.user.id}')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/login?next=/user-profile/{self.user.id}")
    
    def test_GET_user_profile_status_code(self):
        """ Make sure status code for GET user profile is 200 (logged in user) """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get(f'/user-profile/{self.user.id}')
        self.assertEqual(response.status_code, 200)

    def test_user_profile_1_page(self):
        """ Make sure 1 page of posts is displayed """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get(f'/user-profile/{self.user.id}')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)

    def test_user_profile_2_pages(self):
        """ Make sure status 2 pages of posts are displayed """
        # Login user
        self.c.login(username="test", password="test")

        # Create posts (more than can be on 1 page)
        for _ in range(11):
            Post.objects.create(user=self.user, content="test")

        response = self.c.get(f'/user-profile/{self.user.id}')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)

    def test_user_profile_show_only_users_posts(self):
        """ Make sure only posts created by the currently viewed user are visible """
        # Login user
        self.c.login(username="test", password="test")

        # Create a second user
        user_2 = User.objects.create_user(username="test_2", password="test_2")

        # Create user's post
        post_user = Post.objects.create(user=self.user, content="user")
        # Create user_2's post
        post_user_2 = Post.objects.create(user=user_2, content="user_2")

        # Get all posts count
        all_posts = Post.objects.all()

        # Get response from user and user_2 profile
        response = self.c.get(f'/user-profile/{self.user.id}')
        response_user_2 = self.c.get(f'/user-profile/{user_2.id}')

        # Get context paginator posts
        post_list_user = response.context['page_obj'].object_list
        post_list_user_2 = response_user_2.context['page_obj'].object_list

        self.assertEqual(all_posts.count(), 2)
        # User profile - check if only one post exists
        self.assertEqual(post_list_user.count(), 1)
        # User profile - check if post's author is user
        self.assertEqual(post_list_user[0].user, post_user.user)
        # User_2 profile - check if only one post exists
        self.assertEqual(post_list_user_2.count(), 1)
        # User_2 profile - check if post's author is user_2
        self.assertEqual(post_list_user_2[0].user, post_user_2.user)
    
    def test_user_profile_followers(self):
        """ Follow by 5 users -> make sure that correct number is send as a context """
        # Login user
        self.c.login(username="test", password="test")

        # Create 5 users
        for i in range(5):
            Following.objects.create(
                user=User.objects.create_user(username=str(i), password=str(i)),
                user_followed=self.user
            )

        response = self.c.get(f'/user-profile/{self.user.id}')

        self.assertEqual(response.context["followers"].count(), 5)
    
    def test_user_profile_following(self):
        """ Follow 5 users -> make sure that correct number is send as a context """
        # Login user
        self.c.login(username="test", password="test")

        # Create 5 users
        for i in range(5):
            Following.objects.create(
                user=self.user,
                user_followed=User.objects.create_user(username=str(i), password=str(i))
            )

        response = self.c.get(f'/user-profile/{self.user.id}')

        self.assertEqual(response.context["following"].count(), 5)

    # Edit-profile view
    def test_edit_profile_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.post('/edit-profile')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/edit-profile")

    # Edit-profile view - GET
    def test_GET_edit_profile_status_code(self):
        """ Make sure reponse status code for GET request is 200 (logged user) """
        # Login user
        self.c.login(username="test", password="test")
        response = self.c.get('/edit-profile')

        self.assertEqual(response.status_code, 200)

    # Edit-profile view - POST
    def test_POST_edit_profile(self):
        """ Test full POST request -> update all user profile data and redirect to current user profile """
        # Login user
        self.c.login(username="test", password="test")

        # Get test image path
        test_img_path = os.path.join(settings.MEDIA_ROOT, 'profile_pics', 'test.jpg')

        # Open the image
        with open(test_img_path, "rb") as infile:
            # create SimpleUploadedFile object from the image
            img_file = SimpleUploadedFile("test.jpg", infile.read())

            # Send the POST request
            response = self.c.post('/edit-profile', {
                "name": "Tom",
                "date_of_birth": "2000-12-20",
                "about": "My name is Tom",
                "country": "PL",
                "image": img_file
            })

        # Get the new user profile data
        new_user_profile = UserProfile.objects.get(user=self.user)

        # Prepare image file path to comparison
        # 1. Normalize it
        new_img_path = os.path.normpath(new_user_profile.image.path)
        # 2. Get the last part of the path and discard django's additional chars
        img_name = os.path.basename(new_img_path).split("_")[0]


        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/user-profile/{self.user.id}')
        self.assertEqual(new_user_profile.name, "Tom")
        self.assertEqual(new_user_profile.date_of_birth.strftime("%Y-%m-%d"), "2000-12-20")
        self.assertEqual(new_user_profile.about, "My name is Tom")
        self.assertEqual(new_user_profile.country, "PL")
        self.assertEqual(img_name, "test")

        # Delete new image file
        if os.path.exists(new_img_path):
            os.remove(new_img_path)


    # Like view
    def test_like_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.post('/like/post/1')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login?next=/like/post/1")

    # Like view - GET
    def test_GET_like_post_correct(self):
        """ Create a like on a post -> check if GET request gives correct info (like exists and its emoji type) """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Crete a like
        Like.objects.create(user=self.user, post=post, emoji_type=2)

        response = self.c.get(f'/like/post/{post.id}')

        # Get JSON reponse
        json_response = json.loads(response.content)
        response_emoji_type = [emoji_num for emoji_num, emoji_str in Like.LIKE_TYPE_CHOICES if emoji_str == json.loads(response.content)["emojiType"]][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response["like"], "True")
        self.assertEqual(response_emoji_type, 2)

    def test_GET_like_comment_correct(self):
        """ Create a like on a comment -> check if GET request gives correct info (like exists and its emoji type) """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Create a comment
        comment = Comment.objects.create(user=self.user, post=post, content="test")
        # Crete a like
        Like.objects.create(user=self.user, comment=comment, emoji_type=2)

        response = self.c.get(f'/like/comment/{comment.id}')

        # Get JSON reponse
        json_response = json.loads(response.content)
        response_emoji_type = [emoji_num for emoji_num, emoji_str in Like.LIKE_TYPE_CHOICES if emoji_str == json.loads(response.content)["emojiType"]][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json_response["like"], "True")
        self.assertEqual(response_emoji_type, 2)

    def test_GET_like_doesnt_exist(self):
        """ Try to get a like that doesn't exist -> check if status code and response correct  """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")

        response = self.c.get(f'/like/post/{post.id}')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content)["like"], "False")

    def test_GET_like_unknown_action(self):
        """ Send unknown action in the url -> check if status code and error msg correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get('/like/tost/1')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"], "Unknown action - you can only like post or comment"
        )

    def test_GET_like_post_doesnt_exist(self):
        """  Try to like a post that doesn't exist -> check if status code and response correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get('/like/post/1')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")

    def test_GET_like_comment_doesnt_exist(self):
        """  Try to like a post that doesn't exist -> check if status code and response correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get('/like/comment/1')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")


    # Like view - POST
    def test_POST_like_post_correct(self):
        """ Check correct like creation on a post using POST request """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")

        # Post a like
        response = self.c.post(f'/like/post/{post.id}',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        # Get the like
        created_like = post.likes.all()

        self.assertEqual(response.status_code, 201)
        # Make sure only one like created
        self.assertEqual(created_like.count(), 1)
        # Mak sure like's emoji type is dislike
        self.assertEqual(created_like[0].emoji_type, 2)

    def test_POST_like_comment_correct(self):
        """ Check correct like creation on a comment using POST request """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Create a comment
        comment = Comment.objects.create(user=self.user, post=post, content="test")

        # Post a like
        response = self.c.post(f'/like/comment/{comment.id}',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        # Get the like
        created_like = comment.likes.all()

        self.assertEqual(response.status_code, 201)
        # Make sure only one like created
        self.assertEqual(created_like.count(), 1)
        # Mak sure like's emoji type is dislike
        self.assertEqual(created_like[0].emoji_type, 2)

    def test_POST_like_unknown_action(self):
        """ Send unknown action in the url -> check if status code and error msg correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.post('/like/tost/1',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"], "Unknown action - you can only like post or comment"
        )
    
    def test_POST_like_post_doesnt_exist(self):
        """  Try to like a post that doesn't exist -> check if status code and response correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.post('/like/post/1',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")

    def test_POST_like_comment_doesnt_exist(self):
        """  Try to like a comment that doesn't exist -> check if status code and response correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.post('/like/comment/1',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")
    
    # Like view - PUT
    def test_PUT_like_post_correct(self):
        """ Check correct like editing on a post using PUT request """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Crete a like
        Like.objects.create(user=self.user, post=post, emoji_type=2)

        # Change the like
        response = self.c.put(f'/like/post/{post.id}',
                                json.dumps({"emojiType": "smile"}),
                                content_type="application/json")

        # Get the like
        created_like = post.likes.all()

        self.assertEqual(response.status_code, 201)
        # Make sure only one like created
        self.assertEqual(created_like.count(), 1)
        # Mak sure like's emoji type is dislike
        self.assertEqual(created_like[0].emoji_type, 3)

    def test_PUT_like_comment_correct(self):
        """ Check correct like editing on a comment using PUT request """
        # Login user
        self.c.login(username="test", password="test")

        # Create a post
        post = Post.objects.create(user=self.user, content="test")
        # Create a comment
        comment = Comment.objects.create(user=self.user, post=post, content="test")
        # Crete a like
        Like.objects.create(user=self.user, comment=comment, emoji_type=2)

        # Post a like
        response = self.c.put(f'/like/comment/{comment.id}',
                                json.dumps({"emojiType": "smile"}),
                                content_type="application/json")

        # Get the like
        created_like = comment.likes.all()

        self.assertEqual(response.status_code, 201)
        # Make sure only one like created
        self.assertEqual(created_like.count(), 1)
        # Mak sure like's emoji type is dislike
        self.assertEqual(created_like[0].emoji_type, 3)

    def test_PUT_like_unknown_action(self):
        """ Send unknown action in the url -> check if status code and error msg correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.put('/like/tost/1',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content)["error"], "Unknown action - you can only like post or comment"
        )
    
    def test_PUT_like_post_doesnt_exist(self):
        """  Try to change a like on a post that doesn't exist -> check if status code and response correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.put('/like/post/1',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")

    def test_PUT_like_comment_doesnt_exist(self):
        """  Try to like change a like on a comment that doesn't exist -> check if status code and response correct """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.put('/like/comment/1',
                                json.dumps({"emojiType": "dislike"}),
                                content_type="application/json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)["error"], "Post or Comment does not exist")
    
    # Following view
    def test_following_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.post('/following')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login?next=/following')
    
    def test_GET_following_status_code(self):
        """ Make sure status code for GET user profile is 200 (logged in user) """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get('/following')
        self.assertEqual(response.status_code, 200)

    def test_following_1_page(self):
        """ Make sure 1 page of posts is displayed """
        # Login user
        self.c.login(username="test", password="test")

        # Create a user
        new_user = User.objects.create_user(username="1", password="1")

        # Create posts by user which is not followed
        for _ in range(11):
            Post.objects.create(user=new_user, content="test")

        response = self.c.get('/following')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 1)
    
    def test_following_2_pages(self):
        """ Make sure status 2 pages of posts are displayed """
        # Login user
        self.c.login(username="test", password="test")

        # Create 3 users, follow them and create 5 posts for each user
        for i in range(3):
            new_user = User.objects.create_user(username=str(i), password=str(i))

            Following.objects.create(
                user=self.user,
                user_followed=new_user
            )

            for _ in range(5):
                Post.objects.create(user=new_user, content="test")      

        response = self.c.get('/following')

        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)

    def test_following_show_only_users_posts(self):
        """ Make sure only posts created by the followed user are visible """
        # Login user
        self.c.login(username="test", password="test")

        # Create a second user
        user_2 = User.objects.create_user(username="test_2", password="test_2")
        # Follow the new user
        Following.objects.create(user=self.user, user_followed=user_2)

        # Create user's post
        Post.objects.create(user=self.user, content="user")
        # Create user_2's post
        post_user_2 = Post.objects.create(user=user_2, content="user_2")

        # Get all posts
        all_posts = Post.objects.all()

        response = self.c.get('/following')

        # Get context paginator posts
        post_list = response.context['page_obj'].object_list

        self.assertEqual(all_posts.count(), 2)
        # Following - check if only one post exists
        self.assertEqual(len(post_list), 1)
        # Following - check if post's author is user_2
        self.assertEqual(post_list[0].user, post_user_2.user)

    # Follow-unfollow view
    def test_follow_unfollow_login_required(self):
        """ Make sure login required restriction works -> redirect to login """
        response = self.c.post('/follow-unfollow/2')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/login?next=/follow-unfollow/2')
    
    def test_GET_follow_unfollow(self):
        """ Make sure status code for GET user profile is 405 (method not allowed) """
        # Login user
        self.c.login(username="test", password="test")

        response = self.c.get("/follow-unfollow/1")

        self.assertEqual(response.status_code, 405)

    def test_POST_follow_unfollow_correct(self):
        """ Try to follow and unfollow a user -> check if it works and redirection is successful """
        # Login user
        self.c.login(username="test", password="test")

        # Create a new user
        new_user = User.objects.create_user(username="1", password="2")

        # Follow the user
        response_follow = self.c.post(f'/follow-unfollow/{new_user.id}')
        # Get users that the current user follow
        user_followed = self.user.following.all()
        
        # Make sure that the user's following count is 1
        self.assertEqual(user_followed.count(), 1)
        # Make sure that the followed user is new_user
        self.assertEqual(user_followed[0].user_followed.id, new_user.id)
        # Make sure redirection is successful
        self.assertEqual(response_follow.status_code, 302)
        self.assertEqual(response_follow.url, f'/user-profile/{new_user.id}')

        # Send request for the second time = unfollow the user
        response_unfollow = self.c.post(f'/follow-unfollow/{new_user.id}')
        # Check if user is unfollowed
        user_unfollowed = self.user.following.all()
 
        # Make sure that the user is no longer followed after the second request
        self.assertEqual(user_unfollowed.count(), 0)
        # Make sure redirection is successful
        self.assertEqual(response_unfollow.status_code, 302)
        self.assertEqual(response_unfollow.url, f'/user-profile/{new_user.id}')
    
    def test_POST_follow_unfollow_user_doesnt_exist(self):
        """ Follow a user that doesn't exist -> 404 response """
        # Login user
        self.c.login(username="test", password="test")

        # Try to follow a user that doesn't exist
        response = self.c.post('/follow-unfollow/9')

        self.assertEqual(response.status_code, 404)