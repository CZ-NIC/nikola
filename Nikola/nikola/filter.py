import re


def _match_any(address, regexps):
    for regexp in regexps:
        if re.match(regexp, address):
            return True
    return False


def filter_records(records, max_count, fw_exclude_regexp):
    res = []
    for record in records:
        time, data, count = record
        remote_addr = data.split("|")[1]
        if not _match_any(remote_addr, fw_exclude_regexp):
            res.append(record)

    return res
