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


class History(object):
    """
    This holds all the response and request objects for a
    session. A server using this should call "clear" after
    each request cycle in order to keep it from clogging
    memory.
    """
    requests = []
    responses = []
    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def add_response(self, response_obj):
        self.responses.append(response_obj)

    def add_request(self, request_obj):
        self.requests.append(request_obj)

    @property
    def request(self):
        if len(self.requests) == 0:
            return None
        else:
            return self.requests[-1]

    @property
    def response(self):
        if len(self.responses) == 0:
            return None
        else:
            return self.responses[-1]

    def clear(self):
        del self.requests[:]
        del self.responses[:]
