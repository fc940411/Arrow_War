from django.views.generic import View # 通过类视图来写view
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, reverse  # 重定向函数,直接输入url 
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from apps.users.models import Users, Score, GameControl
from apps.war.models import Arrows, Bullets
from django.db.models import Q
from utils.mixin import LoginRequiredMixin
import json
import math
import time
import threading
import random
import re
import gevent
import pymysql.cursors
from gevent import monkey
import redis

class PVE(LoginRequiredMixin, View):
    '''单机页面'''

    def get(self, request):
        '''显示单机首页'''
        user = request.user
        arrow=Arrows.objects.get(parent=user)
        arrow.life = False
        arrow.save()
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

class PVP(LoginRequiredMixin, View):
    '''多人页面'''

    def __init__(self):
        '''连接redis数据库'''
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=3)

    def get(self, request):
        '''显示多人首页'''
        user = request.user
        detail = {'life':True,'left':500,'top':500,'speed':8,'angle':0}
        self.redis.mset({str(user.id):json.dumps(detail)})
        return render(request, 'war/pvp.html',)

    def post(self, request):
        '''返回箭头、子弹位置及存活状态'''
        # 获取箭头信息并控制
        user = request.user
        direction = request.POST.get('direction')
        upspeed = request.POST.get('upspeed')
        detail = json.loads(self.redis.get(str(user.id)))

        #--------控制自身箭头----------
        if direction == 'left':
            detail['angle'] = int(detail['angle']) - 6
            self.redis.mset({str(user.id):json.dumps(detail)})
        elif direction == 'right':
            detail['angle'] = int(detail['angle']) + 6
            self.redis.mset({str(user.id):json.dumps(detail)})

        if upspeed == 'up':
            if detail['speed'] != 16:
                detail['speed'] = 16
                self.redis.mset({str(user.id):json.dumps(detail)})
        else:
            if detail['speed'] != 8:
                detail['speed'] = 8
                self.redis.mset({str(user.id):json.dumps(detail)})

        if detail['life'] == False:
            killed = True
        else:
            killed = False

        my_arrow = {'left':detail['left'], 
                    'top':detail['top'], 
                    'angle':detail['angle'],
                    'life':detail['life'],}
        #--------获取其余箭头和子弹信息----------
        arrows = self.redis.keys()
        other_arrows = []
        for arrow in arrows:
            i = arrow.decode('utf-8')
            if i != 'bullets' and i != str(user.id):
                detail = json.loads(self.redis.get(i))
                arrow_information = {'left':detail['left'], 
                                     'top':detail['top'], 
                                     'angle':detail['angle']}
                other_arrows.append(arrow_information)

        all_bullets = []
        if self.redis.get('bullets'):
            bullets = json.loads(self.redis.get('bullets'), encoding = "utf-8")
            if len(bullets) > 0:
                for bullet in bullets:
                    bullet_information = {'left':bullet['left'], 
                                         'top':bullet['top'], 
                                         'angle':bullet['angle']}
                    all_bullets.append(bullet_information)


        return JsonResponse({'my_arrow':my_arrow,
                             'other_arrows':other_arrows,
                             'bullets':all_bullets,
                             'killed':killed})

class PVP_Calc(LoginRequiredMixin, View):
    '''箭头位置计算'''
    def __init__(self):
        '''连接redis数据库'''
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=3)

    def arrow_calc(self, arrow_id):
        '''箭头移动计算'''
        i = json.loads(self.redis.get(arrow_id))
        if i['life'] == True:
            x = i['left'] - 500
            y = i['top'] - 500
            
            if x**2 + y**2 >= 497**2 or i['left'] < 0 or i['top'] < 0:
                # 1.判断是否出界
                i['life'] = False
            else:
                # 2.判断是否相撞
                arrows = self.redis.keys()
                for arrow in arrows:
                    if arrow.decode('utf-8') != arrow_id and arrow.decode('utf-8') != 'bullets':
                        n = json.loads(self.redis.get(arrow.decode('utf-8')))
                        if (n['left']-i['left'])**2 + (n['top']-i['top'])**2 <= 7**2:
                            i['life'] = False
                            n['life'] = False
                            self.redis.mset(arrow.decode('utf-8'), n)
                if self.redis.get('bullets'):
                    bullets = json.loads(self.redis.get('bullets'), encoding = "utf-8")
                    for b in bullets:
                        if b['parent_id'] != arrow_id:
                            if (b['left']-i['left'])**2 + (b['top']-i['top'])**2 <= 5**2:
                                i['life'] = False
                  
                # 3.计算移动位置
                i['left'] = i['left'] + math.sin(math.pi*(i['angle'])/180)*i['speed']
                i['top'] = i['top'] - math.cos(math.pi*(i['angle'])/180)*i['speed']
            self.redis.mset({arrow_id:json.dumps(i)})

    def bullet_calc(self):
        '''子弹位置计算'''
        if self.redis.get('bullets'):
            bullets = json.loads(self.redis.get('bullets'), encoding = "utf-8")
            index = -1
            del_list = []
            for b in bullets:
                index += 1
                bullets[index]['left'] = b['left'] + math.sin(math.pi*(b['angle'])/180)*b['speed']
                bullets[index]['top'] = b['top'] - math.cos(math.pi*(b['angle'])/180)*b['speed']
                if (b['left']-500)**2 + (b['top']-500)**2 >= 550**2 or b['left'] < 0 or b['top'] < 0:
                    # 1.判断是否出界
                    del_list.append(index)
                    
            del_list.reverse()
            if del_list:
                for i in del_list:
                    del bullets[i]

            self.redis.mset({'bullets':json.dumps(bullets)})

    def post(self, request):
        '''循环计算位置'''
        state_position_calc = request.POST.get('state_position_calc')
        if state_position_calc == '0':
            state = GameControl.objects.get(id=1)
            state.position_calc = True
            state.save()
        elif state_position_calc == '1':
            state = GameControl.objects.get(id=1)
            state.position_calc = False
            state.save()

        if state.position_calc == True:
            while True:
                start_time = time.time()
                state = GameControl.objects.get(id=1)
                if state.position_calc == False:
                    break

                # 计算子弹位置
                self.bullet_calc()

                # 获取所有箭头并计算位置
                arrows = self.redis.keys()
                for arrow in arrows:
                    if arrow.decode('utf-8') != 'bullets':
                        self.arrow_calc(arrow.decode('utf-8'))

                end_time = time.time()
                t = round(end_time-start_time, 3)
                if t < 0.06:
                    time.sleep(0.06 - t)
        return JsonResponse({'res':0})

class PVP_Createbullets(LoginRequiredMixin, View):
    '''子弹生成计算'''

    def __init__(self):
        '''连接redis数据库'''
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=3)

    def post(self, request):
        user = request.user
        arrow = json.loads(self.redis.get(str(user.id)).decode('utf-8'))
        bullet = {'parent_id':str(user.id), 'left':int(arrow['left']), 'top':int(arrow['top']), 'angle':int(arrow['angle']), 'speed':int(arrow['speed']+8)}
        if self.redis.get('bullets'):
            bullets = json.loads(self.redis.get('bullets'), encoding = "utf-8")
            bullets.append(bullet)
            self.redis.mset({'bullets':json.dumps(bullets)})
        else:
            self.redis.mset({'bullets':json.dumps([bullet])})

        return JsonResponse({'res':0})

class Game_Control(View):
    '''游戏控制页面'''
    
    def get(self, request):
        '''显示控制页面'''
        return render(request, 'war/gamecontrol.html')

    def post(self, request):
        state = GameControl.objects.get(id=1)
        return JsonResponse({'position_calc':state.position_calc,
                            })