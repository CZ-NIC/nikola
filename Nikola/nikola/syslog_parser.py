#!/usr/bin/python
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

    if kwargs:
        time = time.replace(**kwargs)

    return time.strftime('%Y-%m-%d %H:%M:%S'), rest


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

    return date, "%s|%s|%s|%s|%s" % (parsed['SRC'], parsed['SPT'], parsed['DST'], parsed['DPT'],
                                     parsed['PROTO'])


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
