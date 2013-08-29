#!/usr/bin/python

import atsha204
import binascii

from jsonrpclib import Server


def _mix_randoms(client_random, server_random):
    """
    Mix two streams of data (expects both numbers in binary)
    """
    if len(server_random) != len(client_random):
        raise IndexError('Random numbers should have same length')

    length = len(server_random)
    res = ""

    for i in range(length):
        res += client_random[i] + server_random[i]

    return res[:length], res[-length:]


class WrappedServer(Server):
    def __init__(self, addr, digest):
        self.digest = digest
        self.client_signature = None
        self.server_signature = None
        Server.__init__(self, addr)

    def init_session(self):
        # TODO better random
        client_random = '\0' * 32

        res = self.router.init_session(self.digest, binascii.hexlify(client_random))
        if 'server_random' in res:
            server_random = binascii.unhexlify(res['server_random'])
            client_random, server_random = _mix_randoms(client_random, server_random)
            self.client_signature = client_random
            self.server_signature = server_random

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
