# -*- coding: utf-8 -*-

"""Main module."""

import logging
import json
import asyncio
from urllib.parse import urlparse

log = logging.getLogger(__name__)

class TcpServerProtocol(asyncio.Protocol):
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        log.info('Server: Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        log.info('Server: Data received: {!r}'.format(data))
        # mesg = json.loads(data)
        if self.callback:
            self.callback(data)

        #self.transport.write(msg)


class Mobotix():
    """
    MOBOTIX system driver for SAM V1
    """

    def __init__(self, loop, tcp_svr):
        self.loop = loop or asyncio.get_event_loop()
        _url = urlparse(tcp_svr)
        self.host = _url.hostname or '0.0.0.0'
        self.port = _url.port or 9009

        self.publish = None

        coro = self.loop.create_server(
            lambda: TcpServerProtocol(callback=self.received),
            self.host, self.port)
        self.loop.run_until_complete(coro)

    def __str__(self):
        return "MOBOTIX"

    def get_info(self):
        return {'actions': 'MOBOTIX'}

    def set_publish(self, publish):
        if callable(publish):
            self.publish = publish
        else:
            self.publish = None

    def start(self):
        self._auto_loop()

    def _auto_loop(self):
        self.loop.call_later(1, self._auto_loop)

    def received(self, data):
        rep_msg = {}
        try:
            mesg = json.loads(data)
            if not mesg:
                return
            rep_msg['type'] = 'Auxiliary Input'
            rep_msg['name'] = mesg.get('camera')[4:]
            rep_msg['offset'] = 0
            rep_msg['time_stamp'] = mesg.get('time_stamp')
            rep_msg['source'] = 'publisher.protocols.ipp_host'
            rep_msg['detail'] = mesg.get('camera')
            rep_msg['remark'] = 'MOBOTIX'
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

    ###############

    asyncio.sleep(10)

    # Serve requests until Ctrl+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    loop.close()
