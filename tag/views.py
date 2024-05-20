from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden, HttpRequest, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import Tag

@login_required(login_url = 'user:login')
def tag(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'tag/tag.html', {
            'tags': Tag.objects.all()
        })