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
import ipaddress
import random
import socket
import subprocess
import sys
import time
import traceback
import zmq
import msgpack

from nikola.filter import filter_records
from nikola.logger import get_logger
from nikola.syslog_parser import parse_syslog
from nikola.tester import test_connect, publish_result


logger = None


def send_test_packet(test_ip):
    logger.debug("Trying to send a testing packet (it should be blocked by the firewall).")
    try:
        test_connect(test_ip)
        logger.error("turris firewall rules might not be active")
    except socket.error as e:
        # sending should failed when the rules are applied
        logger.debug("Failed to send the testing packet (this is expected - blocked by firewall)")
    except Exception as e:
        logger.error("failed to send the testing packet: %s" % e)
        e_type, e_value, e_traceback = sys.exc_info()
        logger.error("Exception traceback: %s" % str(traceback.extract_tb(e_traceback)))


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
        "-m", "--max", dest='max', default=1000, help='max record count to be sent', type=int,
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
        "-t", "--test-ip", dest='test_ip', default='192.0.2.84', type=str,
        help='the address which is used for rule testing purposes'
    )

    parser.add_argument(
        "-u", "--test-ruleid", dest='test_rule_id', default='00DEB060', type=str,
        help='this rule id is used for a testing purposes'
    )

    parser.add_argument(
        "-j", "--just-test", dest='just_test', action='store_true', default=False,
        help='just try to send a test packet'
    )

    parser.add_argument(
        "-n", "--now", dest='now', action='store_true', default=False,
        help='don\'t use random sleep interval'
    )

    options = parser.parse_args()

    global logger
    logger = get_logger(options.debug)

    syslog_file = options.syslog_file
    max_packet_count = options.max
    syslog_date_format = options.date_format
    logrotate_conf = options.logrotate_conf
    wans = [e.strip() for e in options.wans.split(",") if e.strip()] if options.wans else []
    now = options.now
    test_ip = options.test_ip
    test_rule_id = options.test_rule_id
    just_test = options.just_test
    topic = options.topic
    socket_path = options.socket_path
    if just_test:
        send_test_packet(test_ip)
        sys.exit()

    parsed = []

    logger.debug("Nikola synchronization is starting...")
    logger.info("recognized WAN interfaces: " + ", ".join(wans))

    if not now:
        # sleep for random amount of time up to one minute
        seconds = random.randrange(60)
        logger.debug("Sleeping for %d seconds." % seconds)
        time.sleep(seconds)

    last_time = time.time()

    failed = False
    try:
        logger.info("Establishing connection took %f seconds" % (time.time() - last_time))
        last_time = time.time()

        if not wans:
            logger.warning('No WAN device was set. No data will be send to the server!')

        if os.path.exists(syslog_file) and wans:
            # logrotete the logs
            output = subprocess.check_output(
                ('/usr/sbin/logrotate', '-f', logrotate_conf, )
            )
            logger.debug(("logrotate output: %s" % output))

            logger.info("Logrotate took %f seconds" % (time.time() - last_time))
            last_time = time.time()

            # Parse syslog
            parsed = parse_syslog("%s.1" % syslog_file, wans, syslog_date_format, logger=logger)

            logger.info("Syslog parsing took %f seconds" % (time.time() - last_time))
            last_time = time.time()

        else:
            # To file to parse means no records
            parsed = []

        logger.info(("Records parsed: %d" % len(parsed)))
        parsed = filter_records(
            parsed, max_packet_count,
            lambda ip: ipaddress.ip_address(ip).is_global,
            lambda ip: ipaddress.ip_address(ip) != ipaddress.ip_address("255.255.255.255"))
        logger.info(("Records after filtering: %d" % len(parsed)))
        logger.info("Records filtering took %f seconds" % (time.time() - last_time))
        last_time = time.time()

        logger.debug(("First record: %s" % parsed[0]) if parsed else 'No records')

        with zmq.Context() as context, context.socket(zmq.PUSH) as zmq_sock:
                zmq_sock.setsockopt(zmq.SNDTIMEO, 10000)
                zmq_sock.setsockopt(zmq.LINGER, 10000)
                zmq_sock.connect(socket_path)
                zmq_sock.send_multipart([topic.encode(), msgpack.packb(parsed, use_bin_type=True)])

        logger.info("Sending records took %f seconds" % (time.time() - last_time))
        last_time = time.time()

    except Exception as e:
        failed = True
        logger.error("Exception thrown: %s" % e)
        e_type, e_value, e_traceback = sys.exc_info()
        logger.error("Exception traceback: %s" % str(traceback.extract_tb(e_traceback)))

    # publish whether the rules are applied
    try:
        publish_result(parsed, test_rule_id, failed)
    except Exception as e:
        e_type, e_value, e_traceback = sys.exc_info()
        logger.error("error during rule test: %s" % e)
        e_type, e_value, e_traceback = sys.exc_info()
        logger.error("Exception traceback: %s" % str(traceback.extract_tb(e_traceback)))

    # try to send the testing packet
    send_test_packet(test_ip)


if __name__ == '__main__':
    main()
