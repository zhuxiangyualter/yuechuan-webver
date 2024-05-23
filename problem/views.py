from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Max, Q
import asyncio
from dotenv import load_dotenv
from functional import seq
import json
import re
from .models import *
from tag.models import *
import openai
from functools import reduce
from problem.templatetags.markdown import unmarkup
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed
from user.views import get_user_from_token
from rest_framework.response import Response

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_KEY')

@permission_classes([IsAuthenticated])
def index(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if request.method == 'GET':
        problems = Problem.objects.filter(facility = user.facility) \
                          .annotate(latest_solution = Max('solution__id'))
        tags = Tag.objects.filter(problems__facility=user.facility).distinct()
        return JsonResponse({
            'data':{
                'problems': problems,
                'tags': tags,
                'user': user
            },
            'status': 200
        })
    if request.method == 'POST':
        print(request.POST['type'])
        if request.POST['type'] == 'search':
            tags = json.loads(request.POST['tags'])
            result = reduce(lambda qs, tag: qs.filter(tag__id = tag), tags, Problem.objects.filter(facility=user.facility))
            print(result)
            print({
                'result': seq(result.values()).map(lambda x: {
                    **x,
                    'statement': unmarkup(x['statement'])
                }).to_list()
            })
            return JsonResponse({
                'result': seq(result.values()).map(lambda x: {
                    **x,
                    'statement': unmarkup(x['statement'])
                }).to_list()
            }, safe=False)

    
@permission_classes([IsAuthenticated])
def generate(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if request.method == 'POST':
        asyncio.run(asyncio.sleep(1))

        openai.api_key = OPENAI_API_KEY
        openai.base_url = 'https://api.ai-yyds.com/v1/'

        statement = ''
        while '?' not in statement and '？' not in statement:
            messages1 = [
                {
                    'role': 'user',
                    'content': f"请你根据：{request.POST['keyword']}这段描述生成一道历史题目。题干不要超过100字，题干中绝对不能包含答案，题干必须是一个疑问句，你的输出绝对不能包含题干之外的任何内容"
                }
            ]
            response1 = openai.chat.completions.create(
                    messages=messages1,
                    model='gpt-3.5-turbo'
                )
            statement = response1.choices[0].message.content

        
        messages2 = [
            {
                'role': 'user',
                'content': f"{statement},以上是一道历史题目的题干，请你给出这道历史题目的答案，应该尽量简短，你的输出绝对不能包含答案之外的任何内容"
            },
        ]
        response2 = openai.chat.completions.create(
                messages=messages2,
                model='gpt-3.5-turbo'
            )
        answer = response2.choices[0].message.content
        
        print(statement, answer)
        return JsonResponse({
            'statement': statement,
            'answer': answer,
        })
@permission_classes([IsAuthenticated])
def view(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    problem = Problem.objects.get(id = id)
    solutions = Solution.objects.filter(problem=problem)
    if request.method == 'GET':
        return JsonResponse({
            'data':{
                'problem': problem,
                'solutions': solutions,
            },
            'status': 200
        })
    elif request.method == 'POST':
        sln = Solution.objects.create(
            creator = user,
            problem = problem,
            content = request.POST['content']
        )
        sln.save()
        return Response({
            'data': {
                'solution': sln.id
            }
        }, status=200)
@permission_classes([IsAuthenticated])
def view_solution(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    try:
        sln = Solution.objects.get(id = id)
        comment = SlnComment.objects.filter(solution=sln)
    except Solution.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        return Response({
            'data': {
                'solution': sln,
                'comments': comment
            }
        }, status=200)
    if request.method == 'POST':
        comment = SlnComment.objects.create(author=user, content=request.POST['comment'], solution=sln)
        return Response(status=200, data={'data':{
          'id' : id
        } }
                        )
@permission_classes([IsAuthenticated])
def new(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if user.role != 'teacher':
        return Response(status=403)
    elif request.method == 'POST':
        problem = Problem.objects.create(
            facility = user.facility,
            creator = user,
            title = request.POST['title'],
            statement = request.POST['statement'],
            answer = request.POST['answer'],
        )
        if request.POST['tag']:
            tags = seq(request.POST['tag'].split(';')).map(lambda s: s.strip()).filter(lambda s: bool(s))
            for t in tags:
                tag = Tag.objects.filter(text=t).first()

                if tag is None:
                    tag = Tag.objects.create(text = t)

                tag.problems.add(problem)
            
            tag.save()

        problem.save()

        return Response(status=200, data={'data':{
            'problem': problem.id
        }})
