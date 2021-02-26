import json
from itertools import chain

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from .models import User, Post, Comment, Like, Following, UserProfile
from .forms import CreatePostForm, CreateCommentForm, CreateUserProfileForm

#TODO: custom 404 page

def index(request):
    """ View: Show all posts """

    # Get all posts
    all_posts = Post.objects.order_by("-date").all()

    # Create page controll
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "post_form": CreatePostForm(),
        "comment_form": CreateCommentForm(auto_id=False),
        "page_obj": page_obj,
        "add_post_available": True
    })

@login_required(login_url="network:login")
def post_comment(request, action):
    """ View: Controls saving a new post/comment (only POST) """

    # Get not allowed
    if request.method == "GET":
        return HttpResponse(status=405)

    if request.method == "POST":
        if action == "post":
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
        elif action == "comment":
            form = CreateCommentForm(request.POST)

            if form.is_valid():
                # Get all data from the form
                content = form.cleaned_data["content"]

                # Get commented post
                try:
                    post = Post.objects.get(pk=request.POST.get('postId'))
                except Post.DoesNotExist:
                    return HttpResponse(status=404)

                # Save the record
                comment = Comment(
                    user = User.objects.get(pk=request.user.id),
                    content = content,
                    post = post
                )
                comment.save()

        # Go back to the place from which the request came
        return HttpResponseRedirect(request.headers['Referer'])

    if request.method == "PUT":
        body = json.loads(request.body)
        # Query for requested post - make sure
        # that current user is the author
        try:
            if action == "post":
                object_to_edit = Post.objects.get(pk=body.get('id'), user=request.user)
            else:
                object_to_edit = Comment.objects.get(pk=body.get('id'), user=request.user)
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return JsonResponse({
                "error": _("Post or Comment does not exist")
            }, status=404)

        # Update post's content
        object_to_edit.content = body.get('content')
        object_to_edit.save()

        # Return positive response
        return HttpResponse(status=201)

    if request.method == "DELETE":
        body = json.loads(request.body)
        # Query for requested post - make sure
        # that current user is the author
        try:
            if action == "post":
                object_to_delete = Post.objects.get(pk=body.get('id'), user=request.user)
            else:
                object_to_delete = Comment.objects.get(pk=body.get('id'), user=request.user)
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return JsonResponse({
                "error": _("Post or Comment does not exist")
            }, status=404)

        # Delete the post and refresh the page
        object_to_delete.delete()
        return HttpResponse(status=204)

@login_required(login_url="network:login")
def user_profile(request, user_id):
    """ View: Shows requested user profile and the user's posts """

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
        "page_obj": page_obj,
        "comment_form": CreateCommentForm(auto_id=False)
    })

@login_required(login_url="network:login")
def edit_profile(request):
    """ View: Controls editing of user profile's data """

    if request.method == "POST":
        # Cancel edit -> go back to the profile
        if request.POST.get("cancel") == "clicked":
            return HttpResponseRedirect(reverse(
                    "network:user-profile",
                    args=[request.user.id]
                ))

        # Submit edit -> update profile
        form = CreateUserProfileForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            # Get current user's profile
            new_profile = UserProfile.objects.get(user=request.user.id)

            # Update all profile's data with form's data
            new_profile.name = form.cleaned_data.get("name")
            new_profile.date_of_birth = form.cleaned_data.get("date_of_birth")
            new_profile.about = form.cleaned_data.get("about")
            new_profile.country = form.cleaned_data.get("country")
            # Update image only if any file was uploaded
            if len(request.FILES) == 1:
                new_profile.image = request.FILES['image']

            # Save changes
            new_profile.save()

            # Go back to user's profile page
            return HttpResponseRedirect(reverse(
                    "network:user-profile",
                    args=[request.user.id]
                ))
        else:
            # If form invalid - load edit-profile with error info
            return render(request, "network/edit_profile.html", {
                "form": form,
                "max_file_size": settings.MAX_UPLOAD_SIZE
            })

    return render(request, "network/edit_profile.html", {
        "form": CreateUserProfileForm(instance=request.user.profile),
        "max_file_size": settings.MAX_UPLOAD_SIZE
    })

@login_required(login_url="network:login")
def like(request, action, action_id):
    """ View: Controls all actions regarding liking """

    if request.method == "GET":
        # Check if like exists and send back info
        try:
            if action == "post":
                post = Post.objects.get(pk=action_id)
                like_obj = Like.objects.get(user=request.user, post=post)
            elif action == "comment":
                comment = Comment.objects.get(pk=action_id)
                like_obj = Like.objects.get(user=request.user, comment=comment)
            else:
                return JsonResponse({
                    "error": _("Unknown action - you can only like post or comment")
                }, status=400)
        except Like.DoesNotExist:
            return JsonResponse({
                "like": "False"
            }, status=200)
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return JsonResponse({
                "error": _("Post or Comment does not exist")
            }, status=404)
        # if like exists send emojiType text
        else:
            return JsonResponse({
                "like": "True",
                "emojiType": [emoji_tuple[1] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[0] == like_obj.emoji_type][0]
            }, status=200)
        # Something went wrong
        return JsonResponse({
                "error": _(f"Unknown error during GET {action} like ")
        }, status=400)

    elif request.method == "POST":
        body = json.loads(request.body)
        emoji_type = [emoji_tuple[0] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[1] == body['emojiType']][0]

        try:
            if action == "post":
                post = Post.objects.get(pk=action_id)
                like_obj = Like(user=request.user, post=post, emoji_type=emoji_type)
            elif action == "comment":
                comment = Comment.objects.get(pk=action_id)
                like_obj = Like(user=request.user, comment=comment, emoji_type=emoji_type)
            else:
                return JsonResponse({
                    "error": _("Unknown action - you can only like post or comment")
                }, status=400)
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return JsonResponse({
                "error": _("Post or Comment does not exist")
            }, status=404)

        like_obj.save()
        return HttpResponse(status=201)

    elif request.method == "PUT":
        body = json.loads(request.body)
        emoji_number = [emoji_tuple[0] for emoji_tuple in Like.LIKE_TYPE_CHOICES if emoji_tuple[1] == body['emojiType']][0]
        try:
            if action == "post":
                post = Post.objects.get(pk=action_id)
                old_like = Like.objects.get(user=request.user, post=post)
            elif action == "comment":
                comment = Comment.objects.get(pk=action_id)
                old_like = Like.objects.get(user=request.user, comment=comment)
            else:
                return JsonResponse({
                    "error": _("Unknown action - you can only like post or comment")
                }, status=400)
        except (Post.DoesNotExist, Comment.DoesNotExist):
            return JsonResponse({
                "error": _("Post or Comment does not exist")
            }, status=404)

        # Update emoji only if it's different
        if old_like.emoji_type != emoji_number:
            old_like.emoji_type = emoji_number
            old_like.save()

        return HttpResponse(status=201)

@login_required(login_url="network:login")
def following(request):
    """ View: Show users' posts that current user follows"""

    current_user = User.objects.get(pk=request.user.id)

    # Get all posts from users that current user follows
    posts = [users.get_user_followed_posts() for users in current_user.following.all()]

    # Flatten 2d array to 1d array
    posts = list(chain(*posts))

    # Create page controll
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "form": None,
        "comment_form": CreateCommentForm(auto_id=False),
        "page_obj": page_obj,
        "add_post_available": False
    })

@login_required(login_url="network:login")
def follow_unfollow(request, user_id):
    """ View: Controls following/unfollowing users (only POST) """
    # GET method is not allowed
    if request.method == "GET":
        return HttpResponse(status=405)
    # Nested try/except helps to reduce db queries by one
    if request.method == "POST":
        try:
            get_follow_obj = Following.objects.get(user=request.user.id, user_followed=user_id)
        except Following.DoesNotExist:
            try:
                user_to_follow = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return HttpResponse(status=404)
            else:
                new_follow_obj = Following(user=request.user, user_followed=user_to_follow)
                new_follow_obj.save()
        else:
            get_follow_obj.delete()

        return HttpResponseRedirect(reverse("network:user-profile", args=[user_id]))

def login_view(request):
    """ View: Controls logging in """

    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)

            # If user tried to enter login_required page - go there after login
            if "next" in request.POST:
                request_args =  request.POST.get("next")[1:].split('/')
                return HttpResponseRedirect(reverse(
                        "network:" + request_args[0], args=request_args[1:]
                       ))
            else:
                return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html", {
                "message": _("Invalid username and/or password.")
            })
    else:
        # Show login panel only for not login users
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/login.html")


def logout_view(request):
    """ View: Controls logging out """

    logout(request)
    return HttpResponseRedirect(reverse("network:index"))


def register(request):
    """ View: Controls registration """

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure no blank fields
        if  (not username) or (not email) or (not password):
            return render(request, "network/register.html", {
                "message": _("You must fill out all fields.")
            })
        # Ensure password matches confirmation
        elif password != confirmation:
            return render(request, "network/register.html", {
                "message": _("Passwords must match.")
            })

        # Attempt to create new user and its profile
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": _("Username already taken.")
            })
        login(request, user)
        return HttpResponseRedirect(reverse("network:index"))
    else:
        # Show register panel only for not login users
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("network:index"))
        else:
            return render(request, "network/register.html")
