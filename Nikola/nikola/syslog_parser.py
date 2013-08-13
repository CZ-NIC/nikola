#!/usr/bin/python
from datetime import datetime

def parse_syslog(path, date_format='%Y-%m-%dT%H:%M:%S', **kwargs):

    def parse_time_datetime(line, format, **kwargs):
        try:
            time = datetime.strptime(line, format)
            rest = ''
        except ValueError, v:
            unmatched_len = len(v.message.partition('unconverted data remains: ')[2])
            time = datetime.strptime(line[:-unmatched_len], format)
            rest = line[len(line)-unmatched_len:]

        if kwargs:
            time = time.replace(**kwargs)

        return time.strftime('%Y-%m-%d %H:%M:%S'), rest

    def parse_line(line, date_format, **kwargs):

        # Cut the date
        date, rest = parse_time_datetime(line, date_format, **kwargs)

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

        return date, "%s|%s|%s|%s|%s" % (parsed['SRC'], parsed['SPT'], parsed['DST'], parsed['DPT'], parsed['PROTO'])

    res = []

    with open(path) as f:
        last = None
        for line in f:
            parsed_line = parse_line(line, date_format, **kwargs)
            if parsed_line:
                date, parsed = parsed_line
                # Same packets in the sequence
                if last and last == parsed:
                    res[-1][2] += 1
                else:
                    res.append([date, parsed, 1])
                    last = parsed

    return res
