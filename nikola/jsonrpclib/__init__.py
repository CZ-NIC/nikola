# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) Josh Marshall 2013 <catchjosh@gmail.com>
# Copyright (C) 2013 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from nikola.jsonrpclib.config import Config
config = Config.instance()
from nikola.jsonrpclib.history import History
history = History.instance()
from nikola.jsonrpclib.jsonrpc import Server, MultiCall, Fault
from nikola.jsonrpclib.jsonrpc import ProtocolError, loads, dumps
