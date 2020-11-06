import json
import numpy as np

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import User, Post, Comment, Like, Following, UserProfile

#TODO: add change userprofile info settings

class CreatePostForm(forms.ModelForm):
    content = forms.CharField(label="Description", widget=forms.Textarea(attrs={
                                    'placeholder': "What are you thinking about?",
                                    'autofocus': 'autofocus',
                                    'rows': '3',
                                    'class': 'form-control',
                                    'aria-label': "post content"
                             }))

    class Meta:
        model = Post
        fields = ["content"]

# TODO: page query variable greater than max pages handle
def index(request):
    if request.method == "POST":
        form = CreatePostForm(request.POST)
        if form.is_valid():
            # Get all data from the form
            content = form.cleaned_data["content"]

            # Save the record
            post = Post(
                user = User.objects.get(pk=request.user.id),
                content = content
            )
            post.save()

    if request.method == "PUT":
        body = json.loads(request.body)
        # Query for requested post - make sure
        # that current user is the author
        try:
            post_to_edit = Post.objects.get(pk=body.get('id'), user=request.user)
        except Post.DoesNotExist: 
            return HttpResponse(status=404)

        # Update post's content
        post_to_edit.content = body.get('content')
        post_to_edit.save()

        # Return positive response
        return HttpResponse(status=204)

    # Get all posts
    all_posts = Post.objects.order_by("-date").all()

    # Create page controll
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "form": CreatePostForm(),
        "page_obj": page_obj,
        "add_post_available": True
    })

@login_required(login_url="network:login")
def user_profile(request, user_id):
    user_data = User.objects.get(pk=user_id)
    posts = user_data.posts.order_by("-date").all()

    # Get following and followed user objects
    following_id_list = Following.objects.filter(user=user_id).values_list('user_followed', flat=True)
    followers_id_list = Following.objects.filter(user_followed=user_id).values_list('user_id', flat=True)

    following_user_list = User.objects.filter(id__in=following_id_list)
    followers_user_list = User.objects.filter(id__in=followers_id_list)

    # Create page controll
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/user_profile.html", {
        "user_data": user_data,
        "following": following_user_list,
        "followers": followers_user_list,
        "page_obj": page_obj
    })

@login_required(login_url="network:login")
def like(request, action, action_id):
    if request.method == "GET":
        # Check if like exists and send back info
        try:
            post = Post.objects.get(pk=action_id)
            like = Like.objects.get(user=request.user, post=post)
        except Like.DoesNotExist:
            return JsonResponse({
                "like": "False"
            }, status=201)  #TODO: update status code
        except Post.DoesNotExist:
             return HttpResponse(status=404) #TODO: redirect to error page
        # if like exists send emojiType text
        else:
            return JsonResponse({
                "like": "True",
                "emojiType": [emoji_tuple[1] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[0] == like.emoji_type][0]
            }, status=201)  #TODO: update status code
        # Something went wrong
        return HttpResponse(status=400) #TODO: update status code

    elif request.method == "POST":
        body = json.loads(request.body)
        emoji_type = [emoji_tuple[0] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[1] == body['emojiType']][0]

        if action == "post":
            post = Post.objects.get(pk=action_id)
            like = Like(user=request.user, post=post, emoji_type=emoji_type)
        elif action == "comment":
            comment = Comment.objects.get(pk=action_id)
            like = Like(user=request.user, comment=comment, emoji_type=emoji_type)
        else: 
            return HttpResponse(status=404)
            #TODO: corrent response 

        # TODO: like duplicate handling
        like.save()
        #TODO: corrent respons
        return HttpResponse(status=204)

    elif request.method == "PUT":
        body = json.loads(request.body)
        emoji_number = [emoji_tuple[0] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[1] == body['emojiType']][0]

        if action == "post":
            post = Post.objects.get(pk=action_id)
            old_like = Like.objects.get(user=request.user, post=post)
        elif action == "comment":
            comment = Comment.objects.get(pk=action_id)
            old_like = Like.objects.get(user=request.user, comment=comment)
        else:
            return HttpResponse(status=404)
            #TODO: corrent response 

        try:
            # Update emoji only if it's different
            if (old_like.emoji_type != emoji_number):
                old_like.emoji_type = emoji_number
                old_like.save()
        except:
            return HttpResponse(status=404) #TODO: corrent response 
        else:
            return HttpResponse(status=204) #TODO: corrent respons


@login_required(login_url="network:login")
def following(request):
    current_user = User.objects.get(pk=request.user.id)

    # Get all posts from users that current user follows
    posts = [users.get_user_followed_posts() for users in current_user.following.all()]
    # Flatten 2d array to 1d array
    posts = np.array(posts).flatten()

    # Create page controll
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "form": None,
        "page_obj": page_obj,
        "add_post_available": False
    })

@login_required(login_url="network:login")
def follow_unfollow(request, user_id):
    # Nested try/except helps to reduce db queries by one
    #TODO: redirect back to profile
    if request.method == "POST":
        try:
            get_follow_obj = Following.objects.get(user=request.user.id, user_followed=user_id)
        except Following.DoesNotExist:
            try:
                user_to_follow = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return HttpResponse(status=404) #TODO: render error msg
            else:
                new_follow_obj = Following(user=request.user, user_followed=user_to_follow)
                new_follow_obj.save()
        else:
            get_follow_obj.delete()
        finally:
            HttpResponse(status=201) #TODO: render error msg

    return HttpResponse(f"Current user: {request.user}, profile: {user_id}")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # If user tried to enter login_required page - go there after login
            print(request.POST)
            
            if "next" in request.POST:
                request_args =  request.POST.get("next")[1:].split('/')
                print(request_args[0])
                print(request_args[1:])
                return HttpResponseRedirect(reverse("network:" + request_args[0], args=request_args[1:]))
            else:
                return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")

@login_required(login_url="network:login")
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user and its profile
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        else:
            profile = UserProfile(user=user)
            profile.save()
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        return render(request, "network/register.html")
