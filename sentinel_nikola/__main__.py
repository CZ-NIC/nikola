#
# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2018 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#


import json
import os
import random
import subprocess
import sys
import time
import traceback
import zmq
import msgpack

from .argparser import get_arg_parser
from .logger import get_logger
from .syslog_parser import parse_syslog


logger = None


def main():
    parser = get_arg_parser()
    options = parser.parse_args()

    global logger
    logger = get_logger(options.debug)

    syslog_file = options.syslog_file
    syslog_date_format = options.date_format
    now = options.now
    topic = options.topic
    socket_path = options.socket_path

    parsed = []

    logger.debug("Nikola synchronization is starting...")

    if not now:
        # sleep for random amount of time up to one minute
        seconds = random.randrange(60)
        logger.debug("Sleeping for %d seconds." % seconds)
        time.sleep(seconds)

    try:
        if os.path.exists(syslog_file):
            if not options.dont_rotate:
                syslog_file = rotate_syslog_file(syslog_file, options.logrotate_conf)

            last_time = time.time()
            parsed = parse_syslog(syslog_file, syslog_date_format, logger=logger)
            logger.info("Syslog parsing took %f seconds" % (time.time() - last_time))

        else:
            logger.warn("Requested syslog file {} not found".format(syslog_file))

        logger.info(("Records parsed: %d" % len(parsed)))

        if options.log_parsed:
            if options.json_log:
                logger.debug(json.dumps(parsed, indent=2))
            else:
                logger.debug(parsed)

        if not options.dont_send:
            send_parsed(socket_path, topic, parsed)

    except Exception as e:
        logger.error("Exception thrown: %s" % e)
        e_type, e_value, e_traceback = sys.exc_info()
        logger.error("Exception traceback: %s" % str(traceback.extract_tb(e_traceback)))


def rotate_syslog_file(syslog_file, conf):
    last_time = time.time()
    output = subprocess.check_output(
        ('/usr/sbin/logrotate', '-f', conf, )
    )
    logger.debug(("logrotate output: %s" % output))

    logger.info("Logrotate took %f seconds" % (time.time() - last_time))
    return "{}.1".format(syslog_file)


def send_parsed(socket_path, topic, parsed):
    last_time = time.time()

    with zmq.Context() as context, context.socket(zmq.PUSH) as zmq_sock:
            zmq_sock.setsockopt(zmq.SNDTIMEO, 10000)
            zmq_sock.setsockopt(zmq.LINGER, 10000)
            zmq_sock.connect(socket_path)
            zmq_sock.send_multipart([topic.encode(), msgpack.packb(parsed, use_bin_type=True)])

    logger.info("Sending records took %f seconds" % (time.time() - last_time))


if __name__ == '__main__':
    main()
