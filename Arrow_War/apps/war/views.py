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
        direction = request.POST.get('direction')
        upspeed = request.POST.get('upspeed')
        #--------连接数据库----------
        connection = pymysql.connect(host='localhost',
                         user='root',
                         password='mysql',
                         db='arrow_war',
                         charset='utf8',
                         cursorclass=pymysql.cursors.DictCursor)
        #--------控制自身箭头----------
        try:
          with connection.cursor() as cursor:
            # 获取箭头信息
            sql = "SELECT `left`,top,angle,life FROM war_arrows WHERE parent_id = %s" % user.id
            cursor.execute(sql)
            arrow = cursor.fetchone()
            if direction == 'left':
              angle = int(arrow['angle']) - 6
              sql = "UPDATE war_arrows SET angle = %s WHERE parent_id = %s" % (str(angle), user.id)
              cursor.execute(sql)
              connection.commit()
            elif direction == 'right':
              angle = int(arrow['angle']) + 6
              sql = "UPDATE war_arrows SET angle = %s WHERE parent_id = %s" % (str(angle), user.id)
              cursor.execute(sql)
              connection.commit()
            else:
              angle = arrow['angle']



            if upspeed == 'up':
              speed = 16
              sql = "UPDATE war_arrows SET speed = %s WHERE parent_id = %s" % (str(speed), user.id)
              cursor.execute(sql)
              connection.commit()
            else:
              speed = 8
              sql = "UPDATE war_arrows SET speed = %s WHERE parent_id = %s" % (str(speed), user.id)
              cursor.execute(sql)
              connection.commit()
            if arrow['life'] == False:
              killed = True
            else:
              killed = False
        except:
          pass
  
        my_arrow = {'left':arrow['left'], 
                    'top':arrow['top'], 
                    'angle':angle,
                    'life':arrow['life'],}
        #--------获取其余箭头和子弹信息----------
        try:
          with connection.cursor() as cursor:
            # 获取其他箭头信息
            sql1 = "SELECT `left`,top,angle FROM war_arrows WHERE life = True AND parent_id <> %s" % user.id
            cursor.execute(sql1)
            arrows = cursor.fetchall()
            # 获取子弹信息
            sql2 = "SELECT `left`,top,angle FROM war_bullets WHERE life = True"
            cursor.execute(sql2)
            bullets = cursor.fetchall()
        except:
          other_arrows = ''
          all_bullets = ''
        else:
          other_arrows = []
          for i in arrows:
            arrow_information = {'left':i['left'], 
                                 'top':i['top'], 
                                 'angle':i['angle']}
            other_arrows.append(arrow_information)
          if len(other_arrows) == 0:
            other_arrows = ''

          all_bullets = []
          for i in bullets:
            bullet_information = {'left':i['left'], 
                                 'top':i['top'], 
                                 'angle':i['angle']}
            all_bullets.append(bullet_information)
          if len(all_bullets) == 0:
            all_bullets = ''
        finally:
          connection.close()


        return JsonResponse({'my_arrow':my_arrow,
                             'other_arrows':other_arrows,
                             'bullets':all_bullets,
                             'killed':killed})

class PVP_Calc(LoginRequiredMixin, View):
    '''箭头位置计算'''
    def arrow_calc(self, i, arrows, bullets, cursor, connection):
      # 箭头移动计算
      x = i['left'] - 500
      y = i['top'] - 500
      if x**2 + y**2 >= 497**2 or i['left'] < 0 or i['top'] < 0:
        # 1.判断是否出界
        sql1 = "UPDATE war_arrows SET life = False WHERE parent_id = %s" % i['parent_id']
        cursor.execute(sql1)
        connection.commit()
      else:
        # 2.判断是否相撞
        for n in arrows:
          if n['parent_id'] > i['parent_id']:
            if (n['left']-i['left'])**2 + (n['top']-i['top'])**2 <= 7**2:
              sql1 = "UPDATE war_arrows SET life = False WHERE parent_id = %s" % i['parent_id'] 
              cursor.execute(sql1)
              connection.commit()
              sql2 = "UPDATE war_arrows SET life = False WHERE parent_id = %s" % n['parent_id']
              cursor.execute(sql2)
              connection.commit()

        for b in bullets:
          if b['parent_id'] != i['parent_id']:
            if (b['left']-i['left'])**2 + (b['top']-i['top'])**2 <= 5**2:
              sql1 = "UPDATE war_arrows SET life = False WHERE parent_id = %s" % i['parent_id']
              cursor.execute(sql1)
              connection.commit()
              
          
        # 3.计算移动位置
        x = i['left'] + math.sin(math.pi*(i['angle'])/180)*i['speed']
        y = i['top'] - math.cos(math.pi*(i['angle'])/180)*i['speed']
        sql3 = "UPDATE war_arrows SET `left` = %s WHERE parent_id = %s" % (str(x), i['parent_id'])
        cursor.execute(sql3)
        sql4 = "UPDATE war_arrows SET top = %s WHERE parent_id = %s" % (str(y), i['parent_id'])
        cursor.execute(sql4)
        connection.commit()

    def bullet_calc(self, b, cursor, connection):
      x = b['left'] + math.sin(math.pi*(b['angle'])/180)*b['speed']
      y = b['top'] - math.cos(math.pi*(b['angle'])/180)*b['speed']
      sql1 = "UPDATE war_bullets SET `left` = %s WHERE id = %s" % (str(x), b['id'])
      cursor.execute(sql1)
      sql2 = "UPDATE war_bullets SET top = %s WHERE id = %s" % (str(y), b['id'])
      cursor.execute(sql2)
      connection.commit()
      if (b['left']-500)**2 + (b['top']-500)**2 >= 550**2 or b['left'] < 0 or b['top'] < 0:
        # 1.判断是否出界
        sql3 = "DELETE FROM war_bullets WHERE id = %s" % b['id']
        cursor.execute(sql3)
        connection.commit()


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
          start_time = time.time()
          
          
          state = GameControl.objects.get(id=1)
          if state.position_calc == False:
            break

          # 用pymysql连接数据库提高数据读取效率
          connection = pymysql.connect(host='localhost',
                           user='root',
                           password='mysql',
                           db='arrow_war',
                           charset='utf8',
                           cursorclass=pymysql.cursors.DictCursor)
          try:
            with connection.cursor() as cursor:
              # 读取单条记录
              sql = "SELECT parent_id,`left`,top,angle,speed,id FROM war_bullets"
              cursor.execute(sql)
              bullets = cursor.fetchall()
              for b in bullets:
                gevent.joinall([
                  gevent.spawn(self.bullet_calc, b, cursor, connection)
                ])
            with connection.cursor() as cursor:
              # 读取单条记录
              sql = "SELECT parent_id,`left`,top,angle,speed FROM war_arrows WHERE life = True"
              cursor.execute(sql)
              arrows = cursor.fetchall()
              for i in arrows:
                gevent.joinall([
                  gevent.spawn(self.arrow_calc, i, arrows, bullets, cursor, connection)
                ])
          finally:
            connection.close()
          end_time = time.time()
          t = round(end_time-start_time, 3)
          if t < 0.06:
            time.sleep(0.06 - t)
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