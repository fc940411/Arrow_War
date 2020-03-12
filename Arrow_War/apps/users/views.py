from django.views.generic import View # 通过类视图来写view
from django.shortcuts import render, redirect  # 重定向函数,直接输入url 
from django.http import HttpResponse, JsonResponse
from django.template import loader, RequestContext
from apps.users.models import Users, Score
from django.db.models import Q
import json
import math
import time
import threading
import random


class Index(View):
    '''首页'''
    def get(self, request):
        return render(request, 'users/index.html')


class Register(View):
    '''注册页'''
    def get(self, request):
        return render(request, 'users/register.html')