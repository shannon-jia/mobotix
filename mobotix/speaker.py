# -*- coding: utf-8 -*-

"""Main module."""

import logging
import time
import asyncio
log = logging.getLogger(__name__)


class SpeakerV1():
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.actions = {}

    def __str__(self):
        return "Speaker V1"

    def get_info(self):
        return {
            'actions': self.actions
        }

    def set_publish(self, publish):
        if callable(publish):
            self.publish = publish
        else:
            self.publish = None

    def start(self):
        self._auto_loop()

    def _auto_loop(self):
        # self._update_actions()
        # log.debug('Actions: {}'.format(self.actions))
        self.loop.call_later(1, self._auto_loop)

    # def _register(self, act, status, timeout):
    #     self.actions[act] = {
    #         'status': status,
    #         'timeout': int(timeout),
    #         'timestamp': self._time_stamp()
    #     }

    # def _update_actions(self):
    #     for act, val in self.actions.items():
    #         timeout = val.get('timeout', 0)
    #         _status = val.get('status')
    #         _time_stamp = val.get('timestamp')
    #         if timeout >= 1:
    #             timeout -= 1
    #             if timeout <= 1:
    #                 self._release(act)
    #                 _status = 'Off/Stop'
    #                 _time_stamp = self._time_stamp()
    #             self.actions[act] = {
    #                 'status': _status,
    #                 'timeout': int(timeout),
    #                 'timestamp': _time_stamp
    #             }

    # def _time_stamp(self):
    #     t = time.localtime()
    #     time_stamp = '%d-%02d-%02d %02d:%02d:%02d' % (t.tm_year,
    #                                                   t.tm_mon,
    #                                                   t.tm_mday,
    #                                                   t.tm_hour,
    #                                                   t.tm_min,
    #                                                   t.tm_sec)
    #     return time_stamp

    # async def got_command(self, mesg):
    #     try:
    #         log.info('Speaker received: {}'.format(mesg))
    #         action = mesg.get('name')
    #         if action is None:
    #             return None
    #         args = mesg.get('args')
    #         status = mesg.get('status')
    #         if status is '':
    #             status = None
    #         else:
    #             status = status.upper()
    #         if type(action) is list:
    #             for act in action:
    #                 await self._do_action(act, args, status)
    #         elif type(action) is str:
    #             await self._do_action(action, args, status)
    #     except Exception as e:
    #         log.error('Speaker do_action() exception: {}'.format(e))

    # async def _do_action(self, act, args, status):
    #     raise NotImplementedError

    # def _release(self, act, args, status):
    #     raise NotImplementedError
