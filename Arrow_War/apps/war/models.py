from django.db import models
from db.base_model import BaseModel
from apps.users.models import Users
# Create your models here.

class Arrows(BaseModel):
    '''箭头类'''
    class Meta:
        verbose_name='箭头'
        verbose_name_plural = '箭头'

    parent = models.ForeignKey(Users,on_delete=models.CASCADE, verbose_name='用户')
    left = models.FloatField(verbose_name='位置x', default=0)
    top = models.FloatField(verbose_name='位置y', default=0)
    speed = models.FloatField(verbose_name='速度', default=0)
    angle = models.FloatField(verbose_name='角度', default=0)
    arrow_style = models.IntegerField(verbose_name='箭头类型', default=0)
    weapon_style = models.IntegerField(verbose_name='武器类型', default=0)
    life = models.BooleanField(verbose_name='是否生存', default=0)
    status = models.IntegerField(verbose_name='箭头状态', default=0)


class Bullets(BaseModel):
    '''子弹类'''
    class Meta:
        verbose_name='子弹'
        verbose_name_plural = '子弹'

    parent = models.ForeignKey(Users,on_delete=models.CASCADE, verbose_name='用户')
    left = models.FloatField(verbose_name='位置x', default=0)
    top = models.FloatField(verbose_name='位置y', default=0)
    speed = models.FloatField(verbose_name='速度', default=0)
    angle = models.FloatField(verbose_name='角度', default=0)
    life = models.BooleanField(verbose_name='是否生存', default=0)
