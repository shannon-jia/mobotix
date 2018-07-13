#!/usr/bin/env python3
# _*_ coding: utf-8 _*_

import asyncio
import logging
import struct


log = logging.getLogger(__name__)


class TcpClientProtocol(asyncio.Protocol):

    def __init__(self, master):
        self.master = master

    def connection_made(self, transport):
        self.transport = transport
        self.master.connected = True

    def data_received(self, data):
        log.info('Data received: {!r}'.format(data))

    def connection_lost(self, exc):
        log.error('The server closed the connection')
        self.master.connected = None


class Adam(object):


    def __init__(self, loop, host, port=502):
        self.loop = loop or asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.connected = None
        self.loop.create_task(self._do_connect())
        self.transport = None

    async def _do_connect(self):
        while True:
            await asyncio.sleep(5)
            if self.connected:
                continue
            try:
                print(self.host)
                xt, _ = await self.loop.create_connection(
                    lambda: TcpClientProtocol(self),
                    self.host,
                    self.port)
                log.info('Connection create on {}'.format(xt))
                self.transport = xt
                self.connected = True
            except OSError:
                log.error('Server not up retrying in 5 seconds...')
            except Exception as e:
                log.error('Error when connect to server: {}'.format(e))


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

    port = 9009
    host = '127.0.0.1'
    adam = Adam(loop, host, port)

    asyncio.sleep(10)

    # Serve requests until Ctrl+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    loop.close()
