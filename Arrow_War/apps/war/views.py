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
        return render(request, 'war/base_war.html', {'nickname':user.nickname, 
                                                       'score':score.scores, 
                                                       'times':score.times, 
                                                       'kills':score.kills,
                                                       })


class PVP(View):
    '''多人页面'''
    def get(self, request):
        '''显示多人首页'''
        user = request.user
        score=Score.objects.get(parent=user)
        return render(request, 'war/base_war.html', {'nickname':user.nickname, 
                                                       'score':score.scores, 
                                                       'times':score.times, 
                                                       'kills':score.kills,
                                                       })