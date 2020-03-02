from django.shortcuts import render, redirect  # 重定向函数,直接输入url 
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from app.models import Users, PlaneStyle, WeaponStyle, Planes, Enermys, Developer, Bullets_Plane
from django.db.models import Q
import json
import math
import time
import threading
import random


# Create your views here.
w1 = 1000  # 战场地图大小

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
        PlaneStyle.objects.create(parent_id=user_id.id)
        WeaponStyle.objects.create(parent_id=user_id.id)
        Planes.objects.create(parent_id=user_id.id, plane_ps_left=w1/2, plane_ps_top=w1/2)
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

    # 获取子弹
    try:
        bullets = Bullets_Plane.objects.filter(bullet_life=True)
    except:
        all_bullets = ''
    else:
        all_bullets = []
        for i in bullets:
            bullet_information = {'bullet_style':i.bullet_style,  
                                  'left':i.bullet_ps_left, 
                                  'top':i.bullet_ps_top, 
                                  'angle':i.bullet_angle}
            all_bullets.append(bullet_information)
    
    return JsonResponse({'war_map':w1,
                         'speed':plane.plane_speed,
                         'angle':plane.plane_angle,
                         'left':plane.plane_ps_left,
                         'top':plane.plane_ps_top,
                         'life':plane.plane_life,
                         'other_planes':other_planes,
                         'enermys':all_enermys,
                         'bullets':all_bullets,
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
        plane.plane_angle = plane.plane_angle - 1.5
    elif direction == 'right':
        plane.plane_angle = plane.plane_angle + 1.5
    plane.save()

    return JsonResponse({'res':'finish'})

# 设置session
def set_session(request):
    '''设置session'''
    user_id = request.POST.get('user_id')
    request.session['user_id'] = int(user_id)
    request.session['islogin'] = True
    request.session.set_expiry(0)
    return HttpResponse('设置成功!')

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
    try:
        state = Developer.objects.get(id=1)
        state_enemy_create = request.POST.get('state_enemy_create')
    except Exception as r:
        print(r)
    else:
        if state_enemy_create == '1':
            state.enermys_create = False
            state.save()
        elif state_enemy_create == '0':
            state.enermys_create = True
            state.save()


    while True:
        state = Developer.objects.get(id=1)
        if state.enermys_create == False:
            break
        time.sleep(3)
        
        pos = random.random()

        if pos >= 0 and pos < 0.25:
            angle = 0
            speed = -5
            left = pos/0.25*(w1-100)+50
            top = 0
        elif pos >= 0.25 and pos < 0.5:    
            angle = 90
            speed = -5
            left = w1
            top = (pos-0.25)/0.25*(w1-100)+50
        elif pos >= 0.5 and pos < 0.75:    
            angle = 180
            speed = -5
            left = (pos-0.5)/0.25*(w1-100)+50
            top = w1
        elif pos >= 0.75 and pos <= 1:    
            angle = 270
            speed = -5
            left = 0
            top = (pos-0.75)/0.25*(w1-100)+50
        # 创建敌机
        Enermys.objects.create(plane_speed = speed, plane_angle = angle, plane_ps_left = left, plane_ps_top = top)
    return HttpResponse('生成敌机!') 

# 子弹生成函数
def bullets_create(request):
    # 子弹5*11
    print('子弹生成函数开始运行!')
    try:
        state = Developer.objects.get(id=1)
        state_bullets_create = request.POST.get('state_bullets_create')
    except Exception as r:
        print(r)
    else:
        if state_bullets_create == '1':
            state.bullets_create = False
            state.save()
        elif state_bullets_create == '0':
            state.bullets_create = True
            state.save()


    while True:
        state = Developer.objects.get(id=1)
        if state.bullets_create == False:
            break
        time.sleep(3)
        try:
            planes = Planes.objects.filter(plane_life=True)
        except:
            pass
        else:
            for i in planes:
                # 创建子弹
                Bullets_Plane.objects.create(parent_id = i.parent.id,
                                             bullet_speed = (i.plane_speed+20), 
                                             bullet_angle = i.plane_angle, 
                                             # 敌机57*43  飞机46*57  子弹5*11
                                             # bullet_ps_left = (i.plane_ps_left+math.cos(math.pi*i.plane_angle/180)*20), 
                                             # bullet_ps_top = (i.plane_ps_top+math.sin(math.pi*i.plane_angle/180)*20),
                                             bullet_ps_left = (i.plane_ps_left+math.sin(math.pi*i.plane_angle/180)*28.5), 
                                             bullet_ps_top = (i.plane_ps_top-math.cos(math.pi*i.plane_angle/180)*28.5),
                                             bullet_life = True, 
                                             )
    return HttpResponse('生成子弹!') 

# 位置计算函数
allpositions = []
def position_list(allpositions):
    try:
        planes = Planes.objects.filter(plane_life=True)
    except:
        pass
    else:
        for i in planes:
            allpositions.append({'plane_id':i.parent.id, 'left':i.plane_ps_left, 'top':i.plane_ps_top, 'angle':i.plane_angle, 'style':'plane'})

    try:
        enemys = Enermys.objects.filter(plane_life=True)
    except:
        pass
    else:
        for i in enemys:
            allpositions.append({'plane_id':i.id, 'left':i.plane_ps_left, 'top': i.plane_ps_top, 'angle':i.plane_angle, 'style':'enemy'})
def position_repeat(i, type):
    # 根据速度和角度,计算飞机位置和地图位置
    if type == 'plane' or type == 'enemy':
        left = i.plane_ps_left + math.sin(math.pi*(i.plane_angle)/180)*i.plane_speed
        top = i.plane_ps_top - math.cos(math.pi*(i.plane_angle)/180)*i.plane_speed
        i.plane_ps_left = left
        i.plane_ps_top = top
        i.save()
    elif type == 'bullet':
        bullet_left = i.bullet_ps_left + math.sin(math.pi*(i.bullet_angle)/180)*i.bullet_speed
        bullet_top = i.bullet_ps_top - math.cos(math.pi*(i.bullet_angle)/180)*i.bullet_speed
        i.bullet_ps_left = bullet_left
        i.bullet_ps_top = bullet_top
        i.save()

    # 判断是否撞墙
    if type == 'plane':
        x = i.plane_ps_left - w1/2
        y = i.plane_ps_top - w1/2
        if x**2+ y**2 >= (w1/2-23)**2 or left < 0 or top < 0:
            i.plane_life = False
            i.plane_ps_left = w1/2
            i.plane_ps_top = w1/2
            i.plane_angle = 0
            i.save()
    elif type == 'enemy':
        if i.plane_ps_left >= w1 or i.plane_ps_top >= w1 or i.plane_ps_left < 0 or i.plane_ps_top < 0:
            i.delete()
    elif type == 'bullet':
        x = i.bullet_ps_left - w1/2 
        y = i.bullet_ps_top - w1/2
        if (x*x)+(y*y) >= w1*w1/4 or i.bullet_ps_left < 0 or i.bullet_ps_top < 0:
            i.delete()
def position_calc(request):
    print('位置计算函数开始运行!')
    try:
        state = Developer.objects.get(id=1)
        state_position_calc = request.POST.get('state_position_calc')
    except Exception as r:
        print(r)
    else:
        if state_position_calc == '1':
            state.position_calc = False
            state.save()
        elif state_position_calc == '0':
            state.position_calc = True
            state.save()

    while True:
        allpositions = []
        position_list(allpositions)
        state = Developer.objects.get(id=1)
        if state.position_calc == False:
            break
        time.sleep(0.06)

        # 获取所有存活敌机
        try:
            enermys = Enermys.objects.filter(plane_life=True)
        except:
            pass
        else:
            for i in enermys:
                position_repeat(i, 'enemy')

        # 获取所有存活英雄飞机
        try:
            planes = Planes.objects.filter(plane_life=True)
        except:
            pass
        else:
            for i in planes:
                position_repeat(i, 'plane')

                # 判断飞机是否撞到敌机
                # 敌机57*43  飞机46*57  子弹5*11
                for p in allpositions:
                    if i.parent.id != p['plane_id']:
                        if (i.plane_ps_left-p['left'])**2 + (i.plane_ps_top-p['top'])**2 <= 1980:
                            i.plane_life = False
                            i.plane_ps_left = w1/2
                            i.plane_ps_top = w1/2
                            i.plane_angle = 0
                            i.save()
                            enermy = Enermys.objects.get(id=p['plane_id'])
                            enermy.delete()

        # 获取所有存活子弹
        try:
            bullets = Bullets_Plane.objects.filter(bullet_life=True)
        except:
            pass
        else:
            for i in bullets:
                user_id = request.session.get('user_id')
                position_repeat(i, 'bullet')
                # 判断子弹是否击中飞机
                # 敌机57*43  飞机46*57  子弹5*11
                for p in allpositions:
                    if (i.bullet_ps_left-p['left'])**2 + (i.bullet_ps_top-p['top'])**2 <= 576:
                        if p['style'] == 'plane':
                            plane = Planes.objects.get(parent_id=p['plane_id'])
                            if p['plane_id'] != user_id:
                                print(p['plane_id'],type(p['plane_id']),user_id,type(p['plane_id']))
                                plane.plane_life = False
                                plane.plane_ps_left = w1/2
                                plane.plane_ps_top = w1/2
                                plane.plane_angle = 0
                                plane.save()
                        elif p['style'] == 'enemy':
                            try:
                                enemy = Enermys.objects.get(id=p['plane_id'])
                            except:
                                pass
                            else:
                                enemy.delete()
                                user = Users.objects.get(id=user_id)
                                user.score = user.score + 1
                                user.save()
                                i.delete()

    if state.position_calc == True:
        return HttpResponse('开启完成!')
    else:
        return HttpResponse('关闭完成')

# 测试页面
def war_test(request):

    return render(request, 'app/war_test.html')

# 测试页面操作
def war_test_handle(request):

    state = Developer.objects.get(id=1)

    return JsonResponse({'position_calc':state.position_calc,
                         'enermys_create':state.enermys_create,
                         'bullets_create':state.bullets_create,
                        })