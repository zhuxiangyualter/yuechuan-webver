from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse
from user.models import *
from .models import *
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AbstractUser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound
from user.models import *
from user.views import get_user_from_token
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
@permission_classes([AllowAny])
def user(request: HttpRequest):
    token = request.headers.get('Authorization')
    user1 = get_user_from_token(token)
    if not user1.is_staff:
        return Response(
            status=403
        )
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        paginator = Paginator(User.objects.all(), 25)
        return Response(
            data = {
                'data': {
                'total': User.objects.count(),
                'users': paginator.get_page(page),
                'facilities': Facility.objects.all(),
                'pages': paginator.num_pages
                }
            },
            status=200
        )
    elif request.method == 'POST':
        if request.POST['type'] == 'delete':
            user = User.objects.get(id=request.POST['id'])
            user.delete()
            return HttpResponse('删除成功')
        elif request.POST['type'] == 'ban':
            user = User.objects.get(id=request.POST['id'])
            user.is_active = not user.is_active
            user.save()
            return HttpResponse('封禁成功')
        elif request.POST['type'] == 'edit':
            user = User.objects.get(id=request.POST['id'])

            if request.POST['username']:
                user.username = request.POST['username']
            if request.POST['role']:
                user.role = request.POST['role']
            if request.POST['facility']:
                user.facility = Facility.objects.get(pk=int(request.POST['facility']))
            else:
                user.facility = None
            user.save()
            return Response(
                status=200,
                data={
                    'message': '修改成功'
                }
            )

@permission_classes([IsAuthenticated])
def facility(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if not user.is_staff:
        return Response(
            status=403
        )
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        paginator = Paginator(Facility.objects.all(), 25)
        return Response(
            data = {
                'data': {
                'total': Facility.objects.count(),
                'facilities': paginator.get_page(page),
                'pages': paginator.num_pages
                },
                'message': 'adminc/facility.html'
            },
            status=200
        )
    elif request.method == 'POST':
        if request.POST['type'] == 'new':
            data = {}

            if request.POST.get('invitation_code'):
                data['invitation_code'] = request.POST['invitation_code']

            if request.POST.get('secret'):
                data['secret'] = request.POST['secret']


            facility = Facility.objects.create(
                name = request.POST['name'],
                **data
            )

            facility.save()

            return HttpResponse('adminc:facility')
        
        elif request.POST['type'] == 'delete':
            id = request.POST['id']

            facility = Facility.objects.get(id=int(id))

            if facility is None:
                return HttpResponseBadRequest('Invalid facility id')
            
            facility.delete()

            return HttpResponse('ok')
@permission_classes([IsAuthenticated])
def student(request: HttpRequest):
    token = request.headers.get('Authorization')
    user1 = get_user_from_token(token)
    if user1.role != 'teacher':
        return Response(status=403)
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        paginator = Paginator(User.objects.filter(facility=user1.facility, role='student'), 25)
        return Response(
            data = {
                'data': {
                'total': User.objects.filter(role='student', facility=user1.facility).count(),
                'users': paginator.get_page(page),
                'facilities': Facility.objects.all(),
                'pages': paginator.num_pages
                }
            },
            status=200
        )
    elif request.method == 'POST':
        if request.POST['type'] == 'delete':
            user = User.objects.get(id=request.POST['id'])
            user.delete()
            return HttpResponse('ok')
        elif request.POST['type'] == 'ban':
            user = User.objects.get(id=request.POST['id'])
            user.is_active = not user.is_active
            user.save()
            return HttpResponse('ok')
        elif request.POST['type'] == 'edit':
            user = User.objects.get(id=request.POST['id'])
            if request.POST['username']:
                user.username = request.POST['username']
            if request.POST['role']:
                user.role = request.POST['role']
            user.save()
            return Response(
                status=200,
                data={
                    'message': '修改成功'
                }
            )