#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的用户
"""

from database.connection import db

with db.get_cursor() as cursor:
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    print("数据库中的用户：")
    for row in rows:
        print(dict(row))
