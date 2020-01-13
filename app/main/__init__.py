# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2019/6/4 22:51
# Author :  Richard
# File   :  __init__.py.py

# main 包含主要的业务逻辑的路由和视图函数
# __init__.py  对主业务逻辑程序的初始化操作

# 将flask框架的蓝图导入
from flask import Blueprint
# 构建蓝图程序
main = Blueprint("main", __name__)
# 导入当前包的路由和视图函数
from . import views

