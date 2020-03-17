from django.db import models
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Users(AbstractUser, BaseModel):
    '''用户模型类'''
    class Meta:
        verbose_name='用户信息'
        verbose_name_plural = '用户信息'

    nickname = models.CharField(verbose_name='昵称', max_length=30)


class Score(BaseModel):
    '''用户成绩类'''
    class Meta:
        verbose_name='用户成绩'
        verbose_name_plural = '用户成绩'


    parent = models.ForeignKey(Users,on_delete=models.CASCADE, verbose_name='用户')
    times = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='生存时间', default=0)
    scores = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='分数', default=0)
    kills = models.IntegerField(verbose_name='击杀数', default=0)
