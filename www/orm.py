#!/usr/bin/env python
# encoding: utf-8

import logging; logging.basicConfig(level=logging.DEBUG)
import aiomysql


# 创建数据库连接池
async def create_pool(loop, **kw):
    logging.info('create database connection pool')
    global __pool
    __pool = await aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw.get('user'),
        password = kw.get('passwd'),
        db = kw['database'],
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 5),
        loop=loop
    )

async def destroy_pool():
    global __pool
    if __pool:
        __pool.close()
        await __pool.wait_closed()

async def select(sql, args, size=None):
    global __pool
    with (await __pool) as conn:
        cur = await conn.cursor(aiomysql.DictCursor)
        await cur.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = await cur.fetchmany(size)
        else:
            rs = await cur.fetchall()
        await cur.close()
        logging.info('rows retuned: %s' % str(rs))
        return rs

async def execute(sql, args):
    with (await __pool) as conn:
        try:
            cur = await conn.cursor()
            await cur.execute(sql.replace('?','%s'), args)
            affected = cur.rowcount
            await cur.close()
        except BaseException as e:
            raise
        return affected


# Meta class
class ModelMetaClass(type):
    def __new__(cls, name, bases, attrs):
        # 排除Model类本身
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        #获取table名称
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        # 获取所有的Field和主键名称
        mappings = dict()
        fields = []
        primary_key = None
        logging.debug('attrs value:'+str(attrs))

        for k, v in attrs.items():
            logging.debug('k = %s, v = %s' % (k, v))
            if isinstance(v, Field):
                logging.info('  found mapping: %s => %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    if primary_key:
                        # 主键字段重复
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primary_key = k
                else:
                    fields.append(k)
        if not primary_key:
            raise RuntimeError('Primary key required.')

        for k in mappings.keys():
            attrs.pop(k)

        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName # 表名称
        attrs['__primary_key__'] = primary_key #主键列
        attrs['__fields__'] = fields

        attrs['__select__'] = 'select `%s`, %s from `%s` ' % (primary_key, ', '.join(escaped_fields), tableName)

        attrs['__insert__'] = 'insert into `%s` (`%s`, %s) values (%s) ' % (tableName, primary_key, ', '.join(escaped_fields), ', '.join([x for x in '?' * (len(fields)+1)]))

        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName,', '.join(list(map(lambda f:'%s=?' % f, escaped_fields))), primary_key)

        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primary_key)
        return super(ModelMetaClass, cls).__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaClass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as e:
            raise AttributeError('model has not attr %s' % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return self.__getattr__(self, key)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                if callable(field.default):
                    value = field.default()
                else:
                    value = field.default
                logging.debug('using default value for %s : %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def find(cls, pk):
        'find obj by primary key'
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])


    async def save(self):
        'save obj'
        logging.debug('self.__fields__ =>'+str(self.__fields__))
        args = list(map(self.getValueOrDefault, self.__fields__))
        logging.debug('args =>'+str(args))
        args.insert(0, self.getValueOrDefault(self.__primary_key__))
        logging.debug('args == >>'+str(args))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record')

    async def delete(self):
        'delete obj'
        arg = self.getValueOrDefault(self.__primary_key__)
        rowcount = await execute(self.__delete__, arg)
        if rowcount != 1:
            logging.warn('faield to delete record')

    @classmethod
    async def deleteAll(cls):
        'delete all obj'
        rowcount = await execute('delete from %s' % cls.__table__, None)
        logging.info('deleted record rows: %s' % str(rowcount))


    async def update(self):
        'update obj'
        primary_key = self.getValueOrDefault(self.__primary_key__)
        if primary_key is None:
            raise AttributeError('There is no primary_key attr')

        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        logging.debug('update args is: %s' % str(args))
        rowcount = await execute(self.__update__, args)
        if rowcount != 1:
            logging.warn('faield to update record')

    @classmethod
    async def findAll(cls):
        rs = await select(cls.__select__, None)
        return list(map(lambda r: cls(**r), rs))

class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
    def __init__(self, name=None, ddl='varchar', primary_key=False, default=''):
        super().__init__(name, ddl, primary_key, default)

class IntegerField(Field):
    def __init__(self, name=None, ddl='integer', primary_key=False, default=0):
        super().__init__(name, ddl, primary_key, default)

class LongField(Field):
    def __init__(self, name=None, ddl='bigint', primary_key=False, default=0):
        super().__init__(name, ddl, primary_key, default)

class TextField(Field):
    def __init__(self, name=None, ddl='text', primary_key=False, default=''):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):
    def __init__(self, name=None, ddl='tinyint', primary_key=False, default=0):
        super().__init__(name, ddl, primary_key, default)

class ByteField(Field):
    def __init__(self, name=None, ddl='tinyint', primary_key=False, default=0):
        super().__init__(name, ddl, primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, ddl='float', primary_key=False, default=0.0): super().__init__(name, ddl, primary_key, default)
