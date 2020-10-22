from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

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
        return f"Post {self.id} made by {self.user} on {self.date}"

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
        return f"Comment {self.id} made by {self.user} on post {self.post_id} on {self.date}"

class Like(models.Model):
    # Model fields
    # auto: like id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="liked by")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes", null=True, blank=True)

    # Model naming
    class Meta:
        verbose_name = "like"
        verbose_name_plural = "likes"

    def __str__(self):
        element = self.post if (self.post is not None) else self.comment

        return f"Like {self.id} by {self.user} on object {element}"
