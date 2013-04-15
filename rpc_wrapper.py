#!/usr/bin/python

import inspect
import datetime

class RpcMethods:
    __advertized_functions = {}

    @staticmethod
    def add_function(function, version):
        if callable(function):
            #signature = inspect.getargspec(function)
            RpcMethods.__advertized_functions[function.__name__] = { 
                u'function': function,
                u'version': version
            }

    @staticmethod
    def get_methods():
        res = {}
        for name, item in RpcMethods.__advertized_functions.iteritems():
            res[name] = {}
            res[name][u'version'] = item[u'version']
            signature = inspect.getargspec(item[u'function'])
            res[name][u'args'] = signature.args
            res[name][u'varargs'] = signature.varargs
            res[name][u'keywords'] = signature.keywords
            res[name][u'defaults'] = signature.defaults
        return res

    @staticmethod
    def call_method(name, *args, **kwargs):
        method = RpcMethods.__advertized_functions[name]
        if not method:
            raise(NameError("Function '%s' not found!"))
        return method[u'function'].__call__(*args, **kwargs)


def advertized_function(version='0.0'):

    def function_maker(func):
        RpcMethods.add_function(func, version)
        return func

    return function_maker

def process_function_calls(calls, server_stub, digest):
    to_be_send = []
    for call in calls:
        res = { u'id': call[u'id'] }
        try:
            res[u'result'] = RpcMethods.call_method(call[u'name'], *call[u'*args'], **call[u'**kwargs'])
        except Exception, e:
            res[u'error'] = repr(e)

        to_be_send.append(res)

    return server_stub.router.propagate(digest, to_be_send)
