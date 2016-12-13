#!/usr/bin/env python
# encoding: utf-8

import logging; logging.basicConfig(level=logging.INFO)

import asyncio,coreweb
import orm
import config
from datetime import datetime
from aiohttp import web

def index(request):
    return web.Response(body=b'<h1>Blog Index</h1>', content_type='text/html')

async def init(loop):
    app = web.Application(loop=loop, middlewares=[
       coreweb.logger_factory, coreweb.response_factory
    ])
    coreweb.init_jinja2(app, filters=dict())
    coreweb.add_routes(app, 'api')
    coreweb.add_static(app)

    app.router.add_route('GET', '/', index)
    await orm.create_pool(loop, **config.configs['db'])
    #app.router.add_route('GET', '/api/1', handlers.first_api)
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 80)
    logging.info('server are started at 127.0.0.1:80')
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()

