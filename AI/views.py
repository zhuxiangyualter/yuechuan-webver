from django.shortcuts import render
from django.http import JsonResponse, HttpRequest, HttpResponseBadRequest, HttpResponseServerError, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from user.models import *
import os
from django.db.models import Q, Count, Max, F
from dotenv import load_dotenv
import openai
import json
from .models import *
from .slide_generator import SlidesAPI
from index.views import Recommend
from tag.models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from user.views import get_user_from_token
from rest_framework.response import Response
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_KEY')
XF_API_SECRET = os.getenv('XF_APISecret')
XF_APP_ID = os.getenv('XF_APPID')
XF_API_KEY = os.getenv('XF_APIK')

api = SlidesAPI(XF_APP_ID, XF_API_SECRET, XF_API_KEY)


class PromptTemplate:
    initializer = ''
    content = ''

    def __init__(self, init='', content='{}'):
        self.initializer = init
        self.content = content

    def wrap(self, history, current):
        result = []

        if self.initializer:
            result.append({
                'role': 'system',
                'content': self.initializer
            })

        result.extend(history)

        result.append({
            'role': 'user',
            'content': self.content.format(current)
        })
        return result


PROMPT_TEMPALTE = {
    'question': PromptTemplate(
        '你需要作为一个AI助手，回答用户的问题。你的答案应当考虑周全，保证在各方面都回答到位。',
        "{}"
    ),
    'problem': PromptTemplate(
        '''你需要根据用户所给出的关键词或提示词来生成题目，并按照以下格式输出：
[题目描述]
---
[答案]

其中，[题目描述]应当是与给定关键词相关的历史学科题目，并应当带有疑问语气。[答案]应当是[题目描述]所对应的答案，并适当简短。题目描述与答案的内容中不要有任何前缀或后缀（如“答案：”）。
用户的输入中除关键词外不会含有任何内容。''',
        "{}"
    )
}

@permission_classes([IsAuthenticated])
def gpt(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if request.method == 'GET':
        return Response(
            status=200,
            data={
                'message': 'AI/gpt.html'
            }
        )
    if request.method == 'POST':

        if not request.POST.get('query'):
            return HttpResponseBadRequest()

        openai.api_key = OPENAI_API_KEY
        openai.base_url = 'https://api.ai-yyds.com/v1/'

        if request.POST['type'] == 'ask':
            history = []

            if request.POST.get('history'):
                history = json.loads(request.POST['history'])

            if request.POST.get('template') and PROMPT_TEMPALTE.get(request.POST.get('template')):
                messages = PROMPT_TEMPALTE[request.POST['template']].wrap(
                    history, request.POST['query']
                )
            else:
                messages = [
                    {
                        'role': 'user',
                        'content': request.POST['query']
                    }
                ]

            response = openai.chat.completions.create(
                messages=messages,
                model='gpt-3.5-turbo'
            )

            return JsonResponse({
                'data':{
                'content': response.choices[0].message.content,
                }
            })

        if request.POST['type'] == 'refresh':
            recommendQCount = 5
            messages = []
            recommendQ = []

            recommendTags = []
            recommendTags = Recommend(user, 0.1)
            recommendTags = recommendTags.recommend_tags(5)

            for tag in recommendTags:
                con = f"围绕关键词“{tag.text}”猜想用户想要询问你的问题，并输出这个问题，你的输出必须是一个疑问句，你的输出绝对不能超过20个字，绝对不能包含问题之外的任何内容，你的输出必须是一个疑问句，输出绝对不能包含“用户”二字"
                messages.append({
                    'role': 'user',
                    'content': con
                })
                response = openai.chat.completions.create(
                    messages=messages,
                    model='gpt-3.5-turbo'
                )
                print(response.choices[0].message.content)
                if '?' or '？' in response.choices[0].message.content:
                    recommendQ.append(response.choices[0].message.content)
                if len(recommendQ) >= recommendQCount:
                    break

            # for tag in Tag.objects.all():
            #     if len(recommendQ) >= recommendQCount:
            #         break
            #     con = f"围绕关键词“{tag.text}”猜想用户想要询问你的问题，并输出这个问题，你的输出必须是一个疑问句，你的输出绝对不能超过20个字，绝对不能包含问题之外的任何内容，你的输出必须是一个疑问句"
            #     response = openai.chat.completions.create(
            #         messages=messages,
            #         model='gpt-3.5-turbo'
            #     )
            #     print(response.choices[0].message.content)
            #     if '?' or '？' in response.choices[0].message.content:
            #         recommendQ.append(response.choices[0].message.content)

            return JsonResponse({
                'data':{
                'recommendQ': recommendQ
                }
            })

@permission_classes([IsAuthenticated])
def genppt(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if request.method == 'GET':
        return Response(
            status=200,
            data={
                'message': 'AI/slides.html'
            }
        )
    if request.method == 'POST':
        task = api.create_task(request.POST['description'], user)

        if task is None:
            return HttpResponseServerError('Failed when spawning task')

        return JsonResponse({
            'data':{
            'id': task.id,
            'cover': task.cover.url,
            'title': task.title,
            'subtitle': task.subtitle
            }
        })

@permission_classes([IsAuthenticated])
def refresh_state(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    record = SlideGeneration.objects.get(id=id)

    if not record:
        return HttpResponseNotFound()

    complete = api.fetch(record)

    record.refresh_from_db()

    return JsonResponse({
        'data':{
        'complete': complete,
        'url': record.result.url if record.status == 'complete' else ''
        }
    })
