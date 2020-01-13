# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Time   :  2019/6/21 22:41
# Author :  Richard
# File   :  utile.py

from .models import *
from _decimal import Decimal


def book_recommand():
    limit_num = 5
    cur_page = 1
    book_list_start = (cur_page - 1) * limit_num
    # page_num = len(Book.query.filter().all()) // limit_num + 1
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
                if len(values[i]) > 50:
                    # print(type(values[i][:80]))
                    book_info[key] = values[i][:50] + "..."
                else:
                    book_info[key] = values[i]
            else:
                book_info[key] = values[i]
            i += 1
        books_info.append(book_info)
    return books_info