from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from .models import *
from tag.models import *
from user.models import *
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from user.views import get_user_from_token
@permission_classes([IsAuthenticated])
def index(request):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    posts = Post.objects.filter(facility = user.facility).order_by('date')
    return Response(
        data = {
            "posts": posts,
        },
        status = 200
    )
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def new(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    post = Post.objects.create(
            author = user,
            title = request.POST['title'],
            content = request.POST['content'],
            facility = user.facility,
        )
    tags = request.POST['tag']
    tag_ls = tags.split(';')
    for t in tag_ls:
        ta = t.strip()
        if ta:
            tag = Tag.objects.filter(text=ta).first()
            if tag is not None:
                tag.post.add(post)
            else:
                tmpT = Tag.objects.create(text = ta)
                tmpT.post.add(post)
    post.save()
    return Response(
        status = 200
        ,data = {
            'data': {
            "post": post.id
            }
        }
        )
@permission_classes([IsAuthenticated])
def view(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    post = Post.objects.get(id = id)

    if request.method == 'GET':
        comments = Comment.objects.filter(post = post)

        if post is None:
            return Response(
                status = 404
            )
        return Response(
            status = 200
            ,data = {
                'data': {
                "post": post,
                "comments": comments
                },
                'message':"success"
            }
        )
    elif request.method == 'POST':
        comment = Comment.objects.create(
            author = user,
            post = post,
            reply = Comment.objects.get(id = int(request.POST['reply'])) if request.POST['reply'] else None,
            content = request.POST['comment']
        )
        comment.save()
        return Response(
            status = 200
            ,data = {
                'data': {
                "id": id
                }
                ,'message':"success"
            }
        )