from django.shortcuts import render, redirect  # 重定向函数,直接输入url 
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from app.models import Users, PlaneStyle, WeaponStyle, Planes, Enermys, Developer
from django.db.models import Q
import json
import math
import time
import threading
import random


# Create your views here.
w1 = 1000  # 战场地图大小
w2 = 400  # 窗口大小


# 首页,即登录页
def index(request):

    return render(request, 'app/index.html')

# 登录确认
def login_check(request):
    '''登录校验'''
    username = request.POST.get('username')
    password = request.POST.get('password')

    
    try:
        check=Users.objects.get(Q(user_name__exact=username)&Q(password__exact=password))
    except:
        return JsonResponse({'res':'wrong'})
    else:
        return JsonResponse({'res':str(check.id)})

# 注册页
def register(request):

    return render(request, 'app/register.html')

# 注册页操作
def register_handle(request):
    '''注册校验'''
    username = request.POST.get('username')
    password = request.POST.get('password')
    truename = request.POST.get('truename')

    
    try:
        check=Users.objects.get(Q(user_name__exact=username))
    except:
        Users.objects.create(username,password,truename)
        user_id = Users.objects.get(Q(user_name__exact=username)&Q(password__exact=password))
        print(user_id,type(user_id),user_id.id)
        PlaneStyle.objects.create(parent_id=user_id.id)
        WeaponStyle.objects.create(parent_id=user_id.id)
        Planes.objects.create(parent_id=user_id.id)
        return JsonResponse({'res':1})
    else:
        return JsonResponse({'res':0})

# 个人页
def personal(request):

    return render(request, 'app/personal.html')

# 个人页操作
def personal_handle(request):
    '''个人主页操作'''
    user_id = request.session.get('user_id')
    dic = {'plane':[],'weapon':[]}
    try:
        PlaneStyle.objects.get(Q(plane_0=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['plane'].append(0)

    try:
        PlaneStyle.objects.get(Q(plane_1=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['plane'].append(1)

    try:
        PlaneStyle.objects.get(Q(plane_2=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['plane'].append(2)

    try:
        PlaneStyle.objects.get(Q(plane_3=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['plane'].append(3)

    try:
        WeaponStyle.objects.get(Q(weapon_0=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['weapon'].append(0)

    try:
        WeaponStyle.objects.get(Q(weapon_1=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['weapon'].append(1)

    try:
        WeaponStyle.objects.get(Q(weapon_2=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['weapon'].append(2)

    try:
        WeaponStyle.objects.get(Q(weapon_3=True)&Q(parent=user_id))
    except:
        pass
    else:
        dic['weapon'].append(3)
    return JsonResponse(dic)

# 战场页
def war(request):
    # 1.获取飞机
    user_id = request.session.get('user_id')
    plane = Planes.objects.get(parent=user_id)
    # 2.判断飞机是否存活,如未存活则给一条命
    if plane.plane_life == False:
        plane.plane_life = True
        plane.save()
    return render(request, 'app/war.html')

# 战场页操作
def war_handle(request):
    # 1.获取飞机
    user_id = request.session.get('user_id')
    plane = Planes.objects.get(parent=user_id)
    speed = plane.plane_speed  # 速度
    angle = plane.plane_angle  # 角度
    left = plane.plane_ps_left  # 位置x
    top = plane.plane_ps_top  # 位置y
    map_left  = plane.map_ps_left  # 地图位置x
    map_top  = plane.map_ps_top  # 地图位置y
    life = plane.plane_life  # 是否存活

    # 获取其他飞机
    try:
        planes = Planes.objects.filter(Q(plane_life=True)&~Q(parent=user_id))
    except:
        other_planes = ''
    else:
        other_planes = []
        for i in planes:
            plane_information = {'plane_style':i.plane_style, 
                                 'weapon_style':i.weapon_style, 
                                 'left':i.plane_ps_left, 
                                 'top':i.plane_ps_top, 
                                 'angle':i.plane_angle}
            other_planes.append(plane_information)

    # 获取其他敌机
    try:
        enermys = Enermys.objects.filter(plane_life=True)
    except:
        all_enermys = ''
    else:
        all_enermys = []
        for i in enermys:
            enermy_information = {'plane_style':i.plane_style, 
                                 'weapon_style':i.weapon_style, 
                                 'left':i.plane_ps_left, 
                                 'top':i.plane_ps_top, 
                                 'angle':i.plane_angle}
            all_enermys.append(enermy_information)


    return JsonResponse({'war_map':w1,
                         'map':w2,
                         'speed':speed,
                         'angle':angle,
                         'left':left,
                         'top':top,
                         'life':life,
                         'map_top':map_top,
                         'map_left':map_left,
                         'other_planes':other_planes,
                         'enermys':all_enermys,
                        })

# 操作飞机
def plane_handle(request):
    '''操作飞机'''
    # 1.获取飞机
    user_id = request.session.get('user_id')
    plane = Planes.objects.get(parent=user_id)
    # 2.获取方向
    direction = request.POST.get('direction')
    if direction == 'left':
        plane.plane_angle = plane.plane_angle - 0.5
    elif direction == 'right':
        plane.plane_angle = plane.plane_angle + 0.5
    plane.save()

    return JsonResponse({'res':'finish'})

# 设置session
def set_session(request):
    '''设置session'''
    user_id = request.POST.get('user_id')
    request.session['user_id'] = int(user_id)
    request.session['islogin'] = True
    request.session.set_expiry(0)
    return HttpResponse()

# 用户登出操作
def logout(request):
    '''用户退出登录'''

    # 1.获取飞机
    user_id = request.session.get('user_id')
    plane = Planes.objects.get(parent=user_id)
    # 2.判断飞机是否存活,如存活则死亡
    if plane.plane_life == True:
        plane.plane_life = False
        plane.save()
    return JsonResponse({'res':1})

# 敌机生成操作
def enermys_create(request):
    print('敌机生成函数开始运行!')
    while True:
        state = Developer.objects.get(id=1)
        if state.enermys_create == False:
            break
        time.sleep(5)
        
        pos = random.random()

        if pos >= 0 and pos < 0.25:
            angle = 0
            speed = -1
            left = pos/0.25*(w1-100)+50
            top = 0
        elif pos >= 0.25 and pos < 0.5:    
            angle = 90
            speed = -1
            left = w1
            top = (pos-0.25)/0.25*(w1-100)+50
        elif pos >= 0.5 and pos < 0.75:    
            angle = 180
            speed = -1
            left = (pos-0.5)/0.25*(w1-100)+50
            top = w1
        elif pos >= 0.75 and pos <= 1:    
            angle = 270
            speed = -1
            left = 0
            top = (pos-0.75)/0.25*(w1-100)+50
        print(pos, angle, left, top)
        # 创建敌机
        Enermys.objects.create(plane_speed = speed, plane_angle = angle, plane_ps_left = left, plane_ps_top = top)
    return HttpResponse('生成敌机!') 

# 位置计算函数
def position_calc(request):
    print('位置计算函数开始运行!')
    while True:
        state = Developer.objects.get(id=1)
        if state.position_calc == False:
            break
        time.sleep(0.02)
        # 获取所有存活英雄飞机
        try:
            planes = Planes.objects.filter(plane_life=True)
        except:
            pass
        else:
            for i in planes:
                speed = i.plane_speed  # 速度
                angle = i.plane_angle  # 角度
                left = i.plane_ps_left  # 位置x
                top = i.plane_ps_top  # 位置y
                map_left  = i.map_ps_left  # 地图位置x
                map_top  = i.map_ps_top  # 地图位置y
                life = i.plane_life  # 是否存活
                # print('前',map_left,map_top)
                # 2.根据速度和角度,计算飞机位置和地图位置
                left = left + math.sin(math.pi*(angle)/180)*speed
                top = top - math.cos(math.pi*(angle)/180)*speed
                map_left= (w2-w1)/2 - (left-(w1-46)/2)
                map_top = (w2-w1)/2 - (top-(w1-46)/2)
                i.plane_ps_left = left
                i.plane_ps_top = top
                i.map_ps_left = map_left
                i.map_ps_top = map_top
                i.save()

                # 3.判断飞机是否坠毁
                x = left - w1/2 
                y = top - w1/2
                if (x*x)+(y*y) >= w1*w1/4:
                    i.plane_life = False
                    i.plane_ps_left = w1/2
                    i.plane_ps_top = w1/2
                    i.plane_angle = 0
                    i.save()

        # 获取所有存活敌机
        try:
            enermys = Enermys.objects.filter(plane_life=True)
        except:
            pass
        else:
            for i in enermys:
                speed = i.plane_speed  # 速度
                angle = i.plane_angle  # 角度
                left = i.plane_ps_left  # 位置x
                top = i.plane_ps_top  # 位置y
                life = i.plane_life  # 是否存活

                # 2.根据速度和角度,计算飞机位置和地图位置
                left = left + math.sin(math.pi*(angle)/180)*speed
                top = top - math.cos(math.pi*(angle)/180)*speed
     
                # 3.输出敌机位置
                i.plane_ps_left = left
                i.plane_ps_top = top
                i.save()    

                # 4.判断飞机是否坠毁
                if left >= w1 or top >= w1 or left < 0 or top < 0:
                    i.delete()



    if state.position_calc == True:
        return HttpResponse('开启完成')
    else:
        return HttpResponse('关闭完成')