from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest
from django.http import HttpResponse
from user.models import *

@login_required(login_url='user:login')
def user(request: HttpRequest):
    if not request.user.is_staff:
        return render(request, '403.html')
    
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        paginator = Paginator(User.objects.all(), 25)
        return render(request, 'adminc/user.html',{
            'total': User.objects.count(), 
            'users': paginator.get_page(page),
            'facilities': Facility.objects.all(),
            'pages': paginator.num_pages
        })
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
            if request.POST['facility']:
                user.facility = Facility.objects.get(pk=int(request.POST['facility']))
            else:
                user.facility = None
            user.save()
            return redirect('adminc:user')


@login_required(login_url='user:login')
def facility(request: HttpRequest):
    if not request.user.is_staff:
        return render(request, '403.html')
    
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        paginator = Paginator(Facility.objects.all(), 25)
        return render(request, 'adminc/facility.html',{
            'total': Facility.objects.count(),
            'facilities': paginator.get_page(page),
            'pages': paginator.num_pages
        })
    
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

            return redirect('adminc:facility')
        
        elif request.POST['type'] == 'delete':
            id = request.POST['id']

            facility = Facility.objects.get(id=int(id))

            if facility is None:
                return HttpResponseBadRequest('Invalid facility id')
            
            facility.delete()

            return HttpResponse('ok')
        
@login_required(login_url='user:login')
def student(request: HttpRequest):
    if request.user.role != 'teacher':
        return render(request, '403.html')
    
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        paginator = Paginator(User.objects.filter(facility=request.user.facility, role='student'), 25)
        return render(request, 'adminc/student.html',{
            'total': User.objects.filter(role='student', facility=request.user.facility).count(), 
            'users': paginator.get_page(page),
            'pages': paginator.num_pages
        })
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
            return redirect('adminc:student')