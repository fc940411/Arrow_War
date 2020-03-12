from django.contrib import admin
from apps.users.models import Users, Score

'''用户管理类'''
class UsersAdmin(admin.ModelAdmin):
    '''用户管理类'''
    list_display = ['id',
                    'username',
                    'email',
                    'password',
                    ]
    actions_on_bottom = True

'''成绩管理类'''
class ScoreAdmin(admin.ModelAdmin):
    '''成绩管理类'''
    list_display = ['parent',
                    'times',
                    'scores',
                    'kills',
                    ]
    actions_on_bottom = True


admin.site.register(Users, UsersAdmin)
admin.site.register(Score, ScoreAdmin)