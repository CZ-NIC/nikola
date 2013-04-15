#!/usr/bin/python

def parse_syslog(path):

    def parse_line(line):
        res = {}
        splitted = line.split('iptables: ')
        if len(splitted) != 2:
            return None
        res[u'time'] = splitted[0][:splitted[0].find(' ')].replace('T', ' ')
        parsed = map(lambda x: x.split('='), splitted[1].split(' '))
        parsed = dict(filter(lambda x: len(x) == 2, parsed))
        res[u'src_port'] = parsed['SPT']
        res[u'dst_port'] = parsed['DPT']
        res[u'src_addr'] = parsed['SRC']
        res[u'dst_addr'] = parsed['DST']
        return res

    res = []

    with open(path) as f:
        for line in f.readlines():
            parsed = parse_line(line)
            if parsed:
                res.append(parsed)
    
    return res
