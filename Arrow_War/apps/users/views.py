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


class Index(View):
    '''首页'''
    def get(self, request):
        '''显示首页'''
        return render(request, 'users/index.html')
    def post(self, request):
        '''登陆'''
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            # if user.is_active == 0:
            #     return JsonResponse({'errmsg':'账号未激活!'})
            # else:
            login(request, user)
            return JsonResponse({'errmsg':0})
        else:
            return JsonResponse({'errmsg':'账号密码错误!'})


class Register(View):
    '''注册页'''
    def get(self, request):
        '''显示注册页面'''
        return render(request, 'users/register.html')

    def post(self, request):
        '''注册处理'''
        # 1.接受数据
        username = request.POST.get('username')
        password = request.POST.get('password')
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        # 2.进行数据校验
        if not all([username, email, password, nickname]):
            # 数据不完整
            return JsonResponse({'errmsg':'数据不完整'})
        if len(nickname) >= 30:
            # 昵称过长
            return JsonResponse({'errmsg':'昵称过长'})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            # 邮箱验证
            return JsonResponse({'errmsg':'邮箱不合法'})
        # 3.进行业务处理
        try:
            check=Users.objects.get(username=username)
        except:
            user = Users.objects.create_user(username=username, password=password, email=email, nickname=nickname)
            user.is_active = True
            user.save()
            Score.objects.create(parent=user)
            Arrows.objects.create(parent=user)
            return JsonResponse({'errmsg':0})
        else:
            # 4.返回应答
            return JsonResponse({'errmsg':'用户已存在'})


class Personal(View):
    '''个人首页'''
    def get(self, request):
        '''显示个人首页'''
        user = request.user
        score=Score.objects.get(parent=user)
        return render(request, 'users/personal.html', {'nickname':user.nickname, 
                                                       'score':score.scores, 
                                                       'times':score.times, 
                                                       'kills':score.kills,
                                                       })
    def post(self, request):
        logout(request)
        return JsonResponse({'errmsg':0})