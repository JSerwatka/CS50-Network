from django.contrib.auth.models import AbstractUser
from django.db import models

from django_countries.fields import CountryField
# django countries from https://pypi.org/project/django-countries/

class User(AbstractUser):
    pass

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    image = models.ImageField(default="profile_pics/default.png", upload_to="profile_pics", blank=True)

    def __str__(self):
        return f"{self.user.username}"

class Post(models.Model):
    # Model fields
    # auto: post-id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="posted by", related_name="posts")
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, null=True, verbose_name="posted on")

    # Model naming
    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
    
    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"

    #TODO: give only part of content followed by ... method (czytaj dalej option, which shows more content)

class Comment(models.Model):
    # Model fields
    # auto: comment-id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="commented by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, null=True, verbose_name="commented on")

    # Model naming
    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
    
    def __str__(self):
        return f"Comment {self.id} made by {self.user} on post {self.post_id} on {self.date.strftime('%d %b %Y %H:%M:%S')}"

    #TODO: give only part of content followed by ... method (czytaj dalej option, which shows more content)


class Like(models.Model):

    # Emojis - choices
    LIKE = "like"
    DISLIKE = "dislike"
    SMILE = "smile"
    HEART = "heart"
    THANKS = "thanks"
    LIKE_TYPE_CHOICES = [
        (LIKE, '<i class="em em---1" aria-role="presentation" aria-label="THUMBS UP SIGN"></i>'),
        (DISLIKE, '<i class="em em--1" aria-role="presentation" aria-label="THUMBS DOWN SIGN"></i>'),
        (SMILE, '<i class="em em-smile" aria-role="presentation" aria-label="SMILING FACE WITH OPEN MOUTH AND SMILING EYES"></i>'),
        (HEART, '<i class="em em-heart" aria-role="presentation" aria-label="HEAVY BLACK HEART"></i>'),
        (THANKS, '<i class="em em-bouquet" aria-role="presentation" aria-label="BOUQUET"></i>')
    ]

    # Model fields
    # auto: like id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="liked by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    emoji_type = models.CharField(max_length=10, choices=LIKE_TYPE_CHOICES, default=LIKE)

    # Model naming
    class Meta:
        verbose_name = "like"
        verbose_name_plural = "likes"

    def __str__(self):
        element = self.post if (self.post is not None) else self.comment
        return f"Like {self.id} by {self.user} on object {element}"


class Following(models.Model):
    # Model fields
    # auto: following id
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user_following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers" )


    class Meta:
        verbose_name = "following"
        verbose_name_plural = "followings"

    def __str__(self):
        return f"{self.user} is followed by {self.user_following}"
