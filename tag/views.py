from django.shortcuts import render
from django.http import JsonResponse, HttpResponseForbidden, HttpRequest, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from .models import Tag
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from user.views import get_user_from_token
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def tag(request: HttpRequest):
    return JsonResponse(
        data = {
            'data':{
            'tags': Tag.objects.all()
            }
        },
        status = 200
    )