# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2019/6/4 22:50
# Author :  Richard
# File   :  models.py

# 当前项目相关的模型文件 所有 实体类
from . import db
# import datetime


# 图书分类
class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # 反向引用 book表 每个category对象都有一个book属性
    book = db.relationship("Book", backref="category", lazy="dynamic")

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Category:%r>'%self.name

# 图书信息
class Book(db.Model):
    __tablename__ = "book"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(50))
    cover_img = db.Column(db.String(200))
    price = db.Column(db.Numeric(2, 18), nullable=False, default=0)
    description = db.Column(db.String(500))

    # 关系：一（category）对多 (book)
    # 外键关联book表每个Bookorder对象都有一个book_id属性 FK_category_id
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    # 反向引用 bookorder表 每个book对象都有一个bookorder属性
    bookorder = db.relationship("Bookorder", backref="book", lazy="dynamic")

    def __init__(self, category_id, name, author, cover_img, price, description):
        self.name = name
        self.author = author
        self.category_id = category_id
        self.cover_img = cover_img
        self.price = price
        self.description = description

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Book:%r>'%self.name


# 用户信息
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, default=0)
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(32), nullable=False)
    head_img = db.Column(db.String(200))
    real_name = db.Column(db.String(20), nullable=False)
    sex = db.Column(db.Integer, nullable=False, default=0)
    born_date = db.Column(db.DATE, nullable=False)
    phone = db.Column(db.String(11), nullable=False)
    balance = db.Column(db.Numeric(2, 18), default=0)

    # 反向引用bookorder表
    user_bookorder = db.relationship("Bookorder", backref="user", lazy="dynamic")

    def __init__(self, user_name, password, real_name, head_img, sex, born_date, phone, balance=0,role=0):
        self.role = role
        self.user_name = user_name
        self.password = password
        self.real_name = real_name
        self.head_img = head_img
        self.sex = sex
        self.born_date = born_date
        self.phone = phone
        self.balance = balance

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<User:%r>'%self.user_name

# 图书订单信息
class Bookorder(db.Model):
    __tablename__ = "bookorder"
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False)
    is_delete = db.Column(db.Integer, nullable=False, default=0)
    is_complete = db.Column(db.Integer, nullable=False, default=0)
    pay_type = db.Column(db.Integer, nullable=False, default=0)
    send_type = db.Column(db.Integer, nullable=False, default=0)
    receive_address = db.Column(db.String(200),nullable=False)
    other = db.Column(db.String(500))

    # 关系：一（user，book）对多 (bookorder)
    # 外键关联book表每个Bookorder对象都有一个book_id属性 FK_book_id
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    # 外键关联user表每个Bookorder对象都有一个user_id属性FK_user_id
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # 反向引用 comment表 每个Bookorder对象都有一个comment属性
    reply = db.relationship("Comment", backref="bookorder", lazy="dynamic")

    def __init__(self, book_id, user_id, order_date, is_delete, is_complete, pay_type, send_type, receive_address, other):
        self.book_id = book_id
        self.user_id = user_id
        self.order_date = order_date
        self.is_delete = is_delete
        self.is_complete = is_complete
        self.pay_type = pay_type
        self.send_type = send_type
        self.receive_address = receive_address
        self.other = other

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Bookorder:%r>'%self.__tablename__

# 回复内容信息
class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False, default=0)
    comment_date = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.String(500), nullable=False)

    # 关系：一（bookorder）对多 (comment)
    # 外键关联bookorder表  comment对象都有一个bookorder_id属性 FK_bookorder_id
    bookorder_id = db.Column(db.Integer, db.ForeignKey("bookorder.id"), nullable=False)

    def __init__(self, bookorder_id, comment_type, date, content):
        self.bookorder_id = bookorder_id
        self.comment_type = comment_type
        self.date = date
        self.content = content

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __rper__(self):
        return '<Comment:%r>'%self.__tablename__

