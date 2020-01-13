# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2019/6/4 22:49
# Author :  Richard
# File   :  __init__.py.py

# app下的__init__.py文件
# 将整个应用初始化
# 主要工作
#     1：构建flask应用以及各种配置
#     2：构建SQLAlchemy的应用
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql
import os
# 将pymysql注册为mysql的驱动
pymysql.install_as_MySQLdb()

db = SQLAlchemy()


def create_app():
    # 定义系统路径的变量
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    BASE_DIR = os.path.join(BASE_DIR, 'app')
    # 定义静态文件的路径
    static_dir = os.path.join(BASE_DIR, 'static')
    # 定义模板文件的路径
    templates_dir = os.path.join(BASE_DIR, 'templates')
    app = Flask(__name__, static_folder=static_dir, template_folder=templates_dir)
    # 配置启动模式为调试模式
    app.config["DEBUG"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    # 配置数据库的连接
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:lx201091@127.0.0.1:3306/online_book"
    # 配置数据库内容在更新时自动提交
    app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"] = True
    # 配置session所需要的秘钥
    app.config["SECRET_KEY"] = "Paispasswordkey"
    # 查询时会显示原始SQL语句
    app.config['SQLALCHEMY_ECHO'] = True
    # 数据库的初始化
    db.app = app
    db.init_app(app)
    # 将main蓝图程序与app关联到一起
    from .main import main as main_blueprint
    # 注册名为main的app
    app.register_blueprint(main_blueprint)

    # 将users蓝图程序与APP关联到一起
    from .users import users as users_blueprint
    # 注册名为users的app
    app.register_blueprint(users_blueprint)  # url_prefix="/user"
    app.permanent_session_lifetime = datetime.timedelta(seconds=10 * 60)
    app.run(host='0.0.0.0', port=80)
    return app


from flask import url_for,redirect,session
from functools import wraps


def is_login(func):
    @wraps(func)
    def check_login(*args,**kwargs):
        user_id = session.get('user_id')
        if user_id:
            return func(*args,**kwargs)
        else:
            return redirect(url_for('users.login'))
    return check_login


if __name__ == "__main__":
    app = create_app()