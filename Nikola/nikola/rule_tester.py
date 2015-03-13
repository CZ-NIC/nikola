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

import socket
import datetime

DATA = "testing packet, please ignore this"
TEST_RESULT_FILE = "/tmp/firewall-turris-status.txt"


def test_connect(test_ip):
    # calucate port (according to time) HH:MM -> 10HHMM
    now = datetime.datetime.now()
    port = 10000 + now.hour * 100 + now.minute

    # send a packet
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(DATA, 0, (test_ip, port))


def publish_result(records, rule_id):

    last_working = ""
    try:
        with open(TEST_RESULT_FILE, 'r') as f:
            for line in f.readlines():
                if line.startswith('last working time:'):
                    last_working = line.split(":", 1)[1].strip()

    except IOError:
        file_exists = False
    else:
        file_exists = True

    success_testing_times = []
    for record in records:
        time, data, count = record
        parsed_rule_id = data.rsplit("|", 1)[1].strip()
        if int(parsed_rule_id, 16) == int(rule_id, 16):
            success_testing_times.append(time)

    last_success = max(success_testing_times) if success_testing_times else None
    last_working = last_success if last_success else last_working
    # When the result file doesn't exist it means that nikola is run for the first time
    # so no testing packet was send and we can't determine the fw state yet
    answer = 'yes' if last_success else ('no' if file_exists else '???')

    with open(TEST_RESULT_FILE, 'w') as f:
        f.writelines([
            'turris firewall working: %s\n' % answer,
            'last working time: %s\n' % last_working,
        ])
