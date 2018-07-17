# -*- coding: utf-8 -*-
"""Router with RabbitMQ topic exchange"""

import asyncio
import logging
import asynqp
from urllib.parse import urlparse

# RABBITMQ_HOST = 'localhost'
# RABBITMQ_PORT = 5672
# RABBITMQ_USERNAME = 'guest'
# RABBITMQ_PASSWORD = 'guest'
# RABBITMQ_VIRTUAL_HOST = '/'

# EXCHANGE = 'sam.router'
# QUEUE = 'sam.queue'
RECONNECT_BACKOFF = 1.0

log = logging.getLogger(__name__)


class RouterMQ():
    """Router based on RabbitMQ with exchange topic."""

    def __init__(self, outgoing_key='Alarms.keeper',
                 routing_keys='#',
                 queue_name=None,
                 callback=None,
                 exchange='sam.router',
                 url=None,
                 host='localhost',
                 port=5672,
                 login='guest',
                 password='guest',
                 virtualhost='/'):
        self.connection = None
        self.channel = None
        self.exchange = None
        self.queue = None
        self.consumer = None
        self.send_packet = None
        self.routing_keys = routing_keys
        self.queue_name = queue_name or 'undefined'
        self.outgoing_key = outgoing_key
        self.callback = callback

        _host = _port = _login = _password = _virtualhost = None
        if url:
            _url = urlparse(url)
            _host = _url.hostname
            _port = _url.port
            _login = _url.username
            _password = _url.password
            _virtualhost = _url.path[1:]

        self.MQ_HOST = _host or host
        self.MQ_PORT = _port or port
        self.MQ_LOGIN = _login or login
        self.MQ_PASSWORD = _password or password
        self.MQ_VIRTUAL_HOST = _virtualhost or virtualhost
        self.EXCHANGE = exchange

    def get_info(self):
        return {
            'hostname': self.MQ_HOST,
            'port': self.MQ_PORT,
            'username': self.MQ_LOGIN,
            'password': '******',
            'virtualhost': self.MQ_VIRTUAL_HOST,
            'queue': self.queue_name,
            'outgoing_key': self.outgoing_key,
            'routing_keys': self.routing_keys,
            'exchange': self.EXCHANGE,
            'type': 'AMQP',
        }

    def set_callback(self, callback):
        """Set the function to process received message"""
        self.callback = callback

    def connect(self):
        asyncio.ensure_future(self.reconnector())

    async def _connect(self):
        """Connects to the amqp exchange and queue"""
        def log_returned_message(message):
            """Log when message has no handler in message queue"""

            log.warning("Nobody cared for {0} {1}".format(message.routing_key,
                                                          message.json()))

        # self.connection = await asynqp.connect(
        #     self.MQ_HOST,
        #     int(self.MQ_PORT),
        #     self.MQ_LOGIN,
        #     self.MQ_PASSWORD,
        #     self.MQ_VIRTUAL_HOST
        # )
        try:
            self.connection = await asynqp.connect(
                self.MQ_HOST,
                int(self.MQ_PORT),
                self.MQ_LOGIN,
                self.MQ_PASSWORD,
                self.MQ_VIRTUAL_HOST
            )
            self.channel = await self.connection.open_channel()
            self.channel.set_return_handler(log_returned_message)
            self.exchange = await self.channel.declare_exchange(self.EXCHANGE,
                                                                'topic')
            self.queue = await self.channel.declare_queue(self.queue_name,
                                                          auto_delete=True)
            for routing_key in self.routing_keys:
                await self.queue.bind(self.exchange, routing_key)
            self.consumer = await self.queue.consume(self.handle_message)
        except asynqp.AMQPError as err:
            log.error("Could not consume on queue.".format(err))
            if self.connection:
                await self.connection.close()
        except Exception as err:
            log.error('Amqp Connection Error: {}'.format(err))
            if self.connection:
                await self.connection.close()

    async def reconnector(self):
        try:
            while True:
                if self.connection is None or self.connection.is_closed():
                    url = 'amqp://{}:{}@{}:{}{}'.format(self.MQ_LOGIN,
                                                        self.MQ_PASSWORD,
                                                        self.MQ_HOST,
                                                        self.MQ_PORT,
                                                        self.MQ_VIRTUAL_HOST)
                    log.info("Connecting to rabbitmq [{}] ...".format(url))
                    try:
                        await self._connect()
                    except Exception as err:
                        log.error("Failed to connect to rabbitmq Error: {} "
                                  "Will retry in {} seconds"
                                  .format(err, RECONNECT_BACKOFF))
                        self.connection = None
                    if self.connection is None:
                        await asyncio.sleep(RECONNECT_BACKOFF)
                    else:
                        log.info("RabbitMQ Successfully connected. ")
                # poll connection state every 100ms
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            if self.connection is not None:
                await self.connection.close()
        except Exception as err:
            log.error("Connect to rabbitmq have Error: {}".format(err))
            if self.connection is not None:
                await self.connection.close()

    def publish(self, mesg, outgoing_key=None):
        """Route publish packet from client to message queue"""
        try:
            key = outgoing_key or self.outgoing_key or ''
            msg = asynqp.Message(mesg, content_encoding='utf-8')
            if self.exchange:
                self.exchange.publish(msg, key)
                log.debug("To %s: %s", key, mesg)
            else:
                log.error("Could not publish, because exchange is not exist")
        except Exception as err:
            log.error('Could not publish, because some error: {}'.format(err))

    def handle_message(self, message):
        """Handle message coming from rabbitmq and route them to the
           respective clients"""
        routing_key = message.routing_key
        json = message.json()
        log.debug("From [%s] %s", routing_key, json)
        if self.callback:
            asyncio.ensure_future(self.callback(json))


def main(debug=True):
    # configure log
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s] %(message)s")
    # log the things
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # ch.setLevel(logging.ERROR)
    # ch.setLevel(logging.CRITICAL)
    if debug:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    global loop
    loop = asyncio.get_event_loop()
    loop.set_debug(0)

    router = RouterMQ(outgoing_key='Alarms.keeper',
                      routing_keys=['Actions.*'],
                      queue_name='keeper',
                      host='localhost')
    reconnect_amqp_task = loop.create_task(router.reconnector())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        reconnect_amqp_task.cancel()
        loop.run_until_complete(reconnect_amqp_task)
    finally:
        loop.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(1)
