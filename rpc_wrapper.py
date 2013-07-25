#!/usr/bin/python

from jsonrpclib import Server

class WrappedServer(Server):
    def __init__(self, addr, digest):
        self.digest = digest
        Server.__init__(self, addr)

    def _request(self, methodname, params, rpcid=None):
        return Server._request(self, methodname, (self.digest,) + params, rpcid)
