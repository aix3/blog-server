#!/usr/bin/env python
# encoding: utf-8
from coreweb import get, post
from models import User

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


def article():
    pass
