#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""The Application Interface."""

import logging
import asyncio
import json
from aiohttp import web

log = logging.getLogger(__name__)


class Api(object):
    ''' Application Interface for RPS
    '''

    def __init__(self, loop, port=8080, site=None, amqp=None):
        loop = loop or asyncio.get_event_loop()
        self.app = web.Application(loop=loop)
        self.app.router.add_get('/', self.index)
        self.app.router.add_get('/v2/system', self.handle_system)
        self.site = site
        self.port = port
        self.amqp = amqp
        self.db = {}

    def start(self):
        # outside
        web.run_app(self.app, host='0.0.0.0', port=self.port)

    async def index(self, request):
        return web.Response(text=json.dumps({
            'info': str(self.site),
            'amqp': self.amqp.get_info(),
            'api_version': 'V1',
            'api': ['v2/system'],
            'modules version': 'IPP-I'}))

    def get_system(self):
        return {
            'system': self.site.get_info(),
        }

    async def handle_system(self, request):
        data = self.get_system()
        return web.Response(
            text=json.dumps(data))
