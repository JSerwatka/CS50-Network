from django.contrib import admin
from .models import User, Post, Comment, Like, UserProfile, Following

# Register your models here.
class UserProfileAdmin(admin.TabularInline):
    """Creates an inline for UserProfile to hook it to User admin page"""
    model = UserProfile

class UserAdmin(admin.ModelAdmin):
    """Contains User model admin page config + UserProfile hooked"""
    list_display = ("id", "username", "email", "password")
    # Hook UserProfile to User admin page
    inlines = [UserProfileAdmin]


class PostAdmin(admin.ModelAdmin):
    """Contains Post model admin page config"""
    list_display = ("id", "user", "content", "date")

class CommentAdmin(admin.ModelAdmin):
    """Contains Comment model admin page config"""
    list_display = ("id", "user", "post", "content", "date")

class LikeAdmin(admin.ModelAdmin):
    """Contains Like model admin page config"""
    list_display = ("id", "user", "post", "comment")

admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Following)
