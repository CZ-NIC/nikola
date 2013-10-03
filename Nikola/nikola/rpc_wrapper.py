#!/usr/bin/python

import atsha204
import binascii

from jsonrpclib import Server

RANDOM_LEN = 32
DATE_LEN = 4


class WrappedServer(Server):
    def __init__(self, addr, digest):
        self.digest = digest
        Server.__init__(self, addr)

    def init_session(self):

        res = self.collector.init_session(self.digest)
        if 'random' in res and len(res['random']) == 2 * RANDOM_LEN \
           and 'timestamp' in res and len(res['timestamp']) == 2 * DATE_LEN:
            random = binascii.unhexlify(res['random'])
            timestamp = res['timestamp']
            session_key = timestamp + self.digest[:24] \
                + binascii.hexlify(atsha204.hmac(random))
            self._set_cookie('sessionid="%s"' % session_key)

        return res

    def _set_cookie(self, value):
        self.transport.cookie = value

    def _get_cookie(self):
        return self.transport.cookie
