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
        res = {}
        splitted = line.split('iptables: ')
        if len(splitted) != 2:
            return None
        #res[u'time'] = parse_time_simple(splitted[0])
        res[u'time'] = parse_time_datetime(line[:date_len], date_format, **kwargs)
        parsed = map(lambda x: x.split('='), splitted[1].split(' '))
        parsed = dict(filter(lambda x: len(x) == 2, parsed))
        res[u'src_port'] = parsed['SPT']
        res[u'dst_port'] = parsed['DPT']
        res[u'src_addr'] = parsed['SRC']
        res[u'dst_addr'] = parsed['DST']
        res[u'protocol'] = parsed['PROTO']
        return res

    res = []

    with open(path) as f:
        for line in f:
            parsed = parse_line(line, date_len, date_format, **kwargs)
            if parsed:
                res.append(parsed)
    
    return res
