from django.contrib import admin
from apps.war.models import Arrows, Bullets

'''箭头管理类'''
class ArrowsAdmin(admin.ModelAdmin):
    '''箭头管理类'''
    list_display = ['parent',
                    'left',
                    'top',
                    'speed',
                    'angle',
                    'arrow_style',
                    'weapon_style',
                    'life',
                    'status',
                    ]
    actions_on_bottom = True


'''子弹管理类'''
class BulletsAdmin(admin.ModelAdmin):
    '''子弹管理类'''
    list_display = ['parent',
                    'left',
                    'top',
                    'speed',
                    'angle',
                    'life',
                    ]
    actions_on_bottom = True


admin.site.register(Arrows, ArrowsAdmin)
admin.site.register(Bullets, BulletsAdmin)