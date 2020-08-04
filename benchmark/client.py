#!/usr/bin/python

import base64
import json
import optparse
import os
import time
import zlib

from datetime import datetime

from sentinel_nikola.syslog_parser import parse_syslog
from generators import ConfigError, PacketGenerator
from rpc_wrapper import WrappedServer

class ServerError(Exception):
    pass

def check_reply(reply):
    if 'error' in reply:
        raise ServerError("error recieved from the server - %s" % str(reply))

def check_config(conf):
    def check_field(name):
        if name not in conf:
            raise ConfigError("missing mandatory field '%s'" % name)
        return True
    return check_field

def _get_batch_file(batch_dir, client_id, batch_id):
    return os.path.join(batch_dir, "%s_%s" % (client_id, batch_id))


def send_data(batch_id, client_id, url, serial, slot_id, key, batch_dir, debug=False, **kwargs):
    batch_path = _get_batch_file(conf['batch_dir'], conf['client_id'], batch_id)
    data = parse_syslog(batch_path, "faketh")

    #  update time
    new_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    for record in data:
        record[0] = new_time
        if debug:
            print record

    # init connection
    server = WrappedServer(url, serial, key, slot_id)
    server.connect_when_not_connected()
    check_reply(server.init_session())

    compressed = base64.b64encode(zlib.compress(json.dumps(data), 1))
    check_reply(server.api_turris_cz.firewall.store_logs(compressed))

    if debug:
        print("%d packets were sent to the server" % len(data))

    # close connection
    server.transport.close()


def process_requests(conf):
    """
    processes requests and returns a list [(timedelta, batch_id), ...]
    """
    with open(options.requests, 'r') as f:
        # skip the header
        f.readline()

        line = f.readline()
        res = []
        while line:
            line.strip('\n')
            batch_id, timedelta, count = line.split(",")
            timedelta, count = int(timedelta), int(count)
            res.append((timedelta, batch_id))

            # generate the data if required
            path = _get_batch_file(conf["batch_dir"], conf['client_id'], batch_id)
            if not os.path.isfile(path):
                generator = PacketGenerator(
                    count=count, output_file=path, wan_eth="faketh", **conf["packets"])
                generator.generate()
                generator.store_results()

            line = f.readline()

    return res


if __name__ == "__main__":

    # Parse the command line options
    optparser = optparse.OptionParser(
        "usage: %prog --config CONFIG.JSON --requests DATA.CSV [--start-time TIME]\n"
    )

    optparser.add_option(
        "-s", "--start-time", dest='start_time', type='string', default=None,
        help='specify start time (format YYYY-MM-DD_hh:mm:ss)'
    )

    optparser.add_option(
        "-c", "--config", dest='config', type='string', default=None,
        help='path to client the cofiguration file'
    )

    optparser.add_option(
        "-r", "--requests", dest='requests', type='string', default=None,
        help='path to a requests file (csv format)'
    )

    (options, args) = optparser.parse_args()
    if len(args) != 0:
        optparser.error("unmatched argument")

    if not options.config or not options.requests:
        optparser.error("missing a mandatory argument")

    with open(options.config, 'r') as f:
        conf = json.load(f)

    map(check_config(conf), ["url", "serial", "slot_id", "key", "client_id", "batch_dir"])

    schedule = process_requests(conf)
    schedule.sort(key=lambda x: x[0])

    if options.start_time:
        # read start_time
        start_time = datetime.strptime(options.start_time, "%Y-%m-%d_%H:%M:%S")

        # wait start_time
        if start_time < datetime.now():
            raise ValueError("start_time should be in the future")
        time.sleep((start_time - datetime.now()).total_seconds())

    start_seconds = time.time()
    # wait till for time deltas
    for i in range(len(schedule)):
        delta, batch_id = schedule[i]
        sleep_time = start_seconds + delta - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

        send_data(batch_id, **conf)
