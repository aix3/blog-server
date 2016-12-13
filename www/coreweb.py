#!/usr/bin/env python
# encoding: utf-8
import functools
import asyncio
import inspect
import json
import urllib
import os
from jinja2 import Environment, FileSystemLoader
from aiohttp import web
import logging;logging.basicConfig(level=logging.DEBUG)

def get(path):
    'Define decorator @get(\'/path\')'
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    'Define decorator @post(\'/path\')'
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

class RequestHandler(object):

    def __init__(self, app, func):
        self._app = app
        self._func = func
        self._has_pos_or_kw_args = has_args_kind(func, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        self._has_var_kw_args = has_args_kind(func, inspect.Parameter.VAR_KEYWORD)
        self._has_kw_only_args = has_args_kind(func, inspect.Parameter.KEYWORD_ONLY)
        self._has_var_pos_args = has_args_kind(func, inspect.Parameter.VAR_POSITIONAL)
        self._has_request_args = has_request_args(func)
        self._kw_only_args = get_kw_only_args(func)
        self._required_args = get_required_args(func)

    async def __call__(self, request):
        kw = None
        if self._has_kw_only_args or self._has_var_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Miss request Content-Type')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest(reason='JSON format error')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                    logging.info('Post request params is: %s', str(kw))
                else:
                    return web.HTTPBadRequest(reason='Unsupport Content-Type %s' % str(request.content_type))
            elif request.method == 'GET':
                qs = request.query_string
                kw = dict()
                if qs:
                    for k, v in urllib.parse.parse_qs(qs, True).items():
                        logging.info('query_string key=%s, value=%s', str(k), str(v))
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_args and self._kw_only_args:
                temp = dict()
                for name in self._kw_only_args:
                    temp[name] = kw[name]
                kw = temp

            for k,v in request.match_info.items():
                if k in kw:
                    logging.warn('Duplicate param %s' % k)
                kw[k] = v

        if self._has_request_args:
            kw['request'] = request

        if self._required_args:
            for name in self._required_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing parameter %s' % name)
        r = await self._func(**kw)
        return r

def has_request_args(func):
    params = inspect.signature(func).parameters
    for k, v in params.items():
        if k == 'request':
            return True

def get_kw_only_args(func):
    args = []
    params = inspect.signature(func).parameters
    for name, arg in params.items():
        if arg.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def get_required_args(func):
    args = []
    params = inspect.signature(func).parameters
    for name, arg in params.items():
        if arg.kind == inspect.Parameter.KEYWORD_ONLY and arg.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def has_args_kind(func, kind):
    params = inspect.signature(func).parameters
    for k, v in params.items():
        if v.kind == kind:
            return True

def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add jinja2 static %s=>%s', '/static/', str(path))

def init_jinja2(app, **kw):
    logging.info('init jinja2 ...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('bss', '{%'),
        block_end_string=kw.get('bes', '%}'),
        variable_start_string=kw.get('vss', '{{'),
        variable_end_string=kw.get('ves', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('init jinja2 path is %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters')
    if filters:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env

def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == -1:
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)

def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('Http method not defined in %s' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ','.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))

async def logger_factory(app, handler):
    async def logger(request):
        #记录日志
        logging.info('Request: %s %s' % (request.method, request.path))
        #继续处理请求
        return (await handler(request))
    return logger

async def response_factory(app, handler):
    async def response(request):
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            resp = None
            template = r.get('__template__')
            if template:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
            else:
                resp = web.Response(body=json.dumps(r, indent=4).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
            return resp
        if isinstance(r, int) and r >=200 and r <= 500:
            return web.Response(r)
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type='text/plain;charset=utf-8'
        return resp
    return response


