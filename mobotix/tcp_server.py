# -*- coding: utf-8 -*-

"""TCP Server"""

import json
import socket
from multiprocessing import *
import logging
from urllib.parse import urlparse
import asyncio

log = logging.getLogger(__name__)


class TcpServer():


    def __init__(self, loop, tcp_svr, site=None):
        self.loop = loop or asyncio.get_event_loop()
        _url = urlparse(tcp_svr)
        self.host = _url.hostname or 'localhost'
        self.port = _url.port or 9009
        self.site = site

    def start(self):
        self.config_tcp_ser()

    def config_tcp_ser(self):
        ser_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ser_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = ('', self.port)
        ser_sock.bind(addr)
        ser_sock.listen(5)

        try:
            while True:
                log.info('Waiting for Client comming ...')
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
                self.deal_data(recv_data)
                log.info('recv[{:s}]: {:s}'.format(str(dest_addr), recv_data))
            else:
                log.warning('[{:s}] was closed!'.format(str(dest_addr)))
            break
        new_sock.close()

    def deal_data(self, recv_data):
        data = json.loads(recv_data)
        import types
        print(type(data), data)
        self.site.send(data)


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

    tcp_svr = 'tcp://localhost:9009'
    tcp_server = TcpServer(loop, tcp_svr)
    tcp_server.start()

    asyncio.sleep(10)

    # Serve requests until Ctrl+C is pressed
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    loop.close()
