# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2019/6/4 22:51
# Author :  Richard
# File   :  views.py

# main主业务逻辑中的视图和路由的定义
from decimal import Decimal
from flask import render_template, request, session, redirect, url_for
# 导入蓝图程序用于构建路由
from . import main
# 导入db用于操作数据库
from .. import db
# 导入实体列 用户操作数据库
from ..models import *
import os,datetime

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'gif', 'GIF'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def is_numeric(s):
    if s.count('.') == 1:  # 判断小数点个数
        sl = s.split('.')  # 按照小数点进行分割
        left = sl[0]  # 小数点前面的
        right = sl[1]  # 小数点后面的
        if left.startswith('-') and left.count('-') == 1 and right.isdigit():
            lleft = left.split('-')[1]  # 按照-分割，然后取负号后面的数字
            if lleft.isdigit():
                return False
        elif left.isdigit() and right.isdigit():
            # 判断是否为正小数
            return True
    elif s.isdigit():
        s = int(s)
        if s != 0:
            return True
    return False

@main.route("/test")
def test():
    # category = Category("时尚杂志")
    # category.save()
    # category = Category.query.filter().all()
    books = Book.query.filter(Book.id>0).join(Category).limit(10).with_entities(Book.id,Book.name,Book.author,Book.category_id,Category.name,Book.cover_img,Book.price,Book.description).all()
    print(books)
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    books_info = []
    for values in books:
        book_info = {}
        # print(values)
        i = 0
        for key in book_info_key:
            if key == 'price':
                book_info[key] = float(values[i].quantize(Decimal('0.00')))
            else:
                book_info[key] = values[i]
            # print(values[i])
            i += 1
        books_info.append(book_info)
    # print(book_info)
    # print(os.path.dirname(__file__))
    return str(books_info)

@main.route("/admin")
def admin():
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    return render_template('admin_index.html',session=session)


# 查看分类列表
@main.route("/admin/category_list", methods=['GET','POST'])
def category_list():
    # 定义错误标志和信息
    msg = '修改成功！'
    # 权限校验
    # role = session.get('role')
    # if role is None or role == 0:
    #     msg = "* 权限不够"
    #     return render_template('index.html', msg=msg)
    category_list = Category.query.filter().all()
    return render_template('category_list.html', category_list=category_list)


# 添加分类
@main.route('/edit_category', methods=['GET','POST'])
def edit_category():
    role = session.get('role')
    if role is None or role == 0:
        # msg = "* 权限不够"
        return redirect(url_for('users.index'))
    if request.method == 'GET':
        category_id = request.args.get('category_id')
        category_info = Category.query.filter(Category.id == category_id).first()
        return redirect(url_for('main.category_list'))
    if request.method == 'POST':
        category_name = request.form.get('category_name','')
        if category_name == '' or len(category_name)>50:
            return redirect(url_for('main.category_list'))
        category = Category(name=category_name)
        category.save()
        return redirect(url_for('main.category_list'))


# 删除分类
@main.route('/delete_category')
def delete_category():
    role = session.get('role')
    if role is None or role == 0:
        # msg = "* 权限不够"
        return redirect(url_for('users.index'))
    category_id = request.args.get('category_id')
    category = Category.query.filter_by(id = category_id).first()
    if not category:
        msg = "* 该目录不存在！"
        return redirect(url_for('main.category_list'), msg)
    else:
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for('main.category_list'))


# 管理员添加图书信息
@main.route("/admin/add_book", methods=['GET','POST'])
def add_book():
    # 定义错误标志和信息
    msg = '添加成功！'
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    if request.method == 'GET':
        category_list = Category.query.filter().all()
        return render_template('add_book.html', category_list=category_list)
    if request.method == 'POST':
        # 获取图书信息
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        author = request.form.get('author')
        print(author)
        cover_img = request.files['cover_img']
        price = request.form.get('price')
        description = request.form.get('description')
        # 判断必传字段是否有空
        if not all([name,type,price]):
            msg = "* 请检查必填字段是否填写"
            return render_template('add_book.html', msg=msg)
        # 判断字段是否合法
        if len(name)>100:
            msg = "* 名字长度不能大于100"
            return render_template("add_book.html", msg=msg)
        if len(author)>50:
            msg = "* 作者名字太长"
            return render_template("add_book.html", msg=msg)
        # 封面保存位置
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'static\\images\\book_img')
        if cover_img is None:
            img_name = "cover_img.png"
        else:
            if allowed_file(cover_img.filename):
                img_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.'+cover_img.filename.split('.')[1]
                cover_img_path = base_path + "\\" + img_name
                cover_img.save(cover_img_path)
            else:
                msg = "* 封面图片类型不支持"
                return render_template("add_book.html", msg=msg)
        if not is_numeric(price):
            msg = "* 价格为正整数或正小数"
            return render_template("add_book.html", msg=msg)
        if len(description)>500:
            msg = "* 描述字数应该小于500个字"
            return render_template("add_book.html", msg=msg)
        # 插入数据库
        book = Book(name=name,
                    category_id=category_id,
                    author=author,
                    cover_img=img_name,
                    price=price,
                    description=description)
        # 保存图书信息
        book.save()
        return redirect(url_for('main.book_list'))


# 管理员更改图书信息
@main.route("/admin/edit_book", methods=['GET','POST'])
def edit_book():
    # 定义错误标志和信息
    msg = '修改成功！'
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    # cover_img = ''
    book_id = request.args.get('book_id')
    if request.method == 'GET':
        book_info_value = Book.query.filter(Book.id == book_id).join(
            Category).with_entities(
            Book.id, Book.name, Book.author, Book.category_id,
            Category.name, Book.cover_img, Book.price, Book.description).first()
        categorys = Category.query.filter().all()
        book_info_key = (
            'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
        )
        book_info = dict(zip(book_info_key, book_info_value))
        book_info['price'] = float(book_info['price'].quantize(Decimal('0.00')))
        return render_template('edit_book.html', book_info=book_info, book_id=book_id, categorys=categorys)
    if request.method == 'POST':
        # 获取图书信息
        book_id = request.args.get('book_id')
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        author = request.form.get('author')
        cover_img = request.form.get('cover_img')
        price = request.form.get('price')
        description = request.form.get('description')
        # 查询图书信息
        book = Book.query.filter(Book.id == book_id).first()
        # 判断必传字段是否有空
        if not all([name, type, price]):
            msg = "* 请检查必填字段是否填写"
            return render_template('edit_book.html', msg=msg, book=book)
        # 判断字段是否合法
        if len(name) > 100:
            msg = "* 名字长度不能大于100"
            return render_template("edit_book.html", msg=msg, book=book)
        if len(author) > 50:
            msg = "* 作者名字太长"
            return render_template("edit_book.html", msg=msg, book=book)
        # 封面保存位置
        base_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static\\images\\book_img')
        if cover_img == '':
            img_name = book.cover_img
        else:
            if allowed_file(cover_img.filename):
                img_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                cover_img_path = base_path + "\\" + img_name
                cover_img.save(cover_img_path)
            else:
                msg = "* 封面图片类型不支持"
                return render_template("edit_book.html", msg=msg, book=book)
        if not is_numeric(price):
            msg = "* 价格为正整数或正小数"
            return render_template("edit_book.html", msg=msg, book=book)
        if len(description) > 500:
            msg = "* 描述字数应该小于500个字"
            return render_template("edit_book.html", msg=msg, book=book)
        # 修改信息
        book.name = name
        book.category_id = category_id
        book.author = author
        book.cover_img = img_name
        book.price = price
        book.description = description
        # 更新图书信息
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('main.book_list'))


# 管理员删除图书信息
@main.route("/admin/delete_book", methods=['GET','POST'])
def delete_book():
    # 定义错误标志和信息
    msg = '删除成功！'
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    if request.method == 'GET':
        book_id = request.args.get('book_id')
    else:
        book_id = request.form.get('book_id')
    book = Book.query.filter_by(id = book_id).first()
    # print('gggggggg',book_id,book)
    if not book:
        msg = "* 该图书不存在！"
        return redirect(url_for('main.book_list'), msg)
    else:
        db.session.delete(book)
        db.session.commit()
    return redirect(url_for('main.book_list'))


# 后台查看图书信息
@main.route("/admin/book_list", methods=["GET","POST"])
def book_list():
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    if request.method == 'POST':
        cur_page = request.form.get('cur_page',1)
    else:
        cur_page = request.args.get('cur_page',1)

    cur_page = int(cur_page)
    limit_num = 10
    book_list_start = (cur_page-1)*limit_num
    page_num = len(Book.query.filter().all())//limit_num + 1
    # print(page_num)
    book_info_key = (
        'id','name','author','category_id','category_name','cover_img','price', 'description',
    )
    books = Book.query.filter(Book.id>book_list_start).join(Category).order_by(Book.id).limit(limit_num).with_entities(Book.id,Book.name,Book.author,Book.category_id,Category.name,Book.cover_img,Book.price,Book.description).all()
    books_info = []
    for values in books:
        book_info = {}
        # print(values)
        i = 0
        for key in book_info_key:
            if key == 'price':
                book_info[key] = float(values[i].quantize(Decimal('0.00')))
            else:
                book_info[key] = values[i]
            i += 1
        books_info.append(book_info)
    # print(page_num)
    # print(cur_page)
    # print(books_info)
    return render_template('book_list.html', books_info=books_info, cur_page=cur_page, page_num=page_num)


# 查看订单列表
@main.route("/admin/order_list", methods=['GET','POST'])
def order_list():
    # 定义错误标志和信息
    msg = '修改成功！'
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    # 分页数 没有就默认为1
    if request.method == 'POST':
        cur_page = request.form.get('cur_page', 1)
    else:
        cur_page = request.args.get('cur_page', 1)
    cur_page =int(cur_page)
    # if request.method == 'GET':
    #     return render_template('order_list.html')
    # if request.method == 'POST':
    # 分页数 没有就默认为1
    # page_num = request.args.get('page_num', 1)
    orders_info_keys = (
        'id', 'buyer', 'name', 'cover_img', 'price',
        'pay_type', 'phone', 'send_type',
        'receive_address', 'order_date', 'other'
    )
    limit_num = 10
    page_num = len(Book.query.filter().all())//limit_num + 1
    order_list_start = (cur_page - 1) * limit_num
    orders_info_values = Bookorder.query.filter(Bookorder.id > order_list_start).join(User, Book).order_by(Book.id).limit(limit_num).with_entities(
        Bookorder.id, User.user_name, Book.name, Book.cover_img, Book.price,
        Bookorder.pay_type, User.phone, Bookorder.send_type, Bookorder.receive_address,
        Bookorder.order_date, Bookorder.other).all()
    # print(orders)
    orders_info = []
    for order_info_values in orders_info_values:
        order_info = dict(zip(orders_info_keys,order_info_values))
        order_info['price'] = float(order_info['price'].quantize(Decimal('0.00')))
        order_info['order_date'] = order_info['order_date'].strftime("%Y-%m-%d %H:%M:%S")
        orders_info.append(order_info)
    return render_template('order_list.html', orders_info=orders_info, page_num=page_num, cur_page=cur_page)


# 管理员删除订单信息
@main.route("/admin/delete_order", methods=['GET','POST'])
def delete_order():
    # 定义错误标志和信息
    msg = '删除成功！'
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    if request.method == 'GET':
        order_id = request.args.get('order_id')
    else:
        order_id = request.form.get('order_id')
    order = Bookorder.query.filter_by(id = order_id).first()
    print('gggggg',order_id,order)
    if not order:
        msg = "* 该订单不存在！"
        return redirect(url_for('main.order_list'), msg)
    else:
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('main.order_list'))


@main.route('/update_pass')
def update_pass():
    return render_template('pass.html')

@main.route('/comment_manage')
def comment_manage():
    return render_template('comment_manage.html')

@main.route('/user_list')
def user_list():
    # 定义错误标志和信息
    msg = '修改成功！'
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    # 分页数 没有就默认为1
    if request.method == 'POST':
        cur_page = request.form.get('cur_page', 1)
    else:
        cur_page = request.args.get('cur_page', 1)
    cur_page = int(cur_page)
    # if request.method == 'GET':
    #     return render_template('order_list.html')
    # if request.method == 'POST':
    # 分页数 没有就默认为1
    # page_num = request.args.get('page_num', 1)
    user_info_keys = (
        'id', 'role', 'user_name', 'head_img', 'real_name',
        'sex', 'born_date', 'phone',
        'balance'
    )
    limit_num = 10
    page_num = len(User.query.filter().all()) // limit_num + 1
    user_list_start = (cur_page - 1) * limit_num
    users_info_values = User.query.filter(User.id > user_list_start).limit(
        limit_num).with_entities(
        User.id, User.role, User.user_name, User.head_img, User.real_name, User.sex,
        User.born_date, User.phone, User.balance).all()
    # print(orders)
    users_info = []
    for user_info_values in users_info_values:
        user_info = dict(zip(user_info_keys, user_info_values))
        user_info['balance'] = float(user_info['balance'].quantize(Decimal('0.00')))
        user_info['born_date'] = user_info['born_date'].strftime("%Y-%m-%d")
        users_info.append(user_info)
    print('*********',users_info_values)
    return render_template('user_list.html', users_info=users_info, page_num=page_num, cur_page=cur_page)

@main.route('/edit_user')
def edit_user():
    pass


# 后台查询图书信息
@main.route("/admin/query_book", methods=["GET", "POST"])
def query_book():
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
        # if request.method == 'GET':
        #     page_num = len(Book.query.filter().all())
        #     return render_template('book_list.html', cur_page=1, page_num=page_num)
        # if request.method == 'POST':
        # 分页数 没有就默认为1
    cur_page = request.form.get('cur_page', 1)
    keyword = request.args.get('keyword', '')
    cur_page = int(cur_page)

    limit_num = 10
    # book_list_start = (cur_page - 1) * limit_num
    page_num = len(Book.query.filter().all()) // limit_num + 1
    # print(page_num)
    book_info_key = (
        'id', 'name', 'author', 'category_id', 'category_name', 'cover_img', 'price', 'description',
    )
    books = Book.query.filter(db.or_(Book.name.like('%'+keyword+'%'),Book.author.like('%'+keyword+'%'))).join(Category).order_by(Book.id).limit(
        limit_num).with_entities(Book.id, Book.name, Book.author, Book.category_id, Category.name, Book.cover_img,
                                 Book.price, Book.description).all()
    # print("#########",keyword)
    print(books)
    books_info = []
    for values in books:
        book_info = {}
        # print(values)
        i = 0
        for key in book_info_key:
            if key == 'price':
                book_info[key] = float(values[i].quantize(Decimal('0.00')))
            else:
                book_info[key] = values[i]
            i += 1
        books_info.append(book_info)
    print(page_num)
    print(cur_page)
    print(books_info)
    return render_template('book_list.html', books_info=books_info, cur_page=cur_page, page_num=page_num)

# 查看订单列表
@main.route("/admin/query_order", methods=['GET','POST'])
def query_order():
    # 定义错误标志和信息
    msg = '修改成功！'
    # 权限校验
    role = session.get('role')
    if role is None or role == 0:
        msg = "* 权限不够"
        return redirect(url_for('users.index'))
    # 分页数 没有就默认为1
    cur_page = request.form.get('cur_page', 1)
    keyword = request.args.get('keyword', '')
    cur_page =int(cur_page)
    # if request.method == 'GET':
    #     return render_template('order_list.html')
    # if request.method == 'POST':
    # 分页数 没有就默认为1
    # page_num = request.args.get('page_num', 1)
    orders_info_keys = (
        'id', 'buyer', 'name', 'cover_img', 'price',
        'pay_type', 'phone', 'send_type',
        'receive_address', 'order_date', 'other'
    )
    limit_num = 10
    page_num = len(Book.query.filter().all())//limit_num + 1
    # order_list_start = (cur_page - 1) * limit_num
    orders_info_values = Bookorder.query.filter(User.user_name.like("%"+keyword+"%")).join(User, Book).order_by(Book.id).limit(limit_num).with_entities(
        Bookorder.id, User.user_name, Book.name, Book.cover_img, Book.price,
        Bookorder.pay_type, User.phone, Bookorder.send_type, Bookorder.receive_address,
        Bookorder.order_date, Bookorder.other).all()
    # print(orders)
    orders_info = []
    for order_info_values in orders_info_values:
        order_info = dict(zip(orders_info_keys,order_info_values))
        order_info['price'] = float(order_info['price'].quantize(Decimal('0.00')))
        order_info['order_date'] = order_info['order_date'].strftime("%Y-%m-%d %H:%M:%S")
        orders_info.append(order_info)
    return render_template('order_list.html', orders_info=orders_info, page_num=page_num, cur_page=cur_page)
