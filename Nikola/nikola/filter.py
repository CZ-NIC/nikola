import re


def _match_any(address, regexps):
    for regexp in regexps:
        if re.match(regexp, address):
            return True
    return False


def _default_rule_in_data(data):
    # rule = 000...0
    return not data.rsplit("|", 1)[1].strip("0")


def filter_records(
        records, max_count, fw_remote_exclude_regexp, fw_local_exlude_regexp):

    # filter out the exclude regexps
    res = []
    for record in records:
        time, data, count = record
        splitted = data.split("|")
        remote_addr = splitted[1]
        local_addr = splitted[3]
        if not _match_any(remote_addr, fw_remote_exclude_regexp) and \
                not _match_any(local_addr, fw_local_exlude_regexp):
            res.append(record)

    # when records reached the limit
    # throw out rules with 00000000 first
    expandable_count = reduce(
        lambda x, y: x + 1 if _default_rule_in_data(y[1]) else x, res, 0)
    total_count = len(res)
    expandable_allowed = max_count - (total_count - expandable_count)

    res2 = []
    for record in res:
        time, data, count = record
        if _default_rule_in_data(data):
            if expandable_allowed > 0:
                res2.append(record)
                expandable_allowed -= 1
        else:
            res2.append(record)

    # limit strip data to fit max_count
    return res2[:max_count]
