from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.http.request import HttpRequest

from paper.models import *
from tag.models import *
from wordcloud import WordCloud
from django.db.models import Q, Count, Max, F
from datetime import timedelta
from io import BytesIO
import json
from django.utils.timezone import now
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AbstractUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed


def get_user_from_token(token):
    try:
        user = Token.objects.get(key=token).user
        return user
    except Token.DoesNotExist:
        raise AuthenticationFailed('Invalid token')
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request: HttpRequest):
    username = request.data.get('username')
    password = request.data.get('password')
    repwd = request.data.get('confirm-password')
    if password != repwd:
        return Response(
            data={
                'error_message': '密码不匹配',
            },
            status=400
        )
    if User.objects.filter(username=username).count():
        return Response(
            data={
                'error_message': '用户名已存在',
            },
            status=400
        )
    invitation = request.data.get['invitation-code']
    secret = request.data.get['auth-secret']

    user = User.objects.create_user(
        username=username,
        password=password
    )
    if invitation:
        facility = Facility.objects.filter(invitation_code=invitation)

        if facility.count() == 0:
            try:
                User.objects.filter(username=username).delete()
            except:
                pass
            return Response(
                data={
                    'error_message': '邀请码/密钥无效',
                },
                status=400
            )

        facility = facility.first()

        if secret:
            if secret == facility.secret:
                user.role = 'teacher'
            else:
                try:
                    User.objects.filter(username=username).delete()
                except:
                    pass
                return Response(
                    data={
                        'error_message': '邀请码/密钥无效',
                    },
                    status=400
                )
        else:
            user.role = 'student'

        user.facility = facility

    user.save()
    return Response(
        status=200
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response({'error': 'Please provide both username and password'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)

    if not user:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)

    return Response({
        'token': token.key,
        'role': user.role,
        'is_super': user.is_superuser
    }, status=status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
def profile(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    stat = {}
    date = now().today()

    stat['total_posts'] = Post.objects.filter(author=user).count()
    stat['accepted_solutions'] = Answer.objects.filter(Q(score__gte=0.6 * F('problem__score')),
                                                       submission__student=user).count()
    stat['total_solutions'] = Answer.objects.filter(submission__student=user).count()
    stat['unjudged_solutions'] = Answer.objects.filter(score=0, submission__student=user).count()
    stat['solution_trend'] = json.dumps([
        Answer.objects.filter(Q(date__gt=date - timedelta(days=x + 1), date__lt=date - timedelta(days=x)),
                              submission__student=user).count()
        for x in range(0, 28)
    ])

    tag_exist = 0
    for t in user.tag_set.all():
        try:
            weight = UserTagWeight.objects.get(user=user, tag=t).weight
            tag_exist = 1
            print(t.text, weight)
        except:
            print(t.text)
    return Response({
        "message": "success",
        "data": {
            "tag_exist": tag_exist,
            "stat": stat,
        }
    }, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def edit_profile(request: HttpRequest):
    token = request.headers.get('Authorization')

    user = get_user_from_token(token)
    if request.FILES.get('avatar'):
        user.avatar = request.FILES.get('avatar')
        user.save()
        return Response(
            data={
                'message': '头像修改成功',
            },
            status=200
        )
    if request.POST['currentPassword']:
        if not user.check_password(request.POST['currentPassword']):
            return Response(
                data={
                    'error_message': '原密码错误',
                },
                status=400
            )
        if request.POST['newPassword'] and request.POST['newPassword'] == request.POST['confirmPassword']:
            user.set_password(request.POST['newPassword'])
            user.save()
            return Response(data={
                'message': '密码修改成功',
            },
                status=200
            )
        else:
            return Response(
                data={
                     'error_message': '两次密码不一致',
                 },
                 status=400
            )



@permission_classes([IsAuthenticated])
def cloud(request: HttpRequest):
    if request.method == 'GET':
        token = request.headers.get('Authorization')
        user = get_user_from_token(token)
        res = BytesIO()
        tags = dict(UserTagWeight.objects.filter(user=user).values_list('tag__text', 'weight'))
        WordCloud(background_color='white', font_path='static/font/wqy-microhei.ttc').generate_from_frequencies(tags) \
            .to_image().save(res, format='png')
        res.seek(0)
        return FileResponse(res, filename='image.png')
