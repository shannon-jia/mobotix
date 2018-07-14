# -*- coding: utf-8 -*-

"""Main module."""

import json
import socket
from multiprocessing import *
import logging
from urllib.parse import urlparse
import asyncio

log = logging.getLogger(__name__)


class Mobotix():
    """
    MOBOTIX system driver for SAM V1
    """

    CLIENT_UDP_TIMEOUT = 5.0

    def __init__(self, loop, spk_svr):
        self.loop = loop or asyncio.get_event_loop()
        _url = urlparse(spk_svr)
        self.host = _url.hostname or 'localhost'
        self.port = _url.port or 9009

        self.publish = None
        self.actions = {}

        self.mesg = {'camera': 'cam_01', 'mode': 'auto', 'time_stamp': '2018-07-13'}

        # self.config_tcp_ser()

    def __str__(self):
        return "MOBOTIX"

    def get_info(self):
        return {'actions': self.actions}

    def set_publish(self, publish):
        if callable(publish):
            self.publish = publish
        else:
            self.publish = None

    def start(self):
        self._auto_loop()

    def _auto_loop(self):
        self.send(self.mesg)
        self.loop.call_later(5, self._auto_loop)

    def config_tcp_ser(self):
        ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ser_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = ('', self.port)
        ser_sock.bind(addr)
        ser_sock.listen(5)

        try:
            while True:
                log.debug('Waiting for Client comming ...')
                new_sock, dest_addr = ser_sock.accept()
                client = Process(target=self.deal_client, args=(new_sock, dest_addr))
                client.start()
                new_sock.close()
        finally:
            ser_sock.close()

    def deal_client(self, new_sock, dest_addr):
        while True:
            recv_data = new_sock.recv(1024).decode('utf-8')
            if len(recv_data) > 0:
                # self.deal_data(recv_data)
                log.info('recv[{:s}]: {:s}'.format(str(dest_addr), recv_data))
            else:
                log.warning('[{:s}] was closed!'.format(str(dest_addr)))
            break
        new_sock.close()

    def deal_data(self, recv_data):
        import types
        data = json.loads(recv_data)
        print(type(data), data)
        self.send(data)

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

    ser_url = 'tcp://localhost:9009'
    Mobotix(loop, spk_svr)

    asyncio.sleep(10)

    # Serve requests until Ctrl+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    loop.close()
