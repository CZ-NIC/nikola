import re
import functools



def _default_rule_in_data(data):
    # rule = 000...0
    return not data.rsplit("|", 1)[1].strip("0")


def filter_records(
        records, max_count, fw_remote_check, fw_local_check):

    # filter out the exclude regexps
    res = []
    for record in records:
        time, data, count = record
        splitted = data.split("|")
        remote_addr = splitted[1]
        local_addr = splitted[3]
        if fw_remote_filter(remote_addr) and fw_local_filter(local_addr):
            res.append(record)

    # when records reached the limit
    # throw out rules with 00000000 first
    expandable_count = functools.reduce(
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
