# Standard
import json
import os
import time
from datetime import datetime
# Django
from django.test import TestCase, Client
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib import auth
from django.conf import settings
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
# Selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
# Local
from .models import *
from .forms import CreateUserProfileForm

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
        test_img_path = os.path.join(settings.MEDIA_ROOT, 'tests', 'test_too_big.jpg')

        # Open the image
        with open(test_img_path, "rb") as infile:
            # create SimpleUploadedFile object from the image
            img_file = SimpleUploadedFile("test_too_big.jpg", infile.read())

            form = CreateUserProfileForm(files={"image": img_file})

        self.assertFalse(form.is_valid())
        # Make sure that the correct error msg is in form's errors
        self.assertIn(f"Image file exceeds {settings.MAX_UPLOAD_SIZE} MB size limit", form.errors["image"])

class ViewsTestCase(TestCase):
    """ Backend test of every view """
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
        test_img_path = os.path.join(settings.MEDIA_ROOT, 'tests', 'test.jpg')

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
        img_name = os.path.basename(new_img_path)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/user-profile/{self.user.id}')
        self.assertEqual(new_user_profile.name, "Tom")
        self.assertEqual(new_user_profile.date_of_birth.strftime("%Y-%m-%d"), "2000-12-20")
        self.assertEqual(new_user_profile.about, "My name is Tom")
        self.assertEqual(new_user_profile.country, "PL")
        self.assertEqual(img_name, "test.jpg")

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

class FrontEndTestCase(StaticLiveServerTestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username="test", password="password")
        self.c = Client()

        # Populate the user-profile with data
        user_profile = self.user.profile
        user_profile.name = "Tom"
        user_profile.date_of_birth = "2000-12-20"
        user_profile.about = "My name is Tom"
        user_profile.country = "PL"
        user_profile.save()

        # Create a post
        post = Post.objects.create(user=self.user, content="post 1")
        # Create comments
        for i in range(3):
            Comment.objects.create(user=self.user, post=post, content=f"comment {i}")

        options = webdriver.ChromeOptions()
        # Set language to english
        options.add_experimental_option('prefs', {'intl.accept_languages': 'en_US'})
        options.add_argument("--lang=en_US")
        # Set chrome to be invisible
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        # For GitHub actions
        self.browser = webdriver.Chrome(chrome_options=options)
        ''' For VS
        # Create chromedirver path
        project_dir = os.path.abspath(os.getcwd())
        chromedriver_dir = os.path.join(project_dir, "chromedriver", "chromedriver.exe")
        self.browser = webdriver.Chrome(chromedriver_dir, chrome_options=options)
        '''
        self.browser.implicitly_wait(10)

        super(FrontEndTestCase, self).setUp()

    def tearDown(self):
        time.sleep(2)
        # Close browser after testing
        self.browser.quit()
        super(FrontEndTestCase, self).tearDown()

    def login_front_end(self, username="test", password="password"):
        """ Method to automate logging in usign login page form """
        time.sleep(1)
        # Go to login page
        self.browser.get(f"{self.live_server_url}/login")

        # Populate login form with username and password
        username_el = self.browser.find_element_by_id("id_username")
        password_el = self.browser.find_element_by_id("id_password")
        username_el.send_keys(username)
        password_el.send_keys(password)

        # Log in
        self.browser.find_element_by_css_selector("input[type='submit']").click()

    def login_quick(self, username="test", password="password"):
        """ Method to automate logging in using client.login method and cookies """
        self.c.login(username=username, password=password)
        cookie = self.c.cookies['sessionid']
        self.browser.get(self.live_server_url)
        self.browser.add_cookie({"name": "sessionid", "value": cookie.value, "secure": False, "path": "/"})

    def is_element_present(self, element, css_locator):
        """ Method to check if element exists in HTML """
        try:
            element.find_element_by_css_selector(css_locator)
        except NoSuchElementException:
            return False
        else:
            return True

    def like_panel_test(self, user, post_comment):
        # Get - like-panel, like button and emoji-choice smile
        like_panel_el = post_comment.find_element_by_css_selector(".like-panel")
        like_button_el = like_panel_el.find_element_by_css_selector(".like-button")
        smile_emoji_el = like_panel_el.find_element_by_css_selector("i[data-name='smile']")


        # Move cursor to the like button -> after 1.5s to the smile emoji -> click on the smile emoji
        action = ActionChains(self.browser)
        time.sleep(1)
        action.move_to_element(like_button_el).perform()
        time.sleep(1.5)
        action.move_to_element(smile_emoji_el).perform()
        time.sleep(0.1)
        smile_emoji_el.click()
        time.sleep(0.7)

        # Check if the new like exists and have correct emoji (database)
        if post_comment.get_attribute("class").find("post") != -1:
            like = Like.objects.filter(post=Post.objects.get(user=user)).all()
        else:
            comment_id = int(post_comment.get_attribute("id").split("_")[-1])
            like = Like.objects.filter(comment=comment_id).all()
        self.assertEqual(like.count(), 1)
        self.assertEqual(like[0].emoji_type, 3)

        # Check if the new like exists and have correct emoji (like-data)
        if post_comment.get_attribute("class").find("post") != -1:
            like_data_el = self.browser.find_element_by_css_selector(".post .like-data")
        else:
            like_data_el = self.browser.find_elements_by_css_selector(".comment .like-data")[0]
        self.assertTrue(self.is_element_present(like_data_el, "ul.emoji-list i[data-name='smile']"))
        # Check if the new like has data-count = 1
        emoji_el = like_data_el.find_element_by_css_selector("ul.emoji-list i[data-name='smile']")
        self.assertEqual(emoji_el.get_attribute("data-count"), "1")
        # Check if the like-counter is empty
        self.assertEqual(like_data_el.find_element_by_class_name("like-counter").text, "")

    # Index tests
    def test_frontend_create_post_from_form(self):
        """ Create a post using post form -> check if it exists """
        # Login user
        self.login_quick()
        # Get index page
        self.browser.get(self.live_server_url)

        # Get form element
        form_el = self.browser.find_element_by_css_selector(".post-form-wrapper form")
        # form_el = WebDriverWait(self.browser, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".post-form-wrapper form"))
        # )

        # Populate textarea
        form_el.find_element_by_id("id_content").send_keys("Sellenium test")
        # Submit form
        form_el.submit()

        # Check if the post exists
        self.assertEqual(Post.objects.filter(content="Sellenium test").count(), 1)

    def test_frontend_post_order(self):
        """ Create 2 posts -> check if they are in correct order (from newest to oldest) """
        # Create 2 posts
        post_1 = Post.objects.create(user=self.user, content="post 2")
        time.sleep(0.1)
        post_2 = Post.objects.create(user=self.user, content="post 3")

        # Login user
        self.login_quick()
        # Get index page
        self.browser.get(self.live_server_url)

        # Wait for page full load
        # WebDriverWait(self.browser, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, ".post-comment-element"))
        # )

        # Get posts
        posts_el = self.browser.find_elements_by_class_name("post")

        # Check is posts' id are in correct order: 3 -> 2 -> 1
        for i, post_el in zip(range(3, 0, -1), posts_el):
            # Get posts inner text
            post_content = post_el.find_elements_by_class_name("post-content")[0]
            # Get posts number
            post_number = post_content.text.split()[-1]
            self.assertEqual(post_number, str(i))

    # User profile tests
    def test_frontend_following_data(self):
        """ Follow user by 5 other users, follow 2 users -> check if data in user profile is correct """
        users = []

        # Crete users and follow self.user
        for i in range(5):
            users.append(User.objects.create_user(username=str(i), password=str(i)))
            Following.objects.create(user=users[i], user_followed=self.user)

        # Make self.user be followed by 2 users
        Following.objects.create(user=self.user, user_followed=users[0])
        Following.objects.create(user=self.user, user_followed=users[1])

        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Get following data
        following_info_card = self.browser.find_element_by_class_name("profile-following")
        followers = following_info_card.find_element_by_css_selector(".followers .follow-count").text
        following = following_info_card.find_element_by_css_selector(".following .follow-count").text

        self.assertEqual(followers, str(5))
        self.assertEqual(following, str(2))

    def test_frontend_bio_info(self):
        """ Check if user's bio in user profile is correct """
        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Get bio info
        bio_info_card = self.browser.find_element_by_class_name("bio")
        name = bio_info_card.find_element_by_css_selector(".profile-name span") \
                            .text.split(":")[-1].strip()
        birth = bio_info_card.find_element_by_css_selector(".profile-birth span") \
                            .text.split(":")[-1].strip()
        about = bio_info_card.find_element_by_css_selector(".profile-about span") \
                            .text.split(":")[-1].strip()
        country = bio_info_card.find_element_by_css_selector(".profile-country span") \
                            .text.split(":")[-1].strip()


        self.assertEqual(name, "Tom")
        self.assertEqual(birth, "20.12.2000")
        self.assertEqual(about, "My name is Tom")
        self.assertEqual(country, "Poland")

    def test_frontend_profile_picture_src(self):
        """ Check if profile picture is in media/profile_pics folder and is default """
        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Get full profile picure src
        profile_picture = self.browser.find_element_by_css_selector(".profile-picture > img").get_attribute("src")
        # Get short src - media/profile_pic/default.png
        profile_picture_short_src = profile_picture.split("/")[-3:]

        self.assertEqual(profile_picture_short_src[0], "media")
        self.assertEqual(profile_picture_short_src[1], "profile_pics")
        self.assertEqual(profile_picture_short_src[2], "default.png")

    def test_frontend_follow_unfollow_button(self):
        """ Check if follow/unfollow button works """
        # Create a user
        new_user = User.objects.create_user(username="1", password="1")

        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/user-profile/{new_user.id}")

        # Try to follow new_user and check if it works
        follow_button = self.browser.find_element_by_css_selector(".profile-buttons button.follow")
        follow_button.click()
        time.sleep(0.1)
        self.assertEqual(Following.objects.filter(user=self.user, user_followed=new_user).count(), 1)

        # Try to unfollow new_user and check it works
        unfollow_button = self.browser.find_element_by_css_selector(".profile-buttons button.unfollow")
        unfollow_button.click()
        time.sleep(0.1)
        self.assertEqual(Following.objects.filter(user=self.user, user_followed=new_user).count(), 0)

    # Edit-profile tests
    def test_frontend_edit_profile_autopopulate_form(self):
        """ Open edit-profile page and check if form is autopopulated with current user data """
        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Open edit-profile page
        edit_profile_button = self.browser.find_element_by_id("edit-profile-btn")
        edit_profile_button.click()

        # Get all the form's fields
        form_el = self.browser.find_element_by_css_selector(".edit-profile-form > form")
        name_el = form_el.find_element_by_css_selector("input[name='name']")
        date_of_birth_el = form_el.find_element_by_css_selector("input[name='date_of_birth']")
        about_el = form_el.find_element_by_css_selector("textarea[name='about']")
        country_el = Select(form_el.find_element_by_css_selector("select[name='country']"))

        self.assertEqual(name_el.get_attribute("value"), "Tom")
        self.assertEqual(date_of_birth_el.get_attribute("value"), "2000-12-20")
        self.assertEqual(about_el.get_attribute("value"), "My name is Tom")
        self.assertEqual(country_el.first_selected_option.get_attribute("value"), "PL")

    def test_frontend_edit_profile_update_profile(self):
        """ Try to fill out and submit the edit-profile form and check if user's data has changed """
        # Get test image path
        test_img_path = os.path.join(settings.MEDIA_ROOT, 'tests', 'test.jpg')

        # Login user
        self.login_quick()
        # Get to self.user profile page
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Open edit-profile page
        edit_profile_button = self.browser.find_element_by_id("edit-profile-btn")
        edit_profile_button.click()

        # Get all the form's fields
        form_el = self.browser.find_element_by_css_selector(".edit-profile-form > form")
        name_el = form_el.find_element_by_css_selector("input[name='name']")
        date_of_birth_el = form_el.find_element_by_css_selector("input[name='date_of_birth']")
        about_el = form_el.find_element_by_css_selector("textarea[name='about']")
        country_el = Select(form_el.find_element_by_css_selector("select[name='country']"))
        image_el = form_el.find_element_by_id("id_image")

        # Clear name input and fill out with new data
        time.sleep(1)
        name_el.clear()
        time.sleep(1)
        name_el.send_keys("John")
        # Change date of birth
        self.browser.execute_script("arguments[0].setAttribute('value', '2020-12-12');", date_of_birth_el)
        # Clear about input and fill out with new data
        about_el.clear()
        time.sleep(1)
        about_el.send_keys("My name is John")
        # Change country
        country_el.select_by_value("RU")
        # Upload a new photo
        image_el.send_keys(test_img_path)
        time.sleep(0.7)
        # Submit the form
        form_el.submit()
        time.sleep(1)

        # Get the new user profile data
        new_user_profile = UserProfile.objects.get(user=self.user)

        # Prepare image file path to comparison
        # 1. Normalize it
        new_img_path = os.path.normpath(new_user_profile.image.path)
        # 2. Get the last part of the path and discard django's additional chars
        img_name = os.path.basename(new_img_path)

        self.assertEqual(new_user_profile.name, "John")
        self.assertEqual(new_user_profile.date_of_birth.strftime("%Y-%m-%d"), "2020-12-12")
        self.assertEqual(new_user_profile.about, "My name is John")
        self.assertEqual(new_user_profile.country, "RU")
        self.assertEqual(img_name, "test.jpg")

        # Delete new image file
        if os.path.exists(new_img_path):
            os.remove(new_img_path)

    # Posts tests
    def test_frontend_post_content(self):
        """ Check if post's content is equal to post created (index, user-profile, following) """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        Post.objects.create(user=new_user, content="new user post")

        # Login user
        self.login_quick()

        # Check **index view**
        self.browser.get(self.live_server_url)
        posts_content_el = self.browser.find_elements_by_css_selector(".post .post-content")

        self.assertEqual(len(posts_content_el), 2)
        self.assertEqual(posts_content_el[0].text, "new user post")
        self.assertEqual(posts_content_el[1].text, "post 1")

        # Check **user-profile view**
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        posts_content_el = self.browser.find_elements_by_css_selector(".post .post-content")

        self.assertEqual(len(posts_content_el), 1)
        self.assertEqual(posts_content_el[0].text, "post 1")

        # Check **following view**
        self.browser.get(self.live_server_url + "/following")
        posts_content_el = self.browser.find_elements_by_css_selector(".post .post-content")

        self.assertEqual(len(posts_content_el), 1)
        self.assertEqual(posts_content_el[0].text, "new user post")

    def test_frontend_post_creator_button(self):
        """ Check if post creator's name button redirects correctly to user profile """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        Post.objects.create(user=new_user, content="new user post")

        # Login user
        self.login_quick()

        # **Check index view**
        self.browser.get(self.live_server_url)
        post_user_link_el = self.browser.find_elements_by_css_selector(".post .post-user > a")
        # The second post = self.user's post
        post_user_link_el[1].click()
        time.sleep(0.1)

        # Get current url
        current_url_list = self.browser.current_url.split("/")
        # Check if url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

        # **Check user-profile view**
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        post_user_link_el = self.browser.find_elements_by_css_selector(".post .post-user > a")
        # The only post = self.user's post
        post_user_link_el[0].click()
        time.sleep(0.1)

        # Get current url
        current_url_list = self.browser.current_url.split("/")
        # Check if url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

        # **Check following view**
        self.browser.get(self.live_server_url + "/following")
        post_user_link_el = self.browser.find_elements_by_css_selector(".post .post-user > a")
        # The only post = new_user's post
        post_user_link_el[0].click()
        time.sleep(0.1)

        # Get current url
        current_url_list = self.browser.current_url.split("/")
        # Check if url is .../user-profile/{new_user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(new_user.id))

    def test_frontend_index_delete_edit_panel_exists_post(self):
        """ Check if delete-edit-panel exists or doesn't exist for post's creator == current user and post's creator != current user """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Creat a post by the second user
        Post.objects.create(user=new_user, content="new user post")

        # Login user
        self.login_quick()
        # Go to index view
        self.browser.get(self.live_server_url)

        # Get posts
        posts_el = self.browser.find_elements_by_css_selector(".post")

        # Check if delete-edit-panel is present or not
        self.assertFalse(self.is_element_present(posts_el[0], ".delete-edit-panel"))
        self.assertTrue(self.is_element_present(posts_el[1], ".delete-edit-panel"))

    def test_frontend_user_profile_delete_edit_panel_exists_post(self):
        """ Check if delete-edit-panel exists or doesn't exist for post's creator == current user and post's creator != current user """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Creat a post by the second user
        Post.objects.create(user=new_user, content="new user post")

        # Login user
        self.login_quick()

        # Go to the self.user profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get delete-edit-panels
        posts_el = self.browser.find_elements_by_css_selector(".post")
        # Check if delete-edit-panel is present
        self.assertTrue(self.is_element_present(posts_el[0], ".delete-edit-panel"))

        # Go to new_user profile view
        self.browser.get(self.live_server_url + f"/user-profile/{new_user.id}")
        # Get posts
        posts_el = self.browser.find_elements_by_css_selector(".post")
        # Check if delete-edit-panel is present
        self.assertFalse(self.is_element_present(posts_el[0], ".delete-edit-panel"))

    def test_frontend_following_delete_edit_panel_exists_post(self):
        """ Check if delete-edit-panel doesn't exist for and post's creator != current user """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        Post.objects.create(user=new_user, content="new user post")

        # Login the user
        self.login_quick()
        # Go to the following view
        self.browser.get(self.live_server_url + "/following")

        # Get the posts
        posts_el = self.browser.find_elements_by_css_selector(".post")
        # Check if the delete-edit-panel is present
        self.assertFalse(self.is_element_present(posts_el[0], ".delete-edit-panel"))

    def test_frontend_edit_post(self):
        """ Try to edit a post using edit button (index and user-profile views) """
        # Login the user
        self.login_quick()

        for url in ["", f"/user-profile/{self.user.id}"]:
            self.browser.get(self.live_server_url + url)

            # Get the delete-edit-panel
            delete_edit_panel = self.browser.find_element_by_css_selector(".post .delete-edit-panel")
            # Click on the icon button
            delete_edit_panel.find_element_by_class_name("icon-button").click()
            time.sleep(0.1)
            # Click on the edit button
            delete_edit_panel.find_element_by_class_name("dropdown-edit").click()
            # Get the modal, its textarea and save button
            modal_el = self.browser.find_element_by_css_selector(".post .edit-modal")
            modal_textarea_el = modal_el.find_element_by_css_selector(".modal-body textarea")
            modal_save_button = modal_el.find_element_by_css_selector(".modal-footer button.modal-save")
            # Change the modal textarea's value
            modal_textarea_el.clear()
            time.sleep(0.7)
            modal_textarea_el.send_keys("Post edited-" + self.browser.current_url)
            time.sleep(0.5)
            modal_save_button.click()
            time.sleep(1)

            # Get the post's data
            edited_post = Post.objects.get(user=self.user)

            self.assertEqual(edited_post.content, "Post edited-" + self.browser.current_url)

    def test_frontend_index_delete_post(self):
        """ Try to delete a post using delete button """
        # Login the user
        self.login_quick()
        # Go to the index view
        self.browser.get(self.live_server_url)

        # Get delete-edit-panel
        delete_edit_panel = self.browser.find_element_by_css_selector(".post .delete-edit-panel")
        # Click on the icon button
        delete_edit_panel.find_element_by_class_name("icon-button").click()
        time.sleep(0.1)
        # Click on the delete button
        delete_edit_panel.find_element_by_class_name("dropdown-delete").click()
        # Get the modal and click delete
        modal_el = self.browser.find_element_by_css_selector(".post .delete-modal")
        modal_el.find_element_by_css_selector(".modal-footer button.modal-delete").click()
        time.sleep(0.7)

        # Get the post
        deleted_post = Post.objects.filter(user=self.user).all()

        self.assertEqual(deleted_post.count(), 0)

    def test_frontend_user_profile_delete_post(self):
        """ Try to delete a post using delete button """
        # Login the user
        self.login_quick()
        # Go to the self.user profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Get delete-edit-panel
        delete_edit_panel = self.browser.find_element_by_css_selector(".post .delete-edit-panel")
        # Click on the icon button
        delete_edit_panel.find_element_by_class_name("icon-button").click()
        time.sleep(0.1)
        # Click on the delete button
        delete_edit_panel.find_element_by_class_name("dropdown-delete").click()
        # Get the modal and click delete
        modal_el = self.browser.find_element_by_css_selector(".post .delete-modal")
        modal_el.find_element_by_css_selector(".modal-footer button.modal-delete").click()
        time.sleep(0.7)

        # Get the post
        deleted_post = Post.objects.filter(user=self.user).all()

        self.assertEqual(deleted_post.count(), 0)

    def test_frontend_showmore_button_post(self):
        """ Check if show more button shows up for long posts (index, user-profile, following) """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a long text post
        Post.objects.create(user=self.user, content=("Lorem ipsum" * 200))

        # Login the user
        self.login_quick()

        # Test the index and user-profile view
        for url in ["", f"/user-profile/{self.user.id}"]:
            self.browser.get(self.live_server_url + url)

            # Get posts
            posts_el = self.browser.find_elements_by_class_name("post")

            # new_user post - make sure the *show more* button is not hidden
            self.assertNotIn("hidden", posts_el[0].find_element_by_class_name("show-more").get_attribute("class"))
            # self.user post - make sure the *show more* button is hidden
            self.assertIn("hidden", posts_el[1].find_element_by_class_name("show-more").get_attribute("class"))

        # Test the following view
        # Create a short text post (new_user)
        Post.objects.create(user=new_user, content=("Lorem ipsum"))
        time.sleep(0.5)
        # Creat a long text post (new_user)
        Post.objects.create(user=new_user, content=("Lorem ipsum" * 200))

        # Go to the following view
        self.browser.get(self.live_server_url + "/following")

        # Get posts
        posts_el = self.browser.find_elements_by_class_name("post")

        # new_user post - make sure the *show more* button is not hidden
        self.assertNotIn("hidden", posts_el[0].find_element_by_class_name("show-more").get_attribute("class"))
        # self.user post - make sure the *show more* button is hidden
        self.assertIn("hidden", posts_el[1].find_element_by_class_name("show-more").get_attribute("class"))

    def test_frontend_index_like_post(self):
        """ Try to like a post using like-button -> check if new like exists and data-count, like-counter values are correct """
        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)

        # Get the post
        post_el = self.browser.find_element_by_class_name("post")
        # Perform the test
        self.like_panel_test(self.user, post_el)

    def test_frontend_user_profile_like_post(self):
        """ Try to like a post using like-button -> check if new like exists and data-count, like-counter values are correct """
        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Get the post
        post_el = self.browser.find_element_by_class_name("post")
        # Perform the test
        self.like_panel_test(self.user, post_el)

    def test_frontend_following_like_post(self):
        """ Try to like a post using like-button -> check if new like exists and data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        Post.objects.create(user=new_user, content="Lorem ipsum")

        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")

        # Get the post
        post_el = self.browser.find_element_by_class_name("post")
        # Perform the test
        self.like_panel_test(new_user, post_el)

    def test_frontend_index_change_like_post(self):
        """ Try to change a like on a post -> check if new emojie exists and data-count, like-counter values are correct """
        # Create a like
        Like.objects.create(user=self.user, post=self.user.posts.all()[0], emoji_type=1)

        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)

        # Get the post
        post_el = self.browser.find_element_by_class_name("post")
        # Perform the test
        self.like_panel_test(self.user, post_el)

    def test_frontend_user_profile_change_like_post(self):
        """ Try to change a like on a post -> check if new emojie exists and data-count, like-counter values are correct """
        # Create a like
        Like.objects.create(user=self.user, post=self.user.posts.all()[0], emoji_type=1)

        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Get the post
        post_el = self.browser.find_element_by_class_name("post")
        # Perform the test
        self.like_panel_test(self.user, post_el)

    def test_frontend_following_change_like_post(self):
        """ Try to change a like on a post -> check if new emojie exists and data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        new_post = Post.objects.create(user=new_user, content="Lorem ipsum")
        # Create a like
        Like.objects.create(user=self.user, post=new_post, emoji_type=1)

        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")

        # Get the post
        post_el = self.browser.find_element_by_class_name("post")
        # Perform the test
        self.like_panel_test(new_user, post_el)

    def test_frontend_index_like_emoji_twice_post(self):
        """ Liking one post with the same emoji twice -> check if data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Create likes
        Like.objects.create(user=self.user, post=self.user.posts.all()[0], emoji_type=2)
        Like.objects.create(user=new_user, post=self.user.posts.all()[0], emoji_type=2)

        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)

        # Check if the emoji has data-count = 2
        emoji_el = self.browser.find_element_by_css_selector(".post ul.emoji-list i[data-name='dislike']")
        like_counter_el = self.browser.find_element_by_css_selector(".post .like-data .like-counter")

        self.assertEqual(emoji_el.get_attribute("data-count"), "2")

        # Check if the like-counter = 1
        self.assertEqual(like_counter_el.text, "+1")

    def test_frontend_user_profile_like_emoji_twice_post(self):
        """ Liking one post with the same emoji twice -> check if data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Create likes
        Like.objects.create(user=self.user, post=self.user.posts.all()[0], emoji_type=3)
        Like.objects.create(user=new_user, post=self.user.posts.all()[0], emoji_type=3)

        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Check if the emoji has data-count = 2
        emoji_el = self.browser.find_element_by_css_selector(".post ul.emoji-list i[data-name='smile']")
        like_counter_el = self.browser.find_element_by_css_selector(".post .like-data .like-counter")

        self.assertEqual(emoji_el.get_attribute("data-count"), "2")

        # Check if the like-counter = 1
        self.assertEqual(like_counter_el.text, "+1")

    def test_frontend_following_like_emoji_twice_post(self):
        """ Liking one post with the same emoji twice -> check if data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        new_post = Post.objects.create(user=new_user, content="Lorem ipsum")
        # Create likes
        Like.objects.create(user=self.user, post=new_post, emoji_type=1)
        Like.objects.create(user=new_user, post=new_post, emoji_type=1)

        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")

        # Check if the emoji has data-count = 2
        emoji_el = self.browser.find_element_by_css_selector(".post ul.emoji-list i[data-name='like']")
        like_counter_el = self.browser.find_element_by_css_selector(".post .like-data .like-counter")

        self.assertEqual(emoji_el.get_attribute("data-count"), "2")

        # Check if the like-counter = 1
        self.assertEqual(like_counter_el.text, "+1")

    def test_frontend_index_emoji_correct_order_post(self):
        """ Make sure that emoji with most likes is first """
        # Create a second user
        second_user = User.objects.create_user(username="1", password="1")
        # Create a third user
        third_user = User.objects.create_user(username="2", password="2")
        # Create likes
        Like.objects.create(user=self.user, post=self.user.posts.all()[0], emoji_type=1)
        Like.objects.create(user=second_user, post=self.user.posts.all()[0], emoji_type=3)
        Like.objects.create(user=third_user, post=self.user.posts.all()[0], emoji_type=3)

        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)

        # Check if smile emoji is first and like emoji is second
        emoji_list_el = self.browser.find_elements_by_css_selector(".post ul.emoji-list > i")

        self.assertEqual(emoji_list_el[0].get_attribute("data-name"), "smile")
        self.assertEqual(emoji_list_el[1].get_attribute("data-name"), "like")

    def test_frontend_user_profile_emoji_correct_order_post(self):
        """ Make sure that emoji with most likes is first """
        # Create a second user
        second_user = User.objects.create_user(username="1", password="1")
        # Create a third user
        third_user = User.objects.create_user(username="2", password="2")
        # Create likes
        Like.objects.create(user=self.user, post=self.user.posts.all()[0], emoji_type=1)
        Like.objects.create(user=second_user, post=self.user.posts.all()[0], emoji_type=3)
        Like.objects.create(user=third_user, post=self.user.posts.all()[0], emoji_type=3)

        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")

        # Check if smile emoji is first and like emoji is second
        emoji_list_el = self.browser.find_elements_by_css_selector(".post ul.emoji-list > i")

        self.assertEqual(emoji_list_el[0].get_attribute("data-name"), "smile")
        self.assertEqual(emoji_list_el[1].get_attribute("data-name"), "like")

    def test_frontend_following_emoji_correct_order_post(self):
        """ Make sure that emoji with most likes is first """
        # Create a second user
        second_user = User.objects.create_user(username="1", password="1")
        # Create a third user
        third_user = User.objects.create_user(username="2", password="2")
        # Follow the second user
        Following.objects.create(user=self.user, user_followed=second_user)
        # Creat a post by the second user
        new_post = Post.objects.create(user=second_user, content="Lorem ipsum")
        # Create likes
        Like.objects.create(user=self.user, post=new_post, emoji_type=3)
        Like.objects.create(user=second_user, post=new_post, emoji_type=1)
        Like.objects.create(user=third_user, post=new_post, emoji_type=3)

        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")

        # Check if smile emoji is first and like emoji is second
        emoji_list_el = self.browser.find_elements_by_css_selector(".post ul.emoji-list > i")

        self.assertEqual(emoji_list_el[0].get_attribute("data-name"), "smile")
        self.assertEqual(emoji_list_el[1].get_attribute("data-name"), "like")

    def test_frontend_comment_data_post(self):
        """ Check if comment-count == 3 for index and user-profile and 0 for following """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        Post.objects.create(user=new_user, content="Lorem ipsum")

        # Login the user
        self.login_quick()

        # Get the index view
        self.browser.get(self.live_server_url)
        posts_el = self.browser.find_elements_by_css_selector(".post")
        # Get comment count for self.user's post
        comment_count_el = posts_el[1].find_element_by_css_selector(".comment-data")
        comment_count_text = comment_count_el.text.split(":")[-1].strip()
        self.assertEqual(comment_count_text, str(3))

        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get comment count for self.user's post
        comment_count_el = self.browser.find_element_by_css_selector(".post .comment-data")
        comment_count_text = comment_count_el.text.split(":")[-1].strip()
        self.assertEqual(comment_count_text, str(3))

        # Get the following view
        self.browser.get(self.live_server_url + "/following")
        # Get comment count for new_user's post
        comment_count_el = self.browser.find_element_by_css_selector(".post .comment-data")
        comment_count_text = comment_count_el.text.split(":")[-1].strip()
        self.assertEqual(comment_count_text, str(0))

    def test_frontend_comment_section_post(self):
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        Post.objects.create(user=new_user, content="Lorem ipsum")

        # Login the user
        self.login_quick()

        # Get the index view
        self.browser.get(self.live_server_url)
        # Get the comment button and click it
        comment_button = self.browser.find_elements_by_css_selector(".post .comment-button")[0]
        time.sleep(1.5)
        action = ActionChains(self.browser)
        time.sleep(3)
        action.move_to_element(comment_button).perform()
        time.sleep(0.5)
        comment_button.click()
        time.sleep(0.7)
        # Get the comment section
        comment_section_el = self.browser.find_elements_by_css_selector(".post-comment-element .comment-section")[0]
        self.assertIn("show", comment_section_el.get_attribute("class"))

        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the comment button and click it
        comment_button = self.browser.find_element_by_css_selector(".post .comment-button")
        action = ActionChains(self.browser)
        action.move_to_element(comment_button).perform()
        time.sleep(0.5)
        comment_button.click()
        time.sleep(0.7)
        # Get the comment section
        comment_section_el = self.browser.find_elements_by_css_selector(".post-comment-element .comment-section")[0]
        self.assertIn("show", comment_section_el.get_attribute("class"))

        # Get the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the comment button and click it
        comment_button = self.browser.find_element_by_css_selector(".post .comment-button")
        action = ActionChains(self.browser)
        action.move_to_element(comment_button).perform()
        time.sleep(0.5)
        comment_button.click()
        time.sleep(0.7)
        # Get the comment section
        comment_section_el = self.browser.find_elements_by_css_selector(".post-comment-element .comment-section")[0]
        self.assertIn("show", comment_section_el.get_attribute("class"))

    # Comments tests
    def test_frontend_index_post_comment(self):
        """ Create a comment using form -> check if it exists """

        # Login the user
        self.login_quick()

        self.browser.get(self.live_server_url)
        # Open comment section
        comment_button = self.browser.find_element_by_css_selector(".post .comment-button")
        comment_button.click()

        # Get the form and create a new comment
        comment_form_el = self.browser.find_element_by_css_selector(".comment-form-wrapper form")
        comment_form_el.find_element_by_css_selector("textarea").send_keys("Sellenium test")
        comment_form_el.submit()

        # Check if the new comment exists
        self.assertEqual(Comment.objects.filter(content="Sellenium test").count(), 1)

    def test_frontend_user_profile_post_comment(self):
        """ Create a comment using form -> check if it exists """

        # Login the user
        self.login_quick()

        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Open comment section
        comment_button = self.browser.find_element_by_css_selector(".post .comment-button")
        comment_button.click()

        # Get the form and create a new comment
        comment_form_el = self.browser.find_element_by_css_selector(".comment-form-wrapper form")
        comment_form_el.find_element_by_css_selector("textarea").send_keys("Sellenium test")
        comment_form_el.submit()

        # Check if the new comment exists
        self.assertEqual(Comment.objects.filter(content="Sellenium test").count(), 1)

    def test_frontend_following_post_comment(self):
        """ Create a comment using form -> check if it exists """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a long text post
        Post.objects.create(user=new_user, content="Lorem ipsum")

        # Login the user
        self.login_quick()

        self.browser.get(self.live_server_url + "/following")
        # Open comment section
        comment_button = self.browser.find_element_by_css_selector(".post .comment-button")
        comment_button.click()

        # Get the form and create a new comment
        comment_form_el = self.browser.find_element_by_css_selector(".comment-form-wrapper form")
        comment_form_el.find_element_by_css_selector("textarea").send_keys("Sellenium test")
        comment_form_el.submit()

        # Check if the new comment exists
        self.assertEqual(Comment.objects.filter(content="Sellenium test").count(), 1)

    def test_frontend_comment_creator_button_text(self):
        """ Check if comment creator's name button redirects correctly to user profile  """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        post = Post.objects.create(user=new_user, content="new user post")
        # Creat a comment to this post
        Comment.objects.create(user=self.user, post=post, content="comment")

        # Login the user
        self.login_quick()

        # Check **index view**
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        comment_user_link_text_el = post_comment_el.find_element_by_css_selector(".comment-main > a")
        comment_user_link_text_el.click()
        time.sleep(0.1)

        # Get the current url
        current_url_list = self.browser.current_url.split("/")
        # Check if the url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

        # Check **user-profile view**
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        comment_user_link_text_el = post_comment_el.find_elements_by_css_selector(".comment-main > a")
        comment_user_link_text_el[0].click()
        time.sleep(0.1)

        # Get the current url
        current_url_list = self.browser.current_url.split("/")
        # Check if the url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

        # Check **following view**
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        comment_user_link_text_el = post_comment_el.find_elements_by_css_selector(".comment-main > a")
        comment_user_link_text_el[0].click()
        time.sleep(0.1)

        # Get the current url
        current_url_list = self.browser.current_url.split("/")
        # Check if the url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

    def test_frontend_comment_creator_button_picture(self):
        """ Check if comment creator's picture button redirects correctly to user profile  """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        post = Post.objects.create(user=new_user, content="new user post")
        # Creat a comment to this post
        Comment.objects.create(user=self.user, post=post, content="comment")

        # Login the user
        self.login_quick()

        # Check **index view**
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        comment_user_link_text_el = post_comment_el.find_element_by_css_selector(".comment-user-image > a")
        comment_user_link_text_el.click()
        time.sleep(0.1)

        # Get the current url
        current_url_list = self.browser.current_url.split("/")
        # Check if the url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

        # Check **user-profile view**
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        comment_user_link_text_el = post_comment_el.find_elements_by_css_selector(".comment-user-image > a")
        comment_user_link_text_el[0].click()
        time.sleep(0.1)

        # Get the current url
        current_url_list = self.browser.current_url.split("/")
        # Check if the url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

        # Check **following view**
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        comment_user_link_text_el = post_comment_el.find_elements_by_css_selector(".comment-user-image > a")
        comment_user_link_text_el[0].click()
        time.sleep(0.1)

        # Get the current url
        current_url_list = self.browser.current_url.split("/")
        # Check if the url is .../user-profile/{self.user.id}
        self.assertEqual(current_url_list[-2], "user-profile")
        self.assertEqual(current_url_list[-1], str(self.user.id))

    def test_frontend_index_delete_edit_panel_exists_comment(self):
        """ Check if delete-edit-panel exists or doesn't exist for comment's creator == current user and comment's creator != current user """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Create a comment by the second user
        Comment.objects.create(user=new_user, post=self.user.posts.all()[0], content="new user comment")

        # Login the user
        self.login_quick()
        # Go to the index view
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Get the comments
        comments_el = post_comment_el.find_elements_by_css_selector(".comment")

        # Check if delete-edit-panel is present or not
        self.assertTrue(self.is_element_present(comments_el[0], ".delete-edit-panel"))
        self.assertTrue(self.is_element_present(comments_el[1], ".delete-edit-panel"))
        self.assertTrue(self.is_element_present(comments_el[2], ".delete-edit-panel"))
        self.assertFalse(self.is_element_present(comments_el[3], ".delete-edit-panel"))

    def test_frontend_user_profile_delete_edit_panel_exists_comment(self):
        """ Check if delete-edit-panel exists or doesn't exist for comment's creator == current user and comment's creator != current user """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Create a comment by the second user
        Comment.objects.create(user=new_user, post=self.user.posts.all()[0], content="new user comment")

        # Login the user
        self.login_quick()
        # Go to the self.user profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Get the comments
        comments_el = post_comment_el.find_elements_by_css_selector(".comment")

        # Check if delete-edit-panel is present or not
        self.assertTrue(self.is_element_present(comments_el[0], ".delete-edit-panel"))
        self.assertTrue(self.is_element_present(comments_el[1], ".delete-edit-panel"))
        self.assertTrue(self.is_element_present(comments_el[2], ".delete-edit-panel"))
        self.assertFalse(self.is_element_present(comments_el[3], ".delete-edit-panel"))

    def test_frontend_following_delete_edit_panel_exists_comment(self):
        """ Check if delete-edit-panel exists or doesn't exist for comment's creator == current user and comment's creator != current user """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        post = Post.objects.create(user=new_user, content="new user post")
        # Create comments by the second user adn by self.user
        Comment.objects.create(user=new_user, post=post, content="new user comment")
        Comment.objects.create(user=self.user, post=post, content="self.user comment")

        # Login the user
        self.login_quick()
        # Go to the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Get the comments
        comments_el = post_comment_el.find_elements_by_css_selector(".comment")

        # Check if delete-edit-panel is present or not
        self.assertFalse(self.is_element_present(comments_el[0], ".delete-edit-panel"))
        self.assertTrue(self.is_element_present(comments_el[1], ".delete-edit-panel"))

    def test_frontend_edit_comment(self):
        """ Try to edit a comment using edit button (index and user-profile views) """
        # Get the oldest comment
        comment = Comment.objects.get(content="comment 0")
        # Login the user
        self.login_quick()

        for url in ["", f"/user-profile/{self.user.id}"]:
            self.browser.get(self.live_server_url + url)
            # Get the post-comment element
            post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
            # Open comment section
            comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
            comment_button[0].click()

            # Get the delete-edit-panel
            delete_edit_panel = self.browser.find_elements_by_css_selector(".comment .delete-edit-panel")[0]
            # Click on the icon button
            delete_edit_panel.find_element_by_class_name("icon-button").click()
            time.sleep(1.5)
            # Click on the edit button
            delete_edit_panel.find_element_by_class_name("dropdown-edit").click()
            # Get the modal, its textarea and save button
            modal_el = self.browser.find_element_by_css_selector(".comment .edit-modal")
            modal_textarea_el = modal_el.find_element_by_css_selector(".modal-body textarea")
            modal_save_button = modal_el.find_element_by_css_selector(".modal-footer button.modal-save")
            time.sleep(1.5)
            # Change the modal textarea's value
            modal_textarea_el.clear()
            time.sleep(1.5)
            modal_textarea_el.send_keys("Comment edited-" + self.browser.current_url)
            time.sleep(0.5)
            modal_save_button.click()
            time.sleep(1)

            # Get the comment's  new data
            edited_comment_content = Comment.objects.get(pk=comment.id).content

            self.assertEqual(edited_comment_content, "Comment edited-" + self.browser.current_url)

    def test_frontend_index_delete_comment(self):
        """ Try to delete a comment using delete button """
        # Login the user
        self.login_quick()
        # Go to the index view
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Get delete-edit-panel
        delete_edit_panel = self.browser.find_element_by_css_selector(".comment .delete-edit-panel")
        # Click on the icon button
        delete_edit_panel.find_element_by_class_name("icon-button").click()
        time.sleep(0.1)
        # Click on the delete button
        delete_edit_panel.find_element_by_class_name("dropdown-delete").click()
        # Get the modal and click delete
        modal_el = self.browser.find_element_by_css_selector(".comment .delete-modal")
        modal_el.find_element_by_css_selector(".modal-footer button.modal-delete").click()
        time.sleep(0.7)

        # Get the comments
        deleted_comment = Comment.objects.filter(user=self.user, content="comment 0").all()

        self.assertEqual(deleted_comment.count(), 0)

    def test_frontend_user_profile_delete_comment(self):
        """ Try to delete a comment using delete button """
        # Login the user
        self.login_quick()
        # Go to the self.user profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Get delete-edit-panel
        delete_edit_panel = self.browser.find_element_by_css_selector(".comment .delete-edit-panel")
        # Click on the icon button
        delete_edit_panel.find_element_by_class_name("icon-button").click()
        time.sleep(0.1)
        # Click on the delete button
        delete_edit_panel.find_element_by_class_name("dropdown-delete").click()
        # Get the modal and click delete
        modal_el = self.browser.find_element_by_css_selector(".comment .delete-modal")
        modal_el.find_element_by_css_selector(".modal-footer button.modal-delete").click()
        time.sleep(0.7)

        # Get the comments
        deleted_comment = Comment.objects.filter(user=self.user, content="comment 0").all()

        self.assertEqual(deleted_comment.count(), 0)

    def test_frontend_following_delete_comment(self):
        """ Try to delete a comment using delete button """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        post = Post.objects.create(user=new_user, content="new user post")
        # Create comments by self.user
        comment = Comment.objects.create(user=self.user, post=post, content="new user comment")

        # Login the user
        self.login_quick()
        # Go to the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Get delete-edit-panel
        delete_edit_panel = self.browser.find_element_by_css_selector(".comment .delete-edit-panel")
        # Click on the icon button
        delete_edit_panel.find_element_by_class_name("icon-button").click()
        time.sleep(0.1)
        # Click on the delete button
        delete_edit_panel.find_element_by_class_name("dropdown-delete").click()
        # Get the modal and click delete
        modal_el = self.browser.find_element_by_css_selector(".comment .delete-modal")
        modal_el.find_element_by_css_selector(".modal-footer button.modal-delete").click()
        time.sleep(0.7)

        # Get the comments
        deleted_comment = Comment.objects.filter(pk=comment.id).all()

        self.assertEqual(deleted_comment.count(), 0)

    def test_frontend_showmore_button_comment(self):
        """ Check if show more button shows up for long comments (index, user-profile, following) """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post by the second user
        post = Post.objects.create(user=new_user, content="new user post")
        # Creat a long text comment by self.user
        Comment.objects.create(user=self.user, post=self.user.posts.all()[0], content=("Lorem ipsum" * 200))

        # Login the user
        self.login_quick()

        # Test the **index** and **user-profile view**
        for url in ["", f"/user-profile/{self.user.id}"]:
            self.browser.get(self.live_server_url + url)
            # Get the post-comment element
            post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")
            post_comment_el = post_comment_el[1 if not url else 0]
            # Open comment section
            comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
            comment_button[0].click()

            # Get comments
            comments_el = self.browser.find_elements_by_css_selector(".comment")
            time.sleep(1.5)

            # 3rd comment - make sure the *show more* button is hidden
            self.assertIn("hidden", comments_el[2].find_element_by_class_name("show-more").get_attribute("class"))
            # 4th comment - make sure the *show more* button is not hidden
            self.assertNotIn("hidden", comments_el[3].find_element_by_class_name("show-more").get_attribute("class"))

        # Test the **following view**
        # Create a short text comment (new_user)
        Comment.objects.create(user=new_user, post=post, content="new user comment")
        time.sleep(1.5)
        # Creat a long text comment (new_user)
        Comment.objects.create(user=new_user, post=post, content=("Lorem ipsum" * 200))

        # Go to the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Get comments
        comments_el = self.browser.find_elements_by_class_name("comment")
        time.sleep(0.5)
        # 1st comment - make sure the *show more* button is not hidden
        self.assertIn("hidden", comments_el[0].find_element_by_class_name("show-more").get_attribute("class"))
        # 2nd comment - make sure the *show more* button is hidden
        self.assertNotIn("hidden", comments_el[1].find_element_by_class_name("show-more").get_attribute("class"))

    def test_frontend_index_like_comment(self):
        """ Try to like a comment using like-button -> check if new like exists and data-count, like-counter values are correct """
        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()
        time.sleep(0.5)
        # Get a comment
        comment_el = post_comment_el.find_elements_by_class_name("comment")[0]
        time.sleep(0.5)
        # Perform the test
        self.like_panel_test(self.user, comment_el)

    def test_frontend_user_profile_like_comment(self):
        """ Try to like a comment using like-button -> check if new like exists and data-count, like-counter values are correct """
        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()
        time.sleep(0.5)

        # Get a comment
        comment_el = post_comment_el.find_elements_by_class_name("comment")[0]
        time.sleep(0.5)
        # Perform the test
        self.like_panel_test(self.user, comment_el)

    def test_frontend_following_like_comment(self):
        """ Try to like a comment using like-button -> check if new like exists and data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        post = Post.objects.create(user=new_user, content="Lorem ipsum")
        # Creat a comment
        Comment.objects.create(user=new_user, post=post, content="comment")


        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()
        time.sleep(0.5)

        # Get a comment
        comment_el = post_comment_el.find_elements_by_class_name("comment")[0]
        time.sleep(0.5)
        # Perform the test
        self.like_panel_test(self.user, comment_el)

    def test_frontend_index_change_like_comment(self):
        """ Try to change a like on a comment -> check if new emojie exists and data-count, like-counter values are correct """
        # Comment to like
        comment = Comment.objects.get(user=self.user, content="comment 0")
        # Create a like
        Like.objects.create(user=self.user, comment=comment, emoji_type=1)

        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()
        time.sleep(3)
        
        # Get a comment
        comment_el = post_comment_el.find_elements_by_class_name("comment")[0]
        time.sleep(0.5)
        # Perform the test
        self.like_panel_test(self.user, comment_el)

    def test_frontend_user_profile_change_like_comment(self):
        """ Try to change a like on a comment -> check if new emojie exists and data-count, like-counter values are correct """
        # Comment to like
        comment = Comment.objects.get(user=self.user, content="comment 0")
        # Create a like
        Like.objects.create(user=self.user, comment=comment, emoji_type=1)

        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()
        time.sleep(3)
        # Get a comment
        comment_el = post_comment_el.find_elements_by_class_name("comment")[0]
        # Perform the test
        self.like_panel_test(self.user, comment_el)

    def test_frontend_following_change_like_comment(self):
        """ Try to change a like on a comment -> check if new emojie exists and data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        post = Post.objects.create(user=new_user, content="Lorem ipsum")
        # Creat a comment
        comment = Comment.objects.create(user=new_user, post=post, content="comment")
        # Create a like
        Like.objects.create(user=self.user, comment=comment, emoji_type=1)

        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el = self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()
        time.sleep(3)
        # Get a comment
        comment_el = post_comment_el.find_elements_by_class_name("comment")[0]
        # Perform the test
        self.like_panel_test(self.user, comment_el)

    def test_frontend_index_like_emoji_twice_comment(self):
        """ Liking one comment with the same emoji twice -> check if data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")

        # Comment to like
        comment = Comment.objects.get(user=self.user, content="comment 0")
        # Create likes
        Like.objects.create(user=self.user, comment=comment, emoji_type=2)
        Like.objects.create(user=new_user, comment=comment, emoji_type=2)

        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Check if the emoji has data-count = 2
        comment_el = self.browser.find_elements_by_css_selector(".comment")[0]
        emoji_el = comment_el.find_element_by_css_selector("ul.emoji-list i[data-name='dislike']")
        time.sleep(2)
        like_counter_el = comment_el.find_element_by_css_selector(".like-data .like-counter")

        self.assertEqual(emoji_el.get_attribute("data-count"), "2")

        # Check if the like-counter = 1
        self.assertEqual(like_counter_el.text, "+1")

    def test_frontend_user_profile_like_emoji_twice_comment(self):
        """ Liking one comment with the same emoji twice -> check if data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Comment to like
        comment = Comment.objects.get(user=self.user, content="comment 0")
        # Create likes
        Like.objects.create(user=self.user, comment=comment, emoji_type=2)
        Like.objects.create(user=new_user, comment=comment, emoji_type=2)

        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Check if the emoji has data-count = 2
        comment_el = self.browser.find_elements_by_css_selector(".comment")[0]
        emoji_el = comment_el.find_element_by_css_selector("ul.emoji-list i[data-name='dislike']")
        time.sleep(2)
        like_counter_el = comment_el.find_element_by_css_selector(".like-data .like-counter")

        self.assertEqual(emoji_el.get_attribute("data-count"), "2")

        # Check if the like-counter = 1
        self.assertEqual(like_counter_el.text, "+1")

    def test_frontend_following_like_emoji_twice_comment(self):
        """ Liking one comment with the same emoji twice -> check if data-count, like-counter values are correct """
        # Create a second user
        new_user = User.objects.create_user(username="1", password="1")
        # Follow the user
        Following.objects.create(user=self.user, user_followed=new_user)
        # Creat a post
        post = Post.objects.create(user=new_user, content="Lorem ipsum")
        # Creat a comment
        comment = Comment.objects.create(user=new_user, post=post, content="comment")
        # Create likes
        Like.objects.create(user=self.user, comment=comment, emoji_type=2)
        Like.objects.create(user=new_user, comment=comment, emoji_type=2)

        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Check if the emoji has data-count = 2
        comment_el = self.browser.find_elements_by_css_selector(".comment")[0]
        emoji_el = comment_el.find_element_by_css_selector("ul.emoji-list i[data-name='dislike']")
        time.sleep(2)
        like_counter_el = comment_el.find_element_by_css_selector(".like-data .like-counter")

        self.assertEqual(emoji_el.get_attribute("data-count"), "2")

        # Check if the like-counter = 1
        self.assertEqual(like_counter_el.text, "+1")

    def test_frontend_index_emoji_correct_order_comment(self):
        """ Make sure that emoji with most likes is first """
        # Create a second user
        second_user = User.objects.create_user(username="1", password="1")
        # Create a third user
        third_user = User.objects.create_user(username="2", password="2")
        # Comment to like
        comment = Comment.objects.get(user=self.user, content="comment 0")
        # Create likes
        Like.objects.create(user=self.user, comment=comment, emoji_type=1)
        Like.objects.create(user=second_user, comment=comment, emoji_type=3)
        Like.objects.create(user=third_user, comment=comment, emoji_type=3)

        # Login the user
        self.login_quick()
        # Get the index view
        self.browser.get(self.live_server_url)
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Check if smile emoji is first and like emoji is second
        comment_el = self.browser.find_elements_by_css_selector(".comment")[0]
        emoji_list_el = comment_el.find_elements_by_css_selector("ul.emoji-list > i")

        self.assertEqual(emoji_list_el[0].get_attribute("data-name"), "smile")
        self.assertEqual(emoji_list_el[1].get_attribute("data-name"), "like")

    def test_frontend_user_profile_emoji_correct_order_comment(self):
        """ Make sure that emoji with most likes is first """
        # Create a second user
        second_user = User.objects.create_user(username="1", password="1")
        # Create a third user
        third_user = User.objects.create_user(username="2", password="2")
        # Comment to like
        comment = Comment.objects.get(user=self.user, content="comment 0")
        # Create likes
        Like.objects.create(user=self.user, comment=comment, emoji_type=1)
        Like.objects.create(user=second_user, comment=comment, emoji_type=3)
        Like.objects.create(user=third_user, comment=comment, emoji_type=3)

        # Login the user
        self.login_quick()
        # Get the user-profile view
        self.browser.get(self.live_server_url + f"/user-profile/{self.user.id}")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Check if smile emoji is first and like emoji is second
        comment_el = self.browser.find_elements_by_css_selector(".comment")[0]
        emoji_list_el = comment_el.find_elements_by_css_selector("ul.emoji-list > i")

        self.assertEqual(emoji_list_el[0].get_attribute("data-name"), "smile")
        self.assertEqual(emoji_list_el[1].get_attribute("data-name"), "like")

    def test_frontend_following_emoji_correct_order_comment(self):
        """ Make sure that emoji with most likes is first """
        # Create a second user
        second_user = User.objects.create_user(username="1", password="1")
        # Create a third user
        third_user = User.objects.create_user(username="2", password="2")
        # Follow the second user
        Following.objects.create(user=self.user, user_followed=second_user)
        # Creat a post
        post = Post.objects.create(user=second_user, content="Lorem ipsum")
        # Creat a comment
        comment = Comment.objects.create(user=second_user, post=post, content="comment")
        # Create likes
        Like.objects.create(user=self.user, comment=comment, emoji_type=1)
        Like.objects.create(user=second_user, comment=comment, emoji_type=3)
        Like.objects.create(user=third_user, comment=comment, emoji_type=3)

        # Login the user
        self.login_quick()
        # Get the following view
        self.browser.get(self.live_server_url + "/following")
        # Get the post-comment element
        post_comment_el =  self.browser.find_elements_by_css_selector(".post-comment-element")[0]
        # Open comment section
        comment_button = post_comment_el.find_elements_by_css_selector(".post .comment-button")
        comment_button[0].click()

        # Check if smile emoji is first and like emoji is second
        comment_el = self.browser.find_elements_by_css_selector(".comment")[0]
        emoji_list_el = comment_el.find_elements_by_css_selector("ul.emoji-list > i")

        self.assertEqual(emoji_list_el[0].get_attribute("data-name"), "smile")
        self.assertEqual(emoji_list_el[1].get_attribute("data-name"), "like")
