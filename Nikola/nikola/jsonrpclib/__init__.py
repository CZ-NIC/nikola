from nikola.jsonrpclib.config import Config
config = Config.instance()
from nikola.jsonrpclib.history import History
history = History.instance()
from nikola.jsonrpclib.jsonrpc import Server, MultiCall, Fault
from nikola.jsonrpclib.jsonrpc import ProtocolError, loads, dumps
