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

import atsha_fake

from sentinel_nikola.jsonrpclib import Server

RANDOM_LEN = 32


class WrappedServer(Server):
    def __init__(self, addr, serial, key, slot_id=0):
        self.serial = serial
        self.key = key
        self.slot_id = slot_id
        self.challenge = None
        self.response = None
        self.session_id = None
        Server.__init__(self, addr)

    def connect_when_not_connected(self):
        # connect when not connected
        if not self.transport._connection or self.transport._connection == (None, None):
            conn = self.transport.make_connection(self.host)
            conn.connect()

    def init_session(self):

        res = self.api_turris_cz.init_session(self.serial)
        if 'random' in res and len(res['random']) == 2 * RANDOM_LEN:
            self.challenge = res['random']
            self.session_id = res['session_id']
            self.response = atsha_fake.emulate_hmac(
                self.slot_id, self.serial, self.key, self.challenge)
            self._set_cookie('sessionid="%s" response="%s"' % (self.session_id, self.response))

        return res

    def _set_cookie(self, value):
        self.transport.cookie = value

    def _get_cookie(self):
        return self.transport.cookie
