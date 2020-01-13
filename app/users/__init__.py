# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2019/6/4 22:51
# Author :  Richard
# File   :  __init__.py.py

# users针对用户逻辑处理的目录
# __init__.py 针对用户业务逻辑的初始化操作

# 将flask框架的蓝图导入
from flask import Blueprint
# 构建蓝图程序
users = Blueprint("users", __name__)
# 导入当前包的路由和视图函数
from . import views
