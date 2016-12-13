#!/usr/bin/env python
# encoding: utf-8
from coreweb import get, post

@get('/api/1')
def first_api(**param):
    return ('fist api %s' % str(param))


def index():
    pass

def article():
    pass
