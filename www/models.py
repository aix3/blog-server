#!/usr/bin/env python
# encoding: utf-8

import time, uuid
from orm import Model, StringField, BooleanField,FloatField, TextField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 't_users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(20)')
    passwd = StringField(ddl='varchar(256)')
    admin = BooleanField()
    avatar = StringField(ddl='varchar(512)')
    created_at = FloatField(default=time.time())

class Article(Model):
    __table__ = 't_articles'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(20)')
    user_avatar = StringField(ddl='varchar(512)')
    title = StringField(ddl='varchar(256)')
    summary = StringField(ddl='varchar(512)')
    content = TextField()
    created_at = FloatField(default=time.time())

class Comment(Model):
    __table__ = 't_comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(20)')
    user_avatar = StringField(ddl='varchar(512)')
    article_id = StringField(ddl='varchar(50)')
    content = TextField()
    created_at = FloatField(default=time.time())

if __name__ == '__main__':
    print(next_id())
