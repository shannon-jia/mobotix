# -*- coding: utf-8 -*-

"""Main module."""

import logging
import json
import asyncio
import time
from urllib.parse import urlparse


log = logging.getLogger(__name__)


class EchoServerProtocol(asyncio.Protocol):
    def __init__(self, master):
        self.master = master

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log.info('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        log.info('Data received: {!r}'.format(data))
        if self.master.received:
            self.master.received(data)

        # log.info('Close the client socket')
        # self.transport.close()



class Mobotix():
    """
    MOBOTIX system driver for SAM V1
    """

    def __init__(self, loop, tcp_svr='0.0.0.0'):
        self.loop = loop or asyncio.get_event_loop()
        _url = urlparse(tcp_svr)
        self.host = _url.hostname or '0.0.0.0'
        self.port = _url.port or 9009

        self.publish = None
        self.num = 0

        self.loop.create_task(self._do_connect())

    def __str__(self):
        return "MOBOTIX"

    def get_info(self):
        return {'actions': 'MOBOTIX'}

    async def _do_connect(self):
        try:
            server = await self.loop.create_server(
                lambda: EchoServerProtocol(self),
                self.host, self.port)
            self.connected = True
            log.info(f'Serving on {server.sockets[0].getsockname()}')
        except Exception as e:
            log.error(f'{e}')

    def set_publish(self, publish):
        if callable(publish):
            self.publish = publish
        else:
            self.publish = None

    async def got_command(self, mesg):
        try:
            log.info('Mobotix received: {}'.format(mesg))
            return await self._do_action(mesg)
        except Exception as e:
            log.error('Mobotix do_action() exception: {}'.format(e))

    async def _do_action(self, mesg):
        raise NotImplementedError

    def start(self):
        self._auto_loop()

    def _auto_loop(self):
        self.num += 1
        if self.num > 30:
            self.num = 0
            log.info('No message! Please waiting for 30 seconds...')
        self.loop.call_later(1, self._auto_loop)

    def received(self, data):
        self.num = 0
        rep_msg = {}
        try:
            mesg = json.loads(data)
            if not mesg:
                return
            rep_msg['type'] = 'Auxiliary Input'
            rep_msg['name'] = 'PMIX_' + mesg.get('camera')[4:] + '_1'
            rep_msg['offset'] = 0
            # rep_msg['time_stamp'] = mesg.get('time_stamp')[:19]
            rep_msg['time_stamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            rep_msg['source'] = 'publisher.protocols.ipp_host'
            rep_msg['detail'] = 0.0
            rep_msg['remark'] = 'MOBOTIX'
            log.debug(f'Send data: {rep_msg}')
            self.send(rep_msg)
        except Exception as e:
            log.error('Mobotix server send data format is wrong! error: {}'.format(e))

    def send(self, rep_msg):
        if callable(self.publish):
            self.publish(rep_msg)


if __name__ == '__main__':
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s:%(lineno)d] %(message)s")
    # log the things
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(formatter)
    log.addHandler(ch)

    loop = asyncio.get_event_loop()

    asyncio.sleep(10)

    mobotix = Mobotix(loop)
    mobotix.start()

    # Serve requests until Ctrl+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    loop.close()
