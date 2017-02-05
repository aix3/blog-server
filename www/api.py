#!/usr/bin/env python
# encoding: utf-8
import logging; logging.basicConfig(level=logging.INFO)
from coreweb import get, post
from models import User, Article

import time

@post('/api/article/list')
async def article_list():
    logging.info('current time is %s' % time.time())
    articles = await Article.findAll()
    return dict({'articles': articles})

@post('/api/article/get/{id}')
async def article_get(id):
    article = await Article.find(id)
    return article

@post('/api/article/create')
async def article_create(**content):
    article = Article(**content)
    
    article.user_name = 'xiaoxiao'
    article.user_id = 1
    article.user_avatar = 'https://ss0.baidu.com/94o3dSag_xI4khGko9WTAnF6hhy/image/h%3D200/sign=758b33e74e10b912a0c1f1fef3fcfcb5/8326cffc1e178a82019b0bfcff03738da877e8c3.jpg'

    await article.save()
    return dict({'code': 1})

@post('/api/article/delete')
async def article_delete(*, id):
    article = await Article.find(id)
    if article:
        await article.delete()
    return dict({'code': 1})

@get('/user/all')
async def list_user():
    users = await User.findAll()
    return {
        '__template__':'users.html',
        'users': users
    }

@get('/api/1')
def first_api(**param):
    return dict(api='/api/i', params=param, code=200, desc='OK')

@post('/api/p1')
def index(*, a):
    return dict(api='/api/p1', request='request', params=a, code=200, desc='OK')

@post('/api/{number}')
def id(number):
    return dict(api='api/{id}', id=number, code=200, desc='OK')

@post('/api/{number}')
def id(request, number):
    return dict(api='api/{id}', id=number,method=request.method, code=200, desc='OK')

@post('/api/1/{number}')
def id(number,request):
    return dict(api='api/{id}',method=request.method, id=number, code=200, desc='OK')

