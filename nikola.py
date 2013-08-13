#!/usr/bin/python

import optparse
import os

from rpc_wrapper import WrappedServer
from syslog_parser import parse_syslog

if __name__ == '__main__':

    # Parse the command line options
    optparser = optparse.OptionParser("usage: %prog [options] server_addr digest")
    optparser.add_option("-l", "--log-file", dest='syslog_file',
                         default='/var/log/iptables.1', type='string',
                         help='specify the syslog file to be parsed')

    optparser.add_option("-m", "--max", dest='max', default=1000, type='int',
                         help='max record count to be sent')

    optparser.add_option("-f", "--date-format", dest='date_format',
                         default='%Y-%m-%dT%H:%M:%S', type='string',
                         help='specify the syslog date format')

    optparser.add_option("-r", "--log-rotate-conf", dest='logrotate_conf',
                         default='/etc/logrotate.d/nikola', type='string',
                         help='specify the log rotate config to be triggered')

    syslog_date_len = 15

    (options, args) = optparser.parse_args()

    if len(args) != 2:
        optparser.error("incorrect number of arguments")

    server_addr = args[0]
    digest = args[1]
    syslog_file = options.syslog_file
    max_packet_count = options.max
    syslog_date_format = options.date_format
    logrotate_conf = options.logrotate_conf

    #logrotete the logs
    os.system('logrotate "%s"' % logrotate_conf)

    s = WrappedServer(server_addr, digest)

    # Parse syslog
    parsed = parse_syslog(syslog_file, syslog_date_len, syslog_date_format)

    print "Records parsed: %d" % len(parsed)
    print(parsed[0] if parsed else 'No records')
    if max_packet_count < len(parsed):
        msg = "To many data to send in one batch. (%d/%d)" % (len(parsed), max_packet_count)
        print msg
        print s.router.report_error(msg)
    else:
        print s.router.store_logs(parsed)
