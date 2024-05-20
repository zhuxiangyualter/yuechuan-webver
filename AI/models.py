from django.db import models
from django.utils import timezone
from django.utils.deconstruct import deconstructible
import os
from user.models import User

@deconstructible
class Rename(object):
    def __init__(self, path: str):
        self.path = path

    def __call__(self, inst, name: str):
        ext = name.split('.')[-1]
        filename = f'{inst.pk}.{ext}'
        return os.path.join(self.path, filename)

def now():
    return timezone.now()

class SlideGeneration(models.Model):
    creator = models.ForeignKey(User, on_delete = models.CASCADE)
    date = models.DateTimeField(default = now)
    prompt = models.TextField(max_length = 4096)
    remote_id = models.CharField(max_length = 256)
    cover = models.ImageField(null = True, upload_to=Rename('ai/slides/cover/'))
    title = models.CharField(max_length = 256)
    subtitle = models.CharField(max_length = 256)
    result = models.FileField(null = True, upload_to=Rename('ai/slides/'))
    status = models.CharField(max_length = 16, default = 'pending')