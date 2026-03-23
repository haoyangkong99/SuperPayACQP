"""
User Model
"""
from django.db import models


class User(models.Model):
    """
    User model for SuperPayACQP
    """
    userId = models.TextField(primary_key=True)
    name = models.TextField()
    email = models.TextField(unique=True)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.name
