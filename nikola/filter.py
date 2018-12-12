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
        if fw_remote_check(record["ip"]) and fw_local_check(record["local_ip"]):
            res.append(record)

    return res[:max_count]
