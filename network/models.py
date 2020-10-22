from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    # Model fields
    # auto: post-id
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="posted by")
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True, null=True, verbose_name="posted on")

    # Model naming
    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
    
    def __str__(self):
        return f"Post {self.id} made by {self.user} on {self.date}"