#!/usr/bin/python
from datetime import datetime

def parse_syslog(path, date_len=19, date_format='%Y-%m-%dT%H:%M:%S', **kwargs):

    def parse_time_datetime(line, format, **kwargs):
        time = datetime.strptime(line, format)

        time = time.replace(**kwargs)

        return time.strftime('%Y-%m-%d %H:%M:%S')

    def parse_time_simple(line):
        return line[:line.find(' ')].replace('T', ' ')

    def parse_line(line, date_len, date_format, **kwargs):
        splitted = line.split(': ')
        if len(splitted) != 2:
            return None
        date = parse_time_datetime(line[:date_len], date_format, **kwargs)
        parsed = map(lambda x: x.split('='), splitted[1].split(' '))
        parsed = dict(filter(lambda x: len(x) == 2, parsed))
        return date, "%s|%s|%s|%s|%s" % (parsed['SRC'], parsed['SPT'], parsed['DST'], parsed['DPT'], parsed['PROTO'])

    res = []

    with open(path) as f:
        last = None
        for line in f:
            parsed_line = parse_line(line, date_len, date_format, **kwargs)
            if parsed_line:
                date, parsed = parsed_line
                # Same packets in the sequence
                if last and last == parsed:
                    res[-1][2] += 1
                else:
                    res.append([date, parsed, 1])
                    last = parsed

    return res
