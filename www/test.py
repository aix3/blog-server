#!/usr/bin/env python
# encoding: utf-8

import orm
from models import User, Article, Comment
import asyncio
import logging;logging.basicConfig(level=logging.DEBUG)


async def test_save():
    u1 = User()
    u1.email = 'xq@imrq.me'
    u1.name = 'xiaoxiao'
    u1.passwd = '123456'
    u1.admin = True
    u1.avatar = 'xxx.jpeg'
    await u1.save()

    a1 = Article()
    a1.user_id = u1.id
    a1.user_name = u1.name
    a1.user_avatar = u1.avatar
    a1.title = '我的文字'
    a1.sunnary = 'xxx'
    a1.content = '我轻轻的来，正如我轻轻的去'
    await a1.save()

    c1 = Comment()
    c1.user_id = u1.id
    c1.user_name = u1.name
    c1.article_id = a1.id
    c1.content = '售价五个滑稽币'
    await c1.save()

async def test_find():
    u1 = await  User.find(2)
    logging.debug('find user =>'+str(u1))

async def test_findAll():
    u1 = await  User.findAll()
    logging.debug('findAll users =>'+str(u1))


async def test_delete():
    u1 = await  User.find(2)
    logging.debug('find user =>'+str(u1))
    await u1.delete()
    u1 = await User.find(2)
    logging.debug('delete user is'+str(u1))

async def test_update():
    u1 = await  User.find(2)
    logging.debug('find user =>'+str(u1))
    u1.name='xiaoqaing'
    u1.age=18
    await u1.update()
    u1 = await User.find(2)
    logging.debug('updated user is'+str(u1))


loop = asyncio.get_event_loop()
async def setUp():
    conf = dict(user='root', pwd='passwd', db='test')
    await orm.create_pool(loop, **conf)

async def tearDown():
    await orm.destroy_pool()

async def run():
    await setUp()
    await User.deleteAll()
    await test_save()
    #await test_find()
    #await test_delete()
    #await test_findAll()
    #await test_update()
    await tearDown()

if __name__ == '__main__':
    loop.run_until_complete(run())
    loop.close()
