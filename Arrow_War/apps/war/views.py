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
    def get(self, request):
        '''显示多人首页'''
        user = request.user
        arrow=Arrows.objects.get(parent=user)
        arrow.life = True
        arrow.left = 500
        arrow.top = 500
        arrow.speed = 8
        arrow.angle = 0
        arrow.save()
        return render(request, 'war/pvp.html',)

    def post(self, request):
        '''返回箭头、子弹位置及存活状态'''
        # 获取箭头信息并控制
        user = request.user
        arrow = Arrows.objects.get(parent=user)
        
        direction = request.POST.get('direction')
        upspeed = request.POST.get('upspeed')

        if direction == 'left':
          arrow.angle = arrow.angle - 6
        elif direction == 'right':
          arrow.angle = arrow.angle + 6

        if upspeed == 'up':
          arrow.speed = 16
        else:
          arrow.speed = 8
        arrow.save()
        if arrow.life == False:
          killed = True
        else:
          killed = False
        my_arrow = {'arrow_style':arrow.arrow_style, 
                    'weapon_style':arrow.weapon_style, 
                    'left':arrow.left, 
                    'top':arrow.top, 
                    'angle':arrow.angle,
                    'life':arrow.life,}
        
        # 获取其他箭头信息
        try:
            arrows = Arrows.objects.filter(Q(life=True)&~Q(parent=user))
        except:
            other_arrows = ''
        else:
            other_arrows = []
            for i in arrows:
                arrow_information = {'nickname':i.parent.nickname, 
                                     'arrow_style':i.arrow_style, 
                                     'weapon_style':i.weapon_style, 
                                     'left':i.left, 
                                     'top':i.top, 
                                     'angle':i.angle}
                other_arrows.append(arrow_information)
            if len(other_arrows) == 0:
              other_arrows = ''

        # 获取子弹信息
        try:
            bullets = Bullets.objects.filter(life=True)
        except:
            all_bullets = ''
        else:
            all_bullets = []
            for i in bullets:
                bullet_information = {'left':i.left, 
                                      'top':i.top, 
                                      'angle':i.angle}
                all_bullets.append(bullet_information)
        
        return JsonResponse({'my_arrow':my_arrow,
                             'other_arrows':other_arrows,
                             'bullets':all_bullets,
                             'killed':killed})

class PVP_Calc(LoginRequiredMixin, View):
    '''箭头位置计算'''
    def post(self, request):
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
          time.sleep(0.06)
          state = GameControl.objects.get(id=1)
          if state.position_calc == False:
            break


          try:
              arrows = Arrows.objects.filter(life=True)
              bullets = Bullets.objects.filter(life=True)
          except:
            pass
          else:
            for i in arrows:
              # 箭头移动计算
              x = i.left - 500
              y = i.top - 500
              if x**2 + y**2 >= 497**2 or i.left < 0 or i.top < 0:
                # 1.判断是否出界
                i.life = False
                i.left = 500
                i.top = 500
                i.speed = 8
                i.angle = 0
                i.save()
              else:
                # 2.判断是否相撞
                for n in arrows:
                  if n.parent.id > i.parent.id:
                    if (n.left-i.left)**2 + (n.top-i.top)**2 <= 7**2:
                      i.life = False
                      i.left = 500
                      i.top = 500
                      i.speed = 8
                      i.angle = 0
                      i.save()
                      n.life = False
                      n.left = 500
                      n.top = 500
                      n.speed = 8
                      n.angle = 0
                      n.save()

                for b in bullets:
                  if b.parent != i.parent:
                    if (b.left-i.left)**2 + (b.top-i.top)**2 <= 5**2:
                      i.life = False
                      i.left = 500
                      i.top = 500
                      i.speed = 8
                      i.angle = 0
                      i.save()
                  
                # 3.计算移动位置
                i.left = i.left + math.sin(math.pi*(i.angle)/180)*i.speed
                i.top = i.top - math.cos(math.pi*(i.angle)/180)*i.speed
                i.save()
          # 判断子弹是否出界
          try:
            bullets = Bullets.objects.filter(life=True)
          except:
            pass
          else:
            for b in bullets:
              b.left = b.left + math.sin(math.pi*(b.angle)/180)*b.speed
              b.top = b.top - math.cos(math.pi*(b.angle)/180)*b.speed
              b.save()
              if (b.left-500)**2 + (b.top-500)**2 >= 550**2 or b.left < 0 or b.top < 0:
                # 1.判断是否出界
                b.delete()
              
      return JsonResponse({'res':0})

class PVP_Createbullets(LoginRequiredMixin, View):
    '''子弹生成计算'''
    def post(self, request):
      user = request.user
      arrow = Arrows.objects.get(parent=user)
      Bullets.objects.create(parent=user, left=arrow.left, top=arrow.top, angle=arrow.angle)
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