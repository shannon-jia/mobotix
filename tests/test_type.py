#!/usr/bin/python
# -*- coding:utf-8 -*-

import json
import types

data = '{"insun": "天下第一","name":"金刚不坏"}'
js = json.loads(data)

print(type(data), data, '\n', type(js), js)
