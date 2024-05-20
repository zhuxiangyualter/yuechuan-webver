from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.http.request import HttpRequest
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from .models import *
from paper.models import *
from tag.models import *
from wordcloud import WordCloud
from django.db.models import Q, Count, Max, F
from datetime import timedelta
from io import BytesIO
import json
from django.utils.timezone import now


def register(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'user/register.html')
    elif request.method == 'POST':
        if request.POST['password'] != request.POST['confirm-password']:
            return render(request, 'user/register.html', {
                'error_message': '密码不匹配'
            })
        
        if User.objects.filter(username = request.POST['username']).count():
            return render(request, 'user/register.html', {
                'error_message': '用户名已存在'
            })
        
        invitation = request.POST['invitation-code']
        secret = request.POST['auth-secret']

        user = User.objects.create_user(
            username = request.POST['username'],
            password = request.POST['password'],
        )
        
        if invitation:
            facility = Facility.objects.filter(invitation_code=request.POST['invitation-code'])

            if facility.count() == 0:
                try:
                    User.objects.filter(username = request.POST['username']).delete()
                except:
                    pass
                return render(request, 'user/register.html', {
                    'error_message': '邀请码/密钥无效'
                })
            
            facility = facility.first()
            
            if secret:
                if secret == facility.secret:
                    user.role = 'teacher'
                else:
                    try:
                        User.objects.filter(username = request.POST['username']).delete()
                    except:
                        pass
                    return render(request, 'user/register.html', {
                        'error_message': '邀请码/密钥无效'
                    })
            else:
                user.role = 'student'
            
            user.facility = facility
        
        user.save()
        return redirect('user:login')
    
def login_(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'user/login.html')
    if request.method == 'POST':
        user = authenticate(request, username = request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect('user:profile')
        else:
            return render(request, 'user/login.html', {
                'error_message': '用户名/密码错误'
            })


@login_required(login_url = 'user:login')
def profile(request: HttpRequest):

    stat = {}
    date = now().today()

    stat['total_posts'] = Post.objects.filter(author = request.user).count()
    stat['accepted_solutions'] =Answer.objects.filter(Q(score__gte = 0.6 * F('problem__score')), submission__student = request.user).count()
    stat['total_solutions'] = Answer.objects.filter(submission__student = request.user).count()
    stat['unjudged_solutions'] = Answer.objects.filter(score = 0, submission__student = request.user).count()
    stat['solution_trend'] = json.dumps([
        Answer.objects.filter(Q(date__gt=date - timedelta(days=x + 1), date__lt=date - timedelta(days=x)), submission__student = request.user).count()
            for x in range(0, 28)
    ])

    tag_exist  = 0
    for t in request.user.tag_set.all():
        try:
            weight = UserTagWeight.objects.get(user=request.user, tag=t).weight
            tag_exist = 1
            print(t.text,weight)
        except:
            print(t.text)
    return render(request, 'user/profile.html', {
        'tag_exist': tag_exist,
        'stat': stat,
    })

@login_required(login_url = 'user:login')
def edit_profile(request: HttpRequest):
    user = request.user

    if request.method == 'POST':
        if request.FILES.get('avatar'):
            user.avatar = request.FILES.get('avatar')

        if request.POST['currentPassword']:
            if not user.check_password(request.POST['currentPassword']):
                return render(request, 'user/edit_profile.html', {
                    'error_message': '原密码错误'
                })
            
            if request.POST['newPassword'] and request.POST['newPassword'] == request.POST['confirmPassword']:
                user.set_password(request.POST['newPassword'])
            else:
                return render(request, 'user/edit_profile.html', {
                    'error_message': '两次密码不一致'
                })
        user.save()
        return redirect("user:profile")
    else:
        return render(request, 'user/edit_profile.html')
    

@login_required(login_url='user:login')
def cloud(request: HttpRequest):
    if request.method == 'GET':
        res = BytesIO()
        tags = dict(UserTagWeight.objects.filter(user = request.user).values_list('tag__text', 'weight'))

        WordCloud(background_color='white', font_path='static/font/wqy-microhei.ttc').generate_from_frequencies(tags) \
            .to_image().save(res, format='png') 

        res.seek(0)

        return FileResponse(res, filename='image.png')