from django.db import models
import datetime
from django.utils import timezone

from user.models import *
from django.conf import settings

def now():
    return timezone.now()

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length = 255, default = '')
    content = models.TextField()
    facility = models.ForeignKey(Facility, on_delete = models.CASCADE, null = True)
    date = models.DateTimeField(default = now)

class Comment(models.Model):
    post = models.ForeignKey(Post, null = True, on_delete = models.CASCADE)
    author = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.TextField()
    reply = models.ForeignKey('self', null = True, on_delete = models.CASCADE)
    date = models.DateTimeField(default = now)


