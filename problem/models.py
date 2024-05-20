from django.db import models
import datetime
from django.utils import timezone

from user.models import *

def now():
    return timezone.now()

class Problem(models.Model):
    facility = models.ForeignKey(Facility, on_delete = models.CASCADE, null = True)
    creator = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 255)
    type = models.CharField(max_length = 16)
    statement = models.TextField(max_length = 4096)
    answer = models.TextField(max_length = 4096)
    date = models.DateTimeField(default = now)

class Solution(models.Model):
    creator = models.ForeignKey(User, on_delete = models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete = models.CASCADE)
    content = models.TextField(max_length = 4096)
    score = models.FloatField(null = True)
    date = models.DateTimeField(default = now)

class SlnComment(models.Model):
    solution = models.ForeignKey(Solution, null = True, on_delete = models.CASCADE)
    author = models.ForeignKey(User, on_delete = models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField(default = now)