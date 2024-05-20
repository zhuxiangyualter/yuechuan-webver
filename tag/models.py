from django.db import models
from problem.models import  Problem
from zone.models import Post
from user.models import User

class Tag(models.Model):
    text = models.TextField(max_length=10)
    problems = models.ManyToManyField(Problem)
    post = models.ManyToManyField(Post)
    user = models.ManyToManyField(User)

class UserTagWeight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    weight = models.IntegerField('weight', default=0)