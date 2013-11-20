# Nikola - firewall log sender (a part of www.turris.cz project)
# Copyright (C) 2013 CZ.NIC
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

from datetime import datetime


def _parse_time_datetime(line, format, **kwargs):
    try:
        # Try to parse
        time = datetime.strptime(line, format)
        rest = ''
    except ValueError, v:
        # Get the length of unmatched characters
        unmatched_len = len(v.message.partition('unconverted data remains: ')[2])
        try:
            time = datetime.strptime(line[:-unmatched_len], format)
        except ValueError:
            # When second parsing return None as date
            return None, line

        rest = line[len(line) - unmatched_len:]

        # try to parse timezone in format +02:00
        timezone = rest[:6] if re.match(r'[+-][0-9]{2}:[0-9]{2}', rest) else ''

        # remove ':'
        timezone = timezone.replace(':', '')

    if kwargs:
        time = time.replace(**kwargs)

    return time.strftime('%Y-%m-%d %H:%M:%S' + timezone), rest


def _parse_line(line, date_format, **kwargs):

    # Cut the date
    date, rest = _parse_time_datetime(line, date_format, **kwargs)

    if not date:
        return None

    # Cut another part up to attributes
    splitted = rest.split(': ', 1)
    if len(splitted) != 2:
        return None

    # Parse the rest
    parsed = {}
    for x in splitted[1].split(' '):
        if '=' in x:
            key, val = x.split('=', 1)
            parsed[key] = val

    return date, "%s|%s|%s|%s|%s" % (
        parsed.get('SRC', ''),
        parsed.get('SPT', ''),
        parsed.get('DST', ''),
        parsed.get('DPT', ''),
        parsed['PROTO']
    )


def parse_syslog(path, date_format='%Y-%m-%dT%H:%M:%S', **kwargs):

    res = []

    with open(path) as f:
        last = None
        for line in f:
            parsed_line = _parse_line(line, date_format, **kwargs)
            if parsed_line:
                date, parsed = parsed_line
                # Same packets in the sequence
                if last and last == parsed:
                    res[-1][2] += 1
                else:
                    res.append([date, parsed, 1])
                    last = parsed

    return res
