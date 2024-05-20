from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user.models import *

@login_required(login_url='user:login')
def chat(request):
    return render(request, 'chat/chat.html')