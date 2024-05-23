from django.shortcuts import render
from django.http import HttpRequest
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q, Count, Max, F
from django.utils.timezone import now
from datetime import timedelta
import random
import numpy as np
from collections import defaultdict

import json

from zone.models import Post
from user.models import User, Facility
from problem.models import Problem, Solution
from tag.models import *
from paper.models import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from user.views import get_user_from_token
from rest_framework.response import Response

# 推荐文章或题目
class Recommend():

    def __init__(self, user, a: float):
        self.user = user
        self.a = a
    #计算Jaccard 相似度
    def jaccard_similarity(self, tag_a, tag_b):
        item_pr_u_a = Problem.objects.filter(tag__text=tag_a)
        item_pr_u_b = Problem.objects.filter(tag__text=tag_b)
        set_pr_a = set(item_pr_u_a)
        set_pr_b = set(item_pr_u_b)
        inte_pr = set_pr_a & set_pr_b
        union_pr = set_pr_a | set_pr_b
        return len(inte_pr) / len(union_pr)
    #根据用户的标签权重和问题的标签相似度预测问题的评分。
    def predict_rating(self, item):
        weighted_sum = 0
        tag_similaritie = 0
        for tag in self.user.tag_set.all():
            try:
                weight = UserTagWeight.objects.get(user=self.user, tag=tag).weight
            except:
                weight = 1
            try:
                for tagp in item.tag_set.all():
                    tag_similaritie += self.jaccard_similarity(tag.text, tagp.text)
            except:
                tag_similaritie = self.jaccard_similarity(tag.text, item.text)
            weighted_sum += weight * tag_similaritie
        return weighted_sum
    #推荐标签
    def recommend_tags(self, num):
        tag_ratings = []
        for p in Tag.objects.all():
            # print(p.text, self.predict_rating(p))
            tag_ratings.append({"id": p.id, "rating": self.predict_rating(p)})
        recommendResults = []
        counts = [ratings["rating"] for ratings in tag_ratings]
        weights = np.exp(self.a * np.array(counts))
        probabilities = weights / np.sum(weights)
        chosen = []
        while len(recommendResults) < num:
            chosen_index = np.random.choice(len(counts), p=probabilities)
            if chosen_index not in chosen:
                chosen.append(chosen_index)
                chosen_post = Tag.objects.get(id=tag_ratings[chosen_index]['id'])
                recommendResults.append(chosen_post)
            else:
                continue
        return recommendResults
    #推荐题目
    def recommend_problems(self, num):
        problem_ratings = []
        for p in Problem.objects.all():
            # print(p.title, self.predict_rating(p))
            problem_ratings.append({"id": p.id, "rating": self.predict_rating(p)})
        recommendResults = []
        counts = [ratings["rating"] for ratings in problem_ratings]
        weights = np.exp(self.a * np.array(counts))
        probabilities = weights / np.sum(weights)
        chosen = []
        while len(recommendResults) < num:
            chosen_index = np.random.choice(len(counts), p=probabilities)
            if chosen_index not in chosen:
                chosen.append(chosen_index)
                chosen_problem = Problem.objects.get(id=problem_ratings[chosen_index]['id'])
                recommendResults.append(chosen_problem)
            else:
                continue
        return recommendResults
    #推荐文章
    def recommend_posts(self, num):
        post_ratings = []
        for p in Post.objects.all():
            # print(p.title, self.predict_rating(p))
            post_ratings.append({"id": p.id, "rating": self.predict_rating(p)})
        recommendResults = []
        counts = [ratings["rating"] for ratings in post_ratings]
        weights = np.exp(self.a * np.array(counts))
        probabilities = weights / np.sum(weights)
        chosen = []
        while len(recommendResults) < num:
            chosen_index = np.random.choice(len(counts), p=probabilities)
            if chosen_index not in chosen:
                chosen.append(chosen_index)
                chosen_post = Post.objects.get(id=post_ratings[chosen_index]['id'])
                recommendResults.append(chosen_post)
            else:
                continue
        return recommendResults



@permission_classes([IsAuthenticated])
def index(request: HttpRequest):
    token = request.headers.get('Authorization')
    user = get_user_from_token(token)
    facility = user.facility

    feed = []

    for user in User.objects.filter(facility=facility):
        for post in Post.objects.filter(author=user):
            feed.append({
                'type': 'post',
                'date': post.date,
                'user': user,
                'title': post.title,
                'subtitle': post.content[:10],
                'link': reverse('zone:view', args=[post.id])
            })

    for problem in Problem.objects.filter(facility=facility):
        solutions = Solution.objects.filter(creator=user, problem=problem).count()
        feed.append({
            'type': 'problem',
            'date': problem.date,
            'user': problem.creator,
            'title': problem.title,
            'subtitle': problem.statement[:10],
            'link': reverse('problem:view', args=[problem.id]),
            'solved': solutions != 0
        })

    recommendProblems = []
    recommendProblems = Recommend(request.user, 0.1)
    recommendProblems = recommendProblems.recommend_problems(6)

    recommendPosts = []
    recommendPosts = Recommend(request.user, 0.1)
    recommendPosts = recommendPosts.recommend_posts(6)

    return Response(
        data = {
            'data': {
            "feed": sorted(feed, key=lambda x: x['date'], reverse=True),
            "problems": Problem.objects.filter(facility=facility).annotate(
                max_score=Max('solution__score', filter=Q(creator__facility=facility))).filter(Q(max_score__lt=60)),
            "recommend": recommendProblems,
            "recommendpost": recommendPosts,
            },  'message':'index/index.html'
        },
        status = 200
    )