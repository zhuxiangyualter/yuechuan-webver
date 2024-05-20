from django.db import models
from problem.models import  Problem
from django.utils.timezone import now
from user.models import *

class Paper(models.Model):
    facility = models.ForeignKey(Facility, on_delete = models.CASCADE, null = True)
    title = models.TextField(max_length=10)
    date = models.DateTimeField(default = now)

class PaperProblem(models.Model):
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    raw = models.ForeignKey(Problem, on_delete=models.CASCADE)
    score = models.IntegerField('problemScore', default=10)

class Submission(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)

class Answer(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, null=True)
    problem = models.ForeignKey(PaperProblem, on_delete=models.CASCADE)
    answer = models.CharField('answer', max_length=4096, default="未作答")
    score = models.IntegerField('markScore', default=0)
    date = models.DateTimeField(default = now)