# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2019/6/4 22:52
# Author :  Richard
# File   :  views.py

# users针对用户业务逻辑处理的视图和路由
from _decimal import Decimal

from flask import render_template, request, redirect, url_for, session
# 导入蓝图程序用于构建路由
from . import users
# 导入db用于操作数据库
from .. import db
# 导入实体列 用户操作数据库
from ..models import *
from hashlib import md5 as hash_md5
import datetime, os
from ..utile import book_recommand


@users.route("/index.html")
@users.route("/")
def index():
    # if session.get('user_id') is not None:
    limit_num = 10
    cur_page = 1
    book_list_start = (cur_page - 1) * limit_num
    page_num = len(Book.query.filter().all()) // limit_num + 1
    # print(page_num)
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    books = Book.query.filter(Book.id > book_list_start).join(
        Category).limit(limit_num).with_entities(
        Book.id, Book.name, Book.author, Book.category_id,
        Category.name, Book.cover_img, Book.price, Book.description).all()
    books_info = []
    for values in books:
        book_info = {}
        # print(values)
        i = 0
        for key in book_info_key:
            if key == 'price':
                book_info[key] = float(values[i].quantize(Decimal('0.00')))
            if key == 'description':
                if len(values[i]) > 300:
                    # print(type(values[i][:80]))
                    book_info[key] = values[i][:300]+"..."
                else:
                    book_info[key] = values[i]
            else:
                book_info[key] = values[i]
            i += 1
        books_info.append(book_info)
        # session.clear()
        # print(session)
    return render_template('index.html', books_info=books_info, session=session)


@users.route("/register.html")
@users.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        # 获取用户填写的信息
        user_name = request.form.get('user_name')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static\\images\\head_img')
        head_img = "head_img.png"
        # head_img = request.form.get('head_img')
        real_name = request.form.get('real_name')
        sex = request.form.get('sex')
        born_date = request.form.get('born_date')
        phone = request.form.get('phone')
        # 定义个变量来控制过滤用户填写的信息
        msg,flag = '',True
        # 判断用户是否信息都填写了.(all()函数可以判断用户填写的字段是否有空)
        if not all([user_name, pwd1, pwd2, real_name, sex, born_date, phone]):
            msg, flag = '* 请填写完整信息', False
            return render_template('login.html', msg=msg)
        # 判断用户名是长度是否大于20
        if len(user_name) > 20:
             msg, flag = '* 用户名太长', False
        # 判断两次填写的密码是否一致
        if pwd1 != pwd2:
            msg, flag = '* 两次密码不一致', False
        # 判断真实名字长度是否大于20
        if len(real_name) > 20:
            msg, flag = '* 真实名太长', False
        # 判断电话号码长度是否合法
        if len(phone) != 11:
            msg, flag = '电话号码非法', False
        # 判断电话号码开始一位是否合法
        if phone[0] != '1':
            msg, flag = '电话号码非法', False
        # 如果上面的检查有任意一项没有通过就返回注册页面,并提示响应的信息
        if not flag:
            return render_template('login.html', msg=msg)

        # 核对输入的用户是否已经被注册了
        u = User.query.filter(User.user_name == real_name).first()
        # 判断用户名是否已经存在
        if u:
            msg = '用户名已经存在'
            return render_template('login.html', msg=msg)
        # 上面的验证全部通过后就开始创建新用户
        # 首先加密获取密码摘要
        # MD5 加密
        h_md5 = hash_md5()
        h_md5.update(pwd1.encode('utf-8'))  # 需要将字符串进行编码，编码成二进制数据
        pwd1_md5_str = h_md5.hexdigest()  # 获取16进制的摘要作为保存的密码
        # print('MD5生成摘要结果:', pwd1_md5_str)  # 输出结果
        user = User(user_name=user_name,
                    password=str(pwd1_md5_str),
                    real_name=real_name,
                    head_img=head_img,
                    sex=sex,
                    born_date=born_date,
                    phone=phone)
        # 保存注册的用户
        user.save()
        # print(msg)
        # 跳转到登录页面
    return redirect(url_for('users.login'))


@users.route("/login.html")
@users.route('/login', methods=['GET', 'POST'])
def login():
    session.permanent = True
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        # 判断用户名和密码是否填写
        if not all([user_name, password]):
            msg = '* 请填写好完整的信息'
            return render_template('login.html', msg=msg)
        # 核对用户名和密码是否一致
        # 首先对密码进行数字摘要
        h_md5 = hash_md5()
        h_md5.update(password.encode('utf-8'))  # 需要将字符串进行编码，编码成二进制数据
        password_md5_str = h_md5.hexdigest()  # 获取16进制的摘要作为保存的密码
        user = User.query.filter_by(user_name=user_name, password=password_md5_str).first()
        # 如果用户名和密码一致
        if user:
            # 向session中写入相应的数据
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.user_name
            session['head_img'] = user.head_img
            session['balance'] = float(user.balance.quantize(Decimal('0.00')))
            session['born_date'] = user.born_date
            session['phone'] = user.phone
            session['sex'] = user.sex
            if session['role'] == 1:
                return redirect(url_for('main.admin'))
            return redirect(url_for('users.index'))
        # 如果用户名和密码不一致返回登录页面,并给提示信息
        else:
            msg = '* 用户名或者密码不正确'
            return render_template('login.html', msg=msg)


@users.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('users.index'))


# 用户前台查询图书信息
@users.route("/book_list")
def book_list():
    limit_num = 10
    cur_page = 1
    book_list_start = (cur_page - 1) * limit_num
    page_num = len(Book.query.filter().all()) // limit_num + 1
    # print(page_num)
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    books = Book.query.filter(Book.id > book_list_start).join(
        Category).order_by(Book.id).limit(limit_num).with_entities(
        Book.id,Book.name, Book.author, Book.category_id,
        Category.name, Book.cover_img, Book.price, Book.description).all()
    books_info = []
    for values in books:
        book_info = {}
        # print(values)
        i = 0
        for key in book_info_key:
            if key == 'price':
                book_info[key] = float(values[i].quantize(Decimal('0.00')))
            if key == 'description':
                if len(values[i]) > 80:
                    books_info[key] = values[i][:80] + '...'
                else:
                    books_info[key] = values[i]
            else:
                book_info[key] = values[i]
            i += 1
        books_info.append(book_info)

    return render_template('index.html', books_info=books_info)


# 添加订单
@users.route("/order_book", methods=['GET', 'POST'])
def order_book():
    book_recommand_list = book_recommand()
    book_id = request.args.get('id')
    print(book_id)
    book_info_value = Book.query.filter(Book.id == book_id).join(
        Category).with_entities(
        Book.id, Book.name, Book.author, Book.category_id,
        Category.name, Book.cover_img, Book.price, Book.description).first()
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    book_info = dict(zip(book_info_key, book_info_value))
    book_info['price'] = float(book_info['price'].quantize(Decimal('0.00')))
    if request.method == 'GET':
        code = 0
        msg = 200
        # if book_id is None:
        #     # msg = "* 没有该图书！"
        #     return redirect(url_for('book_list'))
        return render_template('bookinfo.html', msg=msg, code=code, book_info=book_info, book_recommand_list=book_recommand_list)
    if request.method == 'POST':
        # 权限校验
        role = session.get('role')
        if role is None:
            msg = "* 请先登录！"
            return render_template('login.html', msg=msg)
        book_id = request.form.get('id')
        # if book_id is None:
        #     # msg = "* 没有该图书！"
        #     return redirect(url_for('book_list'))
        order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pay_type = request.form.get('pay_type')
        send_type = request.form.get('send_type')
        receive_address = request.form.get('receive_address')
        other = request.form.get('other')
        # 判断必填字段是否为空
        # book = Book.query.filter_by(Book.id == book_id)
        print([book_id,pay_type,send_type,receive_address])
        if not all([book_id,pay_type,send_type,receive_address]):
            code=0
            msg = '* 请检查信息是否完整！'
            return render_template('bookinfo.html', msg=msg, code=code, book_info=book_info, book_recommand_list=book_recommand_list)
        book_order = Bookorder(user_id=session.get('user_id'),
                               book_id=book_id,
                               order_date=order_date,
                               is_delete=0,
                               is_complete=0,
                               pay_type=pay_type,
                               send_type=send_type,
                               receive_address=receive_address,
                               other=other)
        # 保存订单
        book_order.save()
        code = 1
        msg = "购买成功！"
        return render_template('bookinfo.html', msg=msg, code=code, book_info=book_info, book_recommand_list=book_recommand_list)


@users.route('/bookrecommend.html')
@users.route('/bookrecommend')
def book_recommend():
    # if session.get('user_id') is not None:
    limit_num = 10
    cur_page = request.args.get('cur_page',1)
    book_list_start = (cur_page - 1) * limit_num
    page_num = len(Book.query.filter().all()) // limit_num + 1
    # print(page_num)
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    books = Book.query.filter(Book.id > book_list_start).join(
        Category).order_by(Book.id).limit(limit_num).with_entities(
        Book.id, Book.name, Book.author, Book.category_id,
        Category.name, Book.cover_img, Book.price, Book.description).all()
    books_info = []
    for values in books:
        book_info = {}
        # print(values)
        i = 0
        for key in book_info_key:
            if key == 'price':
                book_info[key] = float(values[i].quantize(Decimal('0.00')))
            if key == 'description':
                if len(values[i]) > 50:
                    # print(type(values[i][:80]))
                    book_info[key] = values[i][:50] + "..."
                else:
                    book_info[key] = values[i]
            else:
                book_info[key] = values[i]
            i += 1
        books_info.append(book_info)
        # session.clear()
        # print(session)
    return render_template('bookrecommend.html', books_info=books_info, page_num=page_num, cur_page=cur_page)


@users.route('/allbook.html')
@users.route('/allbook')
def allbook():
    # if session.get('user_id') is not None:
    limit_num = 10
    cur_page = int(request.args.get('cur_page', 1))
    book_list_start = (cur_page - 1) * limit_num
    page_num = len(Book.query.filter().all()) // limit_num + 1
    # print(page_num)
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    books = Book.query.filter(Book.id > book_list_start).join(
        Category).order_by(Book.id).limit(limit_num).with_entities(
        Book.id, Book.name, Book.author, Book.category_id,
        Category.name, Book.cover_img, Book.price, Book.description).all()
    books_info = []
    for values in books:
        book_info = {}
        # print(values)
        i = 0
        for key in book_info_key:
            if key == 'price':
                book_info[key] = float(values[i].quantize(Decimal('0.00')))
            if key == 'description':
                if len(values[i]) > 300:
                    # print(type(values[i][:80]))
                    book_info[key] = values[i][:300] + "..."
                else:
                    book_info[key] = values[i]
            else:
                book_info[key] = values[i]
            i += 1
        books_info.append(book_info)
        # session.clear()
        # print(session)
    return render_template('allbook.html', books_info=books_info, page_num=page_num, cur_page=cur_page)


@users.route('/about.html')
@users.route('/about')
def about():
    return render_template('about.html')


@users.route('/showbookbyid')
def showbookbyid():
    book_id = request.args.get('book_id', 5)
    print(book_id)
    book_info_value = Book.query.filter(Book.id==book_id).join(
        Category).with_entities(
        Book.id, Book.name, Book.author, Book.category_id,
        Category.name, Book.cover_img, Book.price, Book.description).first()
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    book_info = dict(zip(book_info_key,book_info_value))
    book_info['price'] = float(book_info['price'].quantize(Decimal('0.00')))
    print(book_info)
    return render_template('bookinfo.html',book_info=book_info)
