from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from .models import *
from tag.models import *

@login_required(login_url='user:login')
def index(request):
    posts = Post.objects.filter(facility = request.user.facility).order_by('date')
    return render(request, 'zone/index.html', {
        "posts": posts,
    })
    
@login_required(login_url='user:login')
def new(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'zone/new.html')
    elif request.method == 'POST':
        post = Post.objects.create(
            author = request.user,
            title = request.POST['title'],
            content = request.POST['content'],
            facility = request.user.facility,
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
        return redirect('zone:view', post.id)

@login_required(login_url='user:login')
def view(request: HttpRequest, id: int):
    post = Post.objects.get(id = id)

    if request.method == 'GET':
        comments = Comment.objects.filter(post = post)

        if post is None:
            return render(request, '404.html')

        return render(request, 'zone/view.html', {
            'post': post,
            'comments': comments
        })
    elif request.method == 'POST':
        comment = Comment.objects.create(
            author = request.user,
            post = post,
            reply = Comment.objects.get(id = int(request.POST['reply'])) if request.POST['reply'] else None,
            content = request.POST['comment']
        )

        comment.save()
        return redirect('zone:view', id)