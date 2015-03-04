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


def test_connect(test_ip):
    # calucate port (according to time) HH:MM -> 10HHMM
    now = datetime.datetime.now()
    port = 10000 + now.hour * 100 + now.minute
    # init the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # send a packet
    sock.sendto(DATA, (test_ip, port))
