# -*- coding: utf-8 -*-

"""Main module."""

import logging
import asyncio

log = logging.getLogger(__name__)


class Mobotix():
    """
    MOBOTIX system driver for SAM V1
    """

    def __init__(self, loop):
        self.loop = loop or asyncio.get_event_loop()

        self.publish = None
        self.actions = {}


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
        self.loop.call_later(1, self._auto_loop)

    # async def got_command(self, mesg):
    #     pass

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
