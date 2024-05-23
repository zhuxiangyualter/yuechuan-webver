from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.http import JsonResponse
from django.db.models import Q, Sum, Subquery, OuterRef
from rest_framework import status
from rest_framework.response import Response

from user.models import *
from tag.models import *
from functools import reduce
from problem.models import *
from paper.models import *
from problem.templatetags.markdown import unmarkup
from functional import seq
from collections import Counter
import json
import openai
from dotenv import load_dotenv
from django.http import HttpResponse
from django.http import *
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
        papers = Paper.objects.filter(facility=user.facility)
        return Response(
            data={
                'data':{
                    'papers': papers
                },
                "message": "success"
        },status=status.HTTP_200_OK
        )
        # return render(request, 'paper/index.html', {
        #     'papers': papers,
        # })
@permission_classes([IsAuthenticated])
def view(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    paper = Paper.objects.get(id=id)
    probblems = PaperProblem.objects.filter(paper=paper)

    if request.method == 'GET':
        # return render(request, 'paper/view.html', {
        #     'paper': paper,
        #     'problems': probblems,
        # })
        return Response(
            data= {
            'data': {
            'paper': paper,
            'problems': probblems
            },
            "message":"success"
        },status=status.HTTP_200_OK
        )
    if request.method == 'POST':

        sub = Submission.objects.create(student=user, paper=paper)

        for p in probblems:
            answer = Answer.objects.filter(
                submission=sub,
                problem=p,
            ).first()
            if answer is not None:
                answer.answer=request.POST[f'answer-{p.raw.id}']
                answer.save()
            else:
                Answer.objects.create(
                    problem=p,
                    submission=sub,
                    answer=request.POST[f'answer-{p.raw.id}']
                )
        # return redirect('paper:submission', sub.id)
        return Response(
            data={
            'data': {
            'submission': sub.id
            },
            "message":"success"
        },status=status.HTTP_200_OK
        )
@permission_classes([IsAuthenticated])
def new(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if request.method == 'GET':
        tags = Tag.objects.filter(problems__facility=user.facility).distinct()

        # return render(request, 'paper/new.html', {
        #     'tags': tags
        # })
        return Response(
            data={
            'data': {
            'tags': tags
            },
            "message":"success"
        },status=status.HTTP_200_OK
        )
    if request.method == 'POST':
        if request.POST['type'] == 'search':
            tags = json.loads(request.POST['tags'])
            result = reduce(lambda qs, tag: qs.filter(tag__id = tag), tags, Problem.objects.filter(facility=user.facility))
            
            return JsonResponse(
                data={
                'data': {
                'result': seq(result.values()).map(lambda x: {
                    **x,
                    'statement': unmarkup(x['statement'])
                }).to_list()
                }
            },status = status.HTTP_200_OK, safe=False)

        if request.POST['type'] == 'submit':
            problems = json.loads(request.POST['problems'])
            paper = Paper.objects.create(title=request.POST['title'], facility=user.facility)
            for id in problems:
                p = Problem.objects.get(pk = id)
                PaperProblem.objects.create(paper=paper, raw=p, score=request.POST[f'score{id}'])
           # return redirect('paper:view', paper.id)
        return Response(
            data={
            'data': {
            'paper': paper.id
            },
            "message":"success"
        },status=status.HTTP_200_OK
        )
@permission_classes([IsAuthenticated])
def submissions(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if request.method == 'GET':
        max_score = Paper.objects.filter(pk=OuterRef('paper_id')) \
            .annotate(max_score=Sum('paperproblem__score'))
        
        if user.role == 'student':
            sub = Submission.objects.filter(student=user) \
                .annotate(score=Sum('answer__score'),max_score=Subquery(max_score.values('max_score')))
            
        elif user.role == 'teacher':
            sub = Submission.objects.filter(student__facility=user.facility) \
                .annotate(score=Sum('answer__score'),max_score=Subquery(max_score.values('max_score')))
            
        # return render(request, 'paper/submissions.html', {
        #     'submissions': sub
        # })
        return Response(
            data={
            'data': {
            'submissions': sub
            },
            "message":"success"
        },status=status.HTTP_200_OK
        )
@permission_classes([IsAuthenticated])
def paper_submission(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if request.method == 'GET':
        if user.role == 'teacher':
            max_score = Paper.objects.filter(pk=OuterRef('paper_id')) \
                .annotate(max_score=Sum('paperproblem__score'))
            paper = Paper.objects.get(id=id)
            sub = Submission.objects.filter(paper=paper) \
                .annotate(score=Sum('answer__score'), total_score=Subquery(max_score.values('max_score')))
            # return render(request, 'paper/paper_submission.html', {
            #     'submissions': sub,
            #     'paper': paper,
            # })
            return Response(
                data={
                'data': {
                'submissions': sub,
                'paper': paper
                },
                "message":"success"
            },status=status.HTTP_200_OK
            )
        elif user.role == 'student':
            return Response(
                data={
                "message":"学生禁用此接口"
            },status=status.HTTP_403_FORBIDDEN
            )
@permission_classes([IsAuthenticated])
def submission(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    s = Submission.objects.get(id=id)
    answer = Answer.objects.filter(submission=s)

    if request.method == 'POST':
        if s.student != user and user.role != 'teacher':
            return Response(
                data={
                "message":"无权限"
            },status=status.HTTP_403_FORBIDDEN
            )
        if request.POST.get('type') == 'analysis':
            openai.api_key = OPENAI_API_KEY
            openai.base_url = 'https://api.ai-yyds.com/v1/'

            cnt = 1
            qs = ''
            for ans in answer:
                pbl = ans.problem.raw
                q = f'第{cnt}道题：题目标题为：{ans.problem.raw.title}，题目内容为{ans.problem.raw.statement}，题目标准答案为：{ans.problem.raw.answer}，学生的答案为：{ans.answer}。'
                cnt += 1
                qs += q
                prompt = '''
                我会给你几道题的题目标题，题目内容，标准答案和我的答案，题目内容可能会包含markdown标记，你必须过滤这些标记，
                你的任务是根据题目，对照标准答案来分析我的答案，找出我的答案的问题，指出我知识的不足并给出学习建议，
                学习建议一定要根据题目和作答情况具体到某些知识点不能太笼统。
                每一道题都要给出分析和建议，在最后总结一下所有题目并总体评价一下学生的作答情况，给出合理的建议。
                你的输出包含分析、评价、建议之外的任何内容，
                不能包含任何不相关的前缀后缀类似"好的"，绝对不能出现与markdown相关的内容，绝对不能出现markdown标记符号，绝对不能出现markdown标记后隐藏的文字，不超过200字。
                '''
                messages = [
                    {
                        'role': 'user',
                        'content': prompt + qs
                    }
                ]
            response = openai.chat.completions.create(
                messages=messages,
                model='gpt-3.5-turbo'
            )
            return JsonResponse({
                'data': {
                'analysis': response.choices[0].message.content
                },
                'message': 'success'
            },status=status.HTTP_200_OK
            )
        else:
            return Response({
                "message":"无权限"
            },status=status.HTTP_403_FORBIDDEN
            )
    if request.method == 'GET':
        if s.student != user and user.role != 'teacher':
            return Response({
                "message":"无权限"
            },status=status.HTTP_403_FORBIDDEN
            )
        # return render(request, 'paper/submission.html', {
        #     'answer': answer,
        #     'submission': s,
        # })
        return Response({
            'data': {
            'answer': answer,
            'submission': s
            },
            "message":"success"
        },status=status.HTTP_200_OK
        )
@permission_classes([IsAuthenticated])
def judge(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if user.role != 'teacher':
        return Response({
            "message":"无权限"
        },status=status.HTTP_403_FORBIDDEN
        )
    sub = Submission.objects.get(id=id)
    answer = Answer.objects.filter(submission=sub)

    if request.method == 'GET':
        return Response({
            'data': {
            'submission': sub,
            'answers': answer,
            },
            "message":"paper/judge.html"
        },status=status.HTTP_200_OK
        )
    elif request.method == 'POST':
        for ap in answer:
            originalScore = ap.score
            ap.score = request.POST[f'score-{ap.id}']
            ap.save()
            if int(ap.score) < int(ap.problem.score) * 0.6:
                tags = ap.problem.raw.tag_set.all()
                for tag in tags:
                    weight = UserTagWeight.objects.filter(user=ap.submission.student, tag=tag).first()
                    if weight is not None:
                        weight.weight += 1
                        print(weight.weight)
                        weight.save()
                    else:
                        UserTagWeight.objects.create(user=ap.submission.student, tag=tag, weight=1)
                    tag.user.add(ap.submission.student)
        # return redirect('paper:submission', id)
        return Response({
            'data': {
            'submission': id
            },
            "message":"success"
        },status=status.HTTP_200_OK
        )
@permission_classes([IsAuthenticated])
def statistics(request: HttpRequest, id: int):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    if user.role != 'teacher':
        return Response({
            "message":"无权限"
        },status=status.HTTP_403_FORBIDDEN
        )
    paper = Paper.objects.filter(id=id) \
        .annotate(sum_score=Sum('paperproblem__score')).first()
    
    sub = Submission.objects.filter(paper_id=id)    \
        .annotate(score=Sum('answer__score'))   \
        .values_list('score', flat=True)

    counter = Counter(sub)
    return Response({
        'data': {
        'paper': paper,
        'count': json.dumps(counter)
        },
        "message":"paper/statistics.html"
    },status=status.HTTP_200_OK
    )
