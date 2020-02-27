from django.db import models

# Create your models here.

'''用户管理类'''
class UserManager(models.Manager):
    '''用户管理类'''


    def create(self,user_name,password,truename):
        # 1.创建一个用户对象
        # 获取self所在的模型类
        model_class = self.model
        user = model_class()
        user.user_name = user_name
        user.password = password
        user.truename = truename
        # 2.保存进数据库
        user.save()
        # 3.返回对象
        return user


'''开发者类'''
class Developer(models.Model):
    '''开发者类'''
    class Meta:
        verbose_name='开发者'
        verbose_name_plural = '开发者'

    # 位置计算函数
    position_calc = models.BooleanField(verbose_name='位置计算状态', default=False)

    # 敌机生成函数
    enermys_create = models.BooleanField(verbose_name='敌机生成状态', default=False)

    # def __str__(self):
    #     # 返回用户名
    #     return '开发者'


'''用户类'''
class Users(models.Model):
    '''用户类'''
    
    class Meta:
        verbose_name='用户信息'
        verbose_name_plural = '用户信息'
            
    # 用户名
    user_name = models.CharField(verbose_name='用户名', max_length=30)
    # 密码
    password = models.CharField(verbose_name='密码', max_length=8)
    # 真实姓名
    truename = models.CharField(verbose_name='真实姓名', max_length=30)
    # 分数
    score = models.IntegerField(verbose_name='分数', default=0)
    # 登录状态
    # login_state = models.IntegerField(verbose_name='登录状态', default=0)


    # 自定义一个管理类对象
    objects = UserManager()
    

    def __str__(self):
        # 返回用户名
        return self.user_name


'''飞机样式类'''
class PlaneStyle(models.Model):
    '''飞机样式类'''

    class Meta:
        verbose_name='飞机样式'
        verbose_name_plural = '飞机样式'

    # 默认飞机样式
    plane_0 = models.BooleanField(verbose_name='默认样式', default=True)
    # 飞机样式1
    plane_1 = models.BooleanField(verbose_name='样式1', default=False)
    # 飞机样式2
    plane_2 = models.BooleanField(verbose_name='样式1', default=False)
    # 飞机样式3
    plane_3 = models.BooleanField(verbose_name='样式1', default=False)
    # 关联用户类
    parent = models.ForeignKey(Users,on_delete=models.CASCADE, verbose_name='用户') 


'''武器样式类'''
class WeaponStyle(models.Model):
    '''武器样式类'''

    class Meta:
        verbose_name='武器样式'
        verbose_name_plural = '武器样式'

    # 默认武器样式
    weapon_0 = models.BooleanField(verbose_name='默认样式', default=True)
    # 武器样式1
    weapon_1 = models.BooleanField(verbose_name='样式1', default=False)
    # 武器样式2
    weapon_2 = models.BooleanField(verbose_name='样式2', default=False)
    # 武器样式3
    weapon_3 = models.BooleanField(verbose_name='样式3', default=False)
    # 关联用户类
    parent = models.ForeignKey(Users,on_delete=models.CASCADE, verbose_name='用户')


# 飞机类
class Planes(models.Model):
    '''飞机类'''

    class Meta:
        verbose_name='飞机信息'
        verbose_name_plural = '飞机信息'


    # 地图大小
    map_width = 1000
    view_width = 400

    # 飞机类型
    plane_style = models.FloatField(verbose_name='飞机类型', default=1)
    # 武器类型
    weapon_style = models.FloatField(verbose_name='武器类型', default=1)
    # 飞机速度
    plane_speed = models.FloatField(verbose_name='速度', default=1)
    # 飞机角度
    plane_angle = models.FloatField(verbose_name='角度', default=0)
    # 飞机位置x
    plane_ps_left = models.FloatField(verbose_name='位置x', default=map_width/2)
    # 飞机位置y
    plane_ps_top = models.FloatField(verbose_name='位置y', default=map_width/2)
    # 地图位置x
    map_ps_left = models.FloatField(verbose_name='位置x', default=(view_width-map_width)/2)
    # 地图位置y
    map_ps_top = models.FloatField(verbose_name='位置y', default=(view_width-map_width)/2)

    # 是否存活
    plane_life = models.BooleanField(verbose_name='是否存活', default=False)
    # 关联用户类
    parent = models.ForeignKey(Users,on_delete=models.CASCADE, verbose_name='用户')

    def __str__(self):
        # 返回飞机id
        return self.parent.user_name


# 敌机类
class Enermys(models.Model):
    '''敌机类'''

    class Meta:
        verbose_name='敌机信息'
        verbose_name_plural = '敌机信息'

    # 敌机类型
    plane_style = models.FloatField(verbose_name='敌机类型', default=1)
    # 武器类型
    weapon_style = models.FloatField(verbose_name='武器类型', default=1)
    # 敌机速度
    plane_speed = models.FloatField(verbose_name='速度', default=1)
    # 敌机角度
    plane_angle = models.FloatField(verbose_name='角度', default=0)
    # 敌机位置x
    plane_ps_left = models.FloatField(verbose_name='位置x', default=0)
    # 敌机位置y
    plane_ps_top = models.FloatField(verbose_name='位置y', default=0)
    # 是否存活
    plane_life = models.BooleanField(verbose_name='是否存活', default=True)
