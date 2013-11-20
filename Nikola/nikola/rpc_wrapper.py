# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2013 CZ.NIC
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

import atsha204
import binascii

from jsonrpclib import Server

RANDOM_LEN = 32
DATE_LEN = 4


class WrappedServer(Server):
    def __init__(self, addr, serial=None):
        self.serial = binascii.hexlify(serial if serial else atsha204.get_serial())
        Server.__init__(self, addr)

    def init_session(self):

        res = self.api_turris_cz.init_session(self.serial)
        if 'random' in res and len(res['random']) == 2 * RANDOM_LEN \
           and 'timestamp' in res and len(res['timestamp']) == 2 * DATE_LEN:
            random = binascii.unhexlify(res['random'])
            timestamp = res['timestamp']
            session_key = timestamp + self.serial[:24] \
                + binascii.hexlify(atsha204.hmac(random))
            self._set_cookie('sessionid="%s"' % session_key)

        return res

    def _set_cookie(self, value):
        self.transport.cookie = value

    def _get_cookie(self):
        return self.transport.cookie
