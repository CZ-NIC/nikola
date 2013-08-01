#!/usr/bin/python

import os
import sys

server = sys.argv[1]
digest = sys.argv[2]
syslog_file = sys.argv[3]

syslog_date_format = '%b %d %H:%M:%S'
syslog_date_len = 15

max_packet_count = 1000

#logrotete the logs
#os.system('logrotate /_scripts/logrotate-iptables.conf')

from rpc_wrapper import WrappedServer
s = WrappedServer(server, digest)


from syslog_parser import parse_syslog
parsed = parse_syslog(syslog_file, syslog_date_len, syslog_date_format, year=2013)

print len(parsed)
print parsed[0]
if max_packet_count < len(parsed):
    msg = "To many data to send in one batch. (%d/%d)" % (len(parsed), max_packet_count)
    print msg
    print s.router.report_error(msg)
else:
    print s.router.store_logs(parsed)
