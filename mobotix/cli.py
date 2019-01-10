# -*- coding: utf-8 -*-

"""Console script for rps."""

import click
from .log import get_log
from .routermq import RouterMQ
from .mobotix import Mobotix
from .api import Api
import asyncio


def validate_url(ctx, param, value):
    try:
        return value
    except ValueError:
        raise click.BadParameter('url need to be format: tcp://ipv4:port')


@click.command()
@click.option('--mob_svr', default='tcp://0.0.0.0:9009',
              callback=validate_url,
              envvar='MOB_SVR',
              help='Mobotix Server Received URL, \n \
              ENV: MOB_SVR, default: tcp://0.0.0.0:9009')
@click.option('--amqp', default='amqp://guest:guest@rabbit:5672//',
              callback=validate_url,
              envvar='SVC_AMQP',
              help='Amqp url, also ENV: SVC_AMQP')
@click.option('--port', default=80,
              envvar='SVC_PORT',
              help='Api port, default=80, ENV: SVC_PORT')
@click.option('--qid', default=1,
              envvar='SVC_QID',
              help='ID for amqp queue name, default=0, ENV: SVC_QID')
@click.option('--debug', is_flag=True)
def main(mob_svr, amqp, port, qid, debug):
    """Publisher for PM-1 with IPP protocol"""

    click.echo("See more documentation at http://www.mingvale.com")

    info = {
        'server_url': mob_svr,
        'api_port': port,
        'amqp': amqp,
    }
    log = get_log(debug)
    log.info('Basic Information: {}'.format(info))

    loop = asyncio.get_event_loop()
    loop.set_debug(0)

    # main process
    try:
        site = Mobotix(loop, tcp_svr=mob_svr)
        router = RouterMQ(outgoing_key='Alarms.keeper',
                          routing_keys=['Actions.mobotix'],
                          queue_name='mobotix_'+str(qid),
                          url=amqp)
        router.set_callback(site.got_command)
        site.set_publish(router.publish)
        api = Api(loop=loop, port=port, site=site, amqp=router)
        site.start()
        amqp_task = loop.create_task(router.reconnector())
        api.start()
        loop.run_forever()
    except KeyboardInterrupt:
        if amqp_task:
            amqp_task.cancel()
            loop.run_until_complete(amqp_task)
        site.stop()
    except Exception as e:
        log.error(e)
    finally:
        loop.stop()
        loop.close()
