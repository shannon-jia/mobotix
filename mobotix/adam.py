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

    HEAD = b'\x00\x00\x00\x00\x00\x06'

    def __init__(self, loop, host, port=502):
        self.station_address = 1
        self.function_code = 5
        self.coil_address = 0x10
        self.send_str = b''

        self.loop = loop or asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.connected = None
        self.loop.create_task(self._do_connect())
        self.transport = None
        self.coils_state = 0
        self.transaction_id = 0
        self.protocol_id = 0
        # self.loop.call_later(6, self.keepAlive)

    async def _do_connect(self):
        while True:
            await asyncio.sleep(5)
            if self.connected:
                continue
            try:
                xt, _ = await self.loop.create_connection(
                    lambda: TcpClientProtocol(self),
                    self.host,
                    self.port)
                log.info('Connection create on {}'.format(xt))
                self.transport = xt
                self.connected = True
                self.read_coils_status()
                # self.login()
            except OSError:
                log.error('Server not up retrying in 5 seconds...')
            except Exception as e:
                log.error('Error when connect to server: {}'.format(e))

    def _command_head(self, length):
        self.transaction_id += 1
        s = struct.Struct('>HHH')
        values = (self.transaction_id,
                  self.protocol_id,
                  length)
        return s.pack(*values)

    # function code is 1
    def read_coils_status(self):
        self.send_str = self._command_head(6)
        s = struct.Struct('>BBHH')
        values = (self.station_address,
                  1,
                  self.coil_address,
                  8)
        self.send_str += s.pack(*values)
        log.info('Adam-6017 read_coil_status...')
        return self.call(self.send_str)

    # function code is 5
    def force_single_coil(self, address, action):
        if action.upper() == 'OFF':
            act = 0x0000
        elif action.upper() == 'ON':
            act = 0xFF00
        else:
            act = 0xFFFF

        self.send_str = self._command_head(6)
        s = struct.Struct('>BBHH')
        values = (self.station_address,
                  5,
                  address,
                  act)
        self.send_str += s.pack(*values)
        log.info('Adam-6017 Function[0x05]({})'.format(action, address))
        return self.call(self.send_str)

    # function code is f
    def force_multi_coils(self, data):
        self.send_str = self._command_head(8)
        s = struct.Struct('>BBHHBB')
        values = (self.station_address,
                  0x0f,
                  self.coil_address,
                  0x08,
                  0x01,
                  data)
        self.send_str += s.pack(*values)
        log.info('Adam-6017 Function[0x0F]({})'.format(data))
        return self.call(self.send_str)

    def call(self, cmd):
        log.info('Try to send: {}'.format(cmd))
        if self.transport:
            self.transport.write(cmd)
            log.debug('send cmd to server: {}'.format(cmd))
        else:
            log.error('Invalid server transport.')

    # zone = 0: do-0
    # zone = 1: do-1
    def alarm_task(self, action, task, zone=0):
        if action.upper() == 'OFF':
            self.coils_state &= ~(1 << zone)
        elif action.upper() == 'ON':
            self.coils_state |= (1 << zone)
        else:
            self.coils_state = 0

        self.force_single_coil(self.coil_address + zone,
                               action)
        # self.read_coils_status()
        # self.force_multi_coils(self.coils_state)


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

    port = 8502
    host = '127.0.0.1'
    adam = Adam(loop, host, port)

    asyncio.sleep(10)
    adam.alarm_task('ON', 1)
    adam.alarm_task('OFF', 1)
    adam.alarm_task('release', 1)
    adam.alarm_task('ON', 1, 1)
    adam.alarm_task('OFF', 1, 1)
    adam.alarm_task('release', 1, 1)

    # Serve requests until Ctrl+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    loop.close()
