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


import argparse
import os
import random
import subprocess
import sys
import time
import traceback
import zmq
import msgpack

from nikola.logger import get_logger
from nikola.syslog_parser import parse_syslog


logger = None


def main():

    # Parse the command line options
    parser = argparse.ArgumentParser(prog="nikola")
    parser.add_argument(
        "-s", "--socket", dest='socket_path', default='ipc:///tmp/sentinel_pull.sock',
        type=str, help='set the socket path'
    )

    parser.add_argument(
        "-T", "--topic", dest='topic', default='sentinel/collect/fwlogs',
        type=str, help='topic'
    )

    parser.add_argument(
        "-l", "--log-file", dest='syslog_file', default='/var/log/iptables', type=str,
        help='specify the syslog file to be parsed'
    )

    parser.add_argument(
        "-f", "--date-format", dest='date_format', default='%Y-%m-%dT%H:%M:%S', type=str,
        help='specify the syslog date format'
    )

    parser.add_argument(
        "-r", "--log-rotate-conf", dest='logrotate_conf', default='/etc/logrotate.d/iptables',
        type=str, help='specify the log rotate config to be triggered'
    )

    parser.add_argument(
        "-d", "--debug", dest='debug', action='store_true', default=False,
        help='use debug output'
    )

    parser.add_argument(
        "-w", "--wan-interfaces", dest='wans', default=None, type=str,
        help='comma separated list of wan interfaces'
    )

    parser.add_argument(
        "-n", "--now", dest='now', action='store_true', default=True,
        help='don\'t use random sleep interval (this is default behavior)'
    )

    parser.add_argument(
        "--random-sleep", dest='now', action='store_false', default=True,
        help='Use random sleep interval'
    )

    options = parser.parse_args()

    global logger
    logger = get_logger(options.debug)

    syslog_file = options.syslog_file
    syslog_date_format = options.date_format
    logrotate_conf = options.logrotate_conf
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
            last_time = time.time()
            # logrotete the logs
            output = subprocess.check_output(
                ('/usr/sbin/logrotate', '-f', logrotate_conf, )
            )
            logger.debug(("logrotate output: %s" % output))

            logger.info("Logrotate took %f seconds" % (time.time() - last_time))
            last_time = time.time()

            # Parse syslog
            parsed = parse_syslog("%s.1" % syslog_file, syslog_date_format, logger=logger)

            logger.info("Syslog parsing took %f seconds" % (time.time() - last_time))

        else:
            # To file to parse means no records
            parsed = []

        logger.info(("Records parsed: %d" % len(parsed)))
        last_time = time.time()

        with zmq.Context() as context, context.socket(zmq.PUSH) as zmq_sock:
                zmq_sock.setsockopt(zmq.SNDTIMEO, 10000)
                zmq_sock.setsockopt(zmq.LINGER, 10000)
                zmq_sock.connect(socket_path)
                zmq_sock.send_multipart([topic.encode(), msgpack.packb(parsed, use_bin_type=True)])

        logger.info("Sending records took %f seconds" % (time.time() - last_time))

    except Exception as e:
        logger.error("Exception thrown: %s" % e)
        e_type, e_value, e_traceback = sys.exc_info()
        logger.error("Exception traceback: %s" % str(traceback.extract_tb(e_traceback)))


if __name__ == '__main__':
    main()
