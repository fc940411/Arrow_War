from django.views.generic import View # 通过类视图来写view
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse  # 重定向函数,直接输入url 
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from apps.users.models import Users, Score
from apps.war.models import Arrows
from django.db.models import Q
import json
import math
import time
import threading
import random
import re

class PVE(View):
    '''单机页面'''
    def get(self, request):
        '''显示单机首页'''
        user = request.user
        score=Score.objects.get(parent=user)
        return render(request, 'war/pve.html', {'nickname':user.nickname, 
                                                      'score':score.scores, 
                                                      'times':score.times, 
                                                      'kills':score.kills,
                                                    })

    def post(self, request):
      user = request.user
      score_num = float(request.POST.get('score'))
      time = float(request.POST.get('time'))
      score = Score.objects.get(parent=user)
      if score_num > score.scores:
        score.scores = score_num
        score.save()
      if time > score.times:
        score.times = time
        score.save()
      return JsonResponse({'res':0})

class PVP(View):
    '''多人页面'''
    def get(self, request):
        '''显示多人首页'''
        user = request.user
        score=Score.objects.get(parent=user)
        return render(request, 'war/pvp.html', {'nickname':user.nickname, 
                                                     'score':score.scores, 
                                                     'times':score.times, 
                                                     'kills':score.kills,
                                                    })

    def post(self, request):

      return JsonResponse({'res':0})