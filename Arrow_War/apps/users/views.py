from django.views.generic import View # 通过类视图来写view
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse  # 重定向函数,直接输入url 
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from django.db.models import Q
from django.conf import settings
from django.core.mail import send_mail
from apps.users.models import Users, Score
from apps.war.models import Arrows
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from celery_tasks.tasks import send_register_active_email
from utils.mixin import LoginRequiredMixin
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
            Score.objects.create(parent=user)
            Arrows.objects.create(parent=user)
            user.is_active = True
            user.save()
            #send_register_active_email.delay(user.id, user.email, user.username)
            return JsonResponse({'errmsg':0})
        else:
            # 4.返回应答
            return JsonResponse({'errmsg':'用户已存在'})


class Personal(LoginRequiredMixin, View):
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


class Register_Active(View):
    '''注册激活类'''
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 300)
        try:
            info = serializer.loads(token)
            # 获取待激活的用户名
            user_id = info['user_id']

            # 根据用户名获取用户信息
            user = Users.objects.get(id=user_id)
            user.is_active = True
            user.save()

            # 跳转到登陆页面
            return redirect(reverse('index'))
        except SignatureExpired as e:
            # 激活链接已过期
            return HttpResponse('激活链接已过期!')


class Ranking(View):
    '''排行榜类'''
    def post(self, request):
        scores = Score.objects.order_by('-scores')
        times = Score.objects.order_by('-times')
        kills = Score.objects.order_by('-kills')
        scores_names = [scores[0].parent.nickname, scores[1].parent.nickname, scores[2].parent.nickname]
        scores_ranking = [scores[0].scores, scores[1].scores, scores[2].scores]
        times_names = [times[0].parent.nickname, times[1].parent.nickname, times[2].parent.nickname]
        times_ranking = [times[0].times, times[1].times, times[2].times]
        kills_names = [kills[0].parent.nickname, kills[1].parent.nickname, kills[2].parent.nickname]
        kills_ranking = [kills[0].kills, kills[1].kills, kills[2].kills]
        return JsonResponse({'scores_name0':scores_names[0],'scores_name1':scores_names[1],'scores_name2':scores_names[2],
                             'scores_ranking0':scores_ranking[0],'scores_ranking1':scores_ranking[1],'scores_ranking2':scores_ranking[2],
                             'times_name0':times_names[0],'times_name1':times_names[1],'times_name2':times_names[2],
                             'times_ranking0':times_ranking[0],'times_ranking1':times_ranking[1],'times_ranking2':times_ranking[2],
                             'kills_name0':kills_names[0],'kills_name1':kills_names[1],'kills_name2':kills_names[2],
                             'kills_ranking0':kills_ranking[0],'kills_ranking1':kills_ranking[1],'kills_ranking2':kills_ranking[2],
            })