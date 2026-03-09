from django.db import models
from django.contrib.auth.models import User
from .category import Category


class Note(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='notes')
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title
