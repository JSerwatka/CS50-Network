from django.contrib import admin
from .models import User, Post, Comment

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    """Contains User model admin page config"""
    list_display = ("id", "username", "email", "password")

class PostAdmin(admin.ModelAdmin):
    """Contains Post model admin page config"""
    list_display = ("id", "user", "content", "date")

class CommentAdmin(admin.ModelAdmin):
    """Contains Comment model admin page config"""
    list_display = ("id", "user", "post_id", "content", "date")


admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)