#!/usr/bin/python

import atsha204
import binascii

from jsonrpclib import Server

RANDOM_LEN = 16


class WrappedServer(Server):
    def __init__(self, addr, digest):
        self.digest = digest
        self.client_signature = None
        self.server_signature = None
        Server.__init__(self, addr)

    def init_session(self):
        # TODO better random
        client_random = '\0' * RANDOM_LEN

        res = self.router.init_session(self.digest, binascii.hexlify(client_random))
        if 'server_random' in res and len(res['server_random']) == 2 * RANDOM_LEN:
            server_random = binascii.unhexlify(res['server_random'])
            self.client_signature = client_random + server_random
            self.server_signature = server_random + client_random

        self._test_prove_server(res)
        return res

    def _request(self, methodname, params, rpcid=None):
        if self.server_signature:

            # calculate next the next server signature
            self.server_signature = atsha204.hmac(self.server_signature)

            server_signature = binascii.hexlify(self.server_signature)
            params = (server_signature, ) + params if params else (server_signature, )

        res = Server._request(self, methodname, params, rpcid)
        self._test_prove_server(res)

        return res

    def _test_prove_server(self, res):
        if self.client_signature:

            # calculate next the next client signature
            self.client_signature = atsha204.hmac(self.client_signature)

            if not binascii.hexlify(self.client_signature) == res.get('server_prove', None):
                # Server is responded incorrectly -> clear the session
                self.client_signature = self.server_signature = None
