import logging


def get_log(debug=False):
    # configure log
    log = logging.getLogger("")
    formatter = logging.Formatter("%(asctime)s %(levelname)s " +
                                  "[%(module)s] %(message)s")
    # log the things
    ch = logging.StreamHandler()
    if debug:
        log.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    log.info('Start Runing...')
    return log
