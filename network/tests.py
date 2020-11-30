from django.test import TestCase, Client
from django.contrib import auth
from django.conf import settings
from django.db import IntegrityError

from selenium import webdriver
import json


from .models import *

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
    # TODO
    pass

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

    def test_index_posts_order(self):
        """ Make sure page object has posts in correct order (from newest to oldest) """
        post_1 = Post.objects.create(user=self.user, content="test")
        post_2 = Post.objects.create(user=self.user, content="test_2")

        response = self.c.get('/')
        # Get post list
        post_list = response.context['page_obj'].object_list

        self.assertEqual(post_list[0].content, "test_2")
        self.assertEqual(post_list[1].content, "test")

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
        # Edit post's content
        response = self.c.put('/post-comment/comment', json.dumps({
            "id": old_comment.id,
            "content": "new content"
        }))
        # Get the comment after editing
        new_comment = Comment.objects.get(pk=old_comment.id)

        self.assertEqual(old_comment.content, "old content")
        self.assertEqual(new_comment.content, "new content")
        self.assertEqual(response.status_code, 201)

    # Post-comment view - DELETE
