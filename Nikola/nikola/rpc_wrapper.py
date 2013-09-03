#!/usr/bin/python

import atsha204
import binascii

from jsonrpclib import Server

RANDOM_LEN = 32
DATE_LEN = 4


class WrappedServer(Server):
    def __init__(self, addr, digest):
        self.digest = digest
        self.session_key = None
        Server.__init__(self, addr)

    def init_session(self):

        res = self.router.init_session(self.digest)
        if 'random' in res and len(res['random']) == 2 * RANDOM_LEN \
           and 'timestamp' in res and len(res['timestamp']) == 2 * DATE_LEN:
            random = binascii.unhexlify(res['random'])
            timestamp = res['timestamp']
            self.session_key = timestamp + self.digest[:24] \
                + binascii.hexlify(atsha204.hmac(random))

        return res

    def _request(self, methodname, params, rpcid=None):
        if self.session_key:

            params = (self.session_key, ) + params if params else (self.session_key, )

        res = Server._request(self, methodname, params, rpcid)

        return res
