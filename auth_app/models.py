from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """User model with name field for username"""
    name = models.CharField(max_length=30, unique=True)
    username = None
    password = models.CharField(max_length=30)

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []


class Message(models.Model):
    """Message model for text messages from user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
