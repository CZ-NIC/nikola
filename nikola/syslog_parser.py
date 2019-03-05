# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2013 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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

import re
import string

from datetime import datetime


TCP_FLAGS = {
    'NS': 0b100000000,
    'CWR': 0b010000000,
    'ECE': 0b001000000,
    'URG': 0b000100000,
    'ACK': 0b000010000,
    'PSH': 0b000001000,
    'RST': 0b000000100,
    'SYN': 0b000000010,
    'FIN': 0b000000001,
}


def _parse_time_datetime(line, format, **kwargs):
    # Only printable characters
    line = "".join([c for c in line if c in string.printable])
    try:
        # Try to parse
        time = datetime.strptime(line, format)
        rest = ''
    except (ValueError, TypeError) as v:
        # Get the length of unmatched characters
        error_repr = getattr(v, "message", str(v))
        unmatched_len = len(error_repr.partition('unconverted data remains: ')[2])
        try:
            time = datetime.strptime(line[:-unmatched_len], format)
        except (ValueError, TypeError):
            # When second parsing return None as date
            return None, None, line

        rest = line[len(line) - unmatched_len:]

        # try to parse timezone in format +02:00
        timezone = rest[:6] if re.match(r'[+-][0-9]{2}:[0-9]{2}', rest) else ''

        # remove ':'
        timezone = timezone.replace(':', '')

    if kwargs:
        time = time.replace(**kwargs)

    return time.strftime('%Y-%m-%d %H:%M:%S' + timezone), int(time.timestamp()), rest


def _parse_line(line, wans, date_format, **kwargs):

    # Cut the date
    date_str, date_int, rest = _parse_time_datetime(line, date_format, **kwargs)

    if not date_str:
        return None

    # Cut another part up to attributes
    splitted = rest.split(': ', 1)
    if len(splitted) != 2:
        return None
    prefix = splitted[0].rsplit(' ', 1)[1]

    # prefix should look like turris[-1A5B7D]:
    if 'turris' not in prefix:
        # don't send other logged packets
        return None
    rule_id = prefix.rsplit('-', 1)[1] if '-' in prefix else ''

    # Parse the rest
    parsed = {}
    flags = 0b0
    for x in splitted[1].split(' '):
        if '=' in x:
            key, val = x.split('=', 1)
            parsed[key] = val
        else:
            flags |= TCP_FLAGS.get(x, 0b0)

    # When the protocol is missing it might be caused by that
    # syslog hasn't put the whole line into log file yet
    # In this case we'll skip the line
    if 'PROTO' not in parsed:
        return None

    # Check whether wan interface is present (otherwise considered as a local traffic)
    res = {}
    res["event_time"] = date_str
    res["ts"] = date_int
    res["packet_count"] = 1
    res["flags"] = "{0:09b}".format(flags)
    res["rule_id"] = rule_id
    res["protocol"] = parsed.get('PROTO', '')
    if parsed.get('IN', '') in wans:
        res["dir"] = 'I'
        res["ip"] = parsed.get('SRC', '')
        res["port"] = parsed.get('SPT', '')
        res["local_ip"] = parsed.get('DST', '')
        res["local_port"] = parsed.get('DPT', '')
    elif parsed.get('OUT', '') in wans:
        res["dir"] = 'O'
        res["ip"] = parsed.get('DST', '')
        res["port"] = parsed.get('DPT', '')
        res["local_ip"] = parsed.get('SRC', '')
        res["local_port"] = parsed.get('SPT', '')
    else:
        return None

    return res


def parse_syslog(path, wans, date_format='%Y-%m-%dT%H:%M:%S', logger=None, **kwargs):
    res = []

    with open(path) as f:
        last = None
        for line in f:
            parsed = _parse_line(line, wans, date_format, **kwargs)
            if parsed:
                # Same packets in the sequence; We should compare only a subset
                # of the dictionary fields, however this would be enough
                if last == parsed:
                    res[-1]["packet_count"] += parsed["packet_count"]
                else:
                    res.append(parsed)
                last = parsed
            else:
                logger and logger.warning("Failed to parse line: '%s'" % line)

    return res
