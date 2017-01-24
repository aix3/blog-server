#!/usr/bin/env python
# encoding: utf-8

configs = {
    'db': {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'passwd': 'passwd',
        'database': 'core'
    },
    'session': {
        'secret': 'Aweer'
    }
}

def merge(configs_dest, config_src):
    for k, v in config_src.items():
        if isinstance(v, dict):
            sub_dict = configs_dest.get(k, None)
            if sub_dict:
                merge(configs_dest[k], v)
            else:
                configs_dest[k] = v
        else:
            configs_dest[k] = v

try:
    import config_dev
    merge(configs, config_dev.configs)
except:
    pass

