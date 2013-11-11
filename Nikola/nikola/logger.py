import logging
import logging.handlers


def get_logger(debug=False):

    # get logger name
    logger = logging.getLogger("nikola")

    # add syslog handler
    sys_handler = logging.handlers.SysLogHandler(address="/dev/log")
    logger.addHandler(sys_handler)

    # add console handler
    stream_handler = logging.StreamHandler()
    logger.addHandler(stream_handler)

    # set debug
    if debug:
        logger.setLevel(logging.DEBUG)

    return logger
