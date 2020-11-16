from django.contrib.auth.models import AbstractUser
from django.db import models
from .util import resize_image

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
    image = models.ImageField(default="profile_pics/default.png", upload_to="profile_pics")

    def __str__(self):
        return f"{self.user.username}"

    def save(self, *args, **kwargs): 
        super().save(*args, **kwargs)
        resize_image(self.image.path, 600, 600)

class Post(models.Model):
    # Model fields
    # auto: post-id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="posted by", related_name="posts")
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, null=False, blank=True, verbose_name="posted on")

    # Model naming
    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
  
    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date.strftime('%d %b %Y %H:%M:%S')}"

    

class Comment(models.Model):
    # Model fields
    # auto: comment-id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="commented by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, null=False, blank=True, verbose_name="commented on")

    # Model naming
    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"
        ordering = ["-date"]
    
    def __str__(self):
        return f"Comment {self.id} made by {self.user} on post {self.post_id} on {self.date.strftime('%d %b %Y %H:%M:%S')}"


class Like(models.Model):

    # Emojis - choices
    LIKE_TYPE_CHOICES = [
        (1, "like"),
        (2, "dislike"),
        (3, "smile"),
        (4, "heart"),
        (5, "thanks")
    ]

    # Model fields
    # auto: like id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="liked by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    emoji_type = models.IntegerField(choices=LIKE_TYPE_CHOICES, default=1)

    # Model naming
    class Meta:
        verbose_name = "like"
        verbose_name_plural = "likes"
        unique_together = [["user", "post"], ["user", "comment"]]
        ordering = ["emoji_type"]

    def __str__(self):
        element = self.post if (self.post is not None) else self.comment
        return f"Like {self.id} by {self.user} on object {element}"


class Following(models.Model):
    # Model fields
    # auto: following id
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    user_followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers" )

    class Meta:
        verbose_name = "following"
        verbose_name_plural = "followings"
        unique_together = ['user', 'user_followed']

    def __str__(self):
        return f"{self.user} is following {self.user_followed}"

    # Get all posts from users that current user follows
    def get_user_followed_posts(self):
        return self.user_followed.posts.order_by("-date").all()
    
