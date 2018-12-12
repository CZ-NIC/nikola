# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2013 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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

import calendar
import datetime
import socket

DATA = "testing packet, please ignore this"
TEST_RESULT_FILE = "/tmp/firewall-turris-status.txt"


def test_connect(test_ip):
    # calucate port (according to time) HH:MM -> 10HHMM
    now = datetime.datetime.now()
    port = 10000 + now.hour * 100 + now.minute

    # send a packet
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(DATA.encode(), 0, (test_ip, port))


def _convert_date_string_to_long(string):
    offset = int(string[-5:]) * 60 * 60 / 100
    parsed_time = datetime.datetime.strptime(string[:-5], '%Y-%m-%d %H:%M:%S')
    return calendar.timegm(parsed_time.timetuple()) - offset


def publish_result(records, rule_id, failed):

    # Try to parse the file
    last_server_time = ""
    last_packet_timestamp = 0
    try:
        with open(TEST_RESULT_FILE, 'r') as f:
            for line in f.readlines():
                if line.startswith('last working time:'):
                    last_server_time = line.split(":", 1)[1].strip()
                if line.startswith('last packet test success timestamp:'):
                    last_packet_timestamp = int(line.split(":", 1)[1].strip() or 0)

    except IOError:
        file_exists = False
    else:
        file_exists = True

    # Server connection
    if not failed:
        last_server_time = datetime.datetime.utcnow()
        last_server_time = last_server_time.strftime('%Y-%m-%d %H:%M:%S') + "+0000"

    server_working = not failed
    last_server_timestamp = _convert_date_string_to_long(last_server_time) \
        if last_server_time else ""
    server_answer = 'yes' if server_working else 'no'

    # Testing packet
    success_packet_times = []
    for record in records:
        parsed_rule_id = record["rule_id"]
        if int(parsed_rule_id, 16) == int(rule_id, 16):
            success_packet_times.append(record["ts"])

    last_packet_timestamp = max(success_packet_times) if success_packet_times else last_packet_timestamp
    packet_working = True if success_packet_times else False

    # When the result file doesn't exist it means that nikola is run for the first time
    # so no testing packet was send and we can't determine the fw state yet
    packet_answer = 'yes' if packet_working else ('no' if file_exists else '???')

    with open(TEST_RESULT_FILE, 'w') as f:
        f.writelines([
            'turris firewall working: %s\n' % server_answer,
            'last working time: %s\n' % last_server_time,
            'last working timestamp: %s\n' % last_server_timestamp,
            'packet test working: %s\n' % packet_answer,
            'last packet test success timestamp: %s\n' % last_packet_timestamp,
        ])
