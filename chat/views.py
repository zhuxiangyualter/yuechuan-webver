from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user.models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from user.views import get_user_from_token
from rest_framework.response import Response
@permission_classes([IsAuthenticated])
def chat(request):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    return Response(
        status = 200,
        data = {
            'message': 'chat page'
        }
    )