from django.contrib import admin
from app.models import Planes
from app.models import Users
from app.models import PlaneStyle
from app.models import WeaponStyle
from app.models import Developer
from app.models import Enermys
from app.models import Bullets_Plane


# 自定义模型管理类


'''开发者管理类'''
class DeveloperAdmin(admin.ModelAdmin):
    '''开发者管理类'''
    list_display = ['id',
                    'position_calc',
                    'enermys_create',
                    'bullets_create',
                    ]
    actions_on_bottom = True


'''用户管理类'''
class UsersAdmin(admin.ModelAdmin):
    '''用户管理类'''
    # def show_all(self, obj):
    #     return Users.objects.filter(PlaneStyle__plane_index)
    list_display = ['id', 
                    'user_name', 
                    'password', 
                    'truename',
                    'score']
    actions_on_bottom = True


'''用户飞机管理类'''
class PlanesAdmin(admin.ModelAdmin):
    '''用户飞机管理类'''
    list_display = ['parent',
                    'plane_life',
                    'plane_style', 
                    'weapon_style', 
                    'plane_speed',
                    'plane_angle', 
                    'plane_ps_left', 
                    'plane_ps_top', 
                    ]
    actions_on_bottom = True


'''敌机管理类'''
class EnermysAdmin(admin.ModelAdmin):
    '''敌机管理类'''
    list_display = ['id',
                    'plane_life',
                    'plane_style', 
                    'weapon_style', 
                    'plane_speed',
                    'plane_angle', 
                    'plane_ps_left', 
                    'plane_ps_top', 
                    ]
    actions_on_bottom = True


'''飞机类型管理类'''
class PlaneStyleAdmin(admin.ModelAdmin):
    '''飞机类型管理类'''
    list_display = ['parent',
                    'plane_0', 
                    'plane_1', 
                    'plane_2', 
                    'plane_3',]
    actions_on_bottom = True


'''武器类型管理类'''
class WeaponStyleAdmin(admin.ModelAdmin):
    '''武器类型管理类'''
    list_display = ['parent',
                    'weapon_0', 
                    'weapon_1', 
                    'weapon_2', 
                    'weapon_3',]
    actions_on_bottom = True

'''子弹管理类'''
class Bullets_PlaneAdmin(admin.ModelAdmin):
    '''子弹管理类'''
    list_display = ['parent',
                    'bullet_style', 
                    'bullet_speed', 
                    'bullet_angle', 
                    'bullet_ps_left',
                    'bullet_ps_top',
                    'bullet_life',
                    ]
    actions_on_bottom = True


# Register your models here.
admin.site.register(Developer, DeveloperAdmin)
admin.site.register(Planes, PlanesAdmin)
admin.site.register(Users, UsersAdmin)
admin.site.register(PlaneStyle, PlaneStyleAdmin)
admin.site.register(WeaponStyle, WeaponStyleAdmin)
admin.site.register(Enermys, EnermysAdmin)
admin.site.register(Bullets_Plane, Bullets_PlaneAdmin)
