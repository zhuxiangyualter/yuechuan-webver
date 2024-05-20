import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.deconstruct import deconstructible
import random
from random import randbytes

@deconstructible
class Rename(object):
    def __init__(self, path: str):
        self.path = path

    def __call__(self, inst, name: str):
        ext = name.split('.')[-1]
        filename = f'{inst.username}.{ext}'
        return os.path.join(self.path, filename)

def new_invitation_code():
    return random.randint(100000000, 999999999)

def new_secret():
    return randbytes(8).hex().upper()

class Facility(models.Model):
    name = models.CharField('name', max_length = 255)
    invitation_code = models.IntegerField('invitation code', default=new_invitation_code, unique=True)
    secret = models.CharField(max_length = 16, default = new_secret)

class User(AbstractUser):
    username = models.CharField('username', max_length = 10 , unique = True)
    avatar = models.ImageField('avatar', upload_to = Rename('user/avatar/'), default='user/avatar/default_avatar.jpg')
    user_role = [
        ('student', 'student'),
        ('teacher', 'teacher'),
    ]
    title = models.CharField('title', max_length = 7, default = '普通用户')
    role = models.CharField('role', max_length=16, choices=user_role, default='student')
    facility = models.ForeignKey(Facility, on_delete = models.CASCADE, null=True)
