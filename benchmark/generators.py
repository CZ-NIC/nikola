import random
import os
from datetime import datetime

class ConfigError(Exception):
    pass


# open moref files at once
class FilesOpener(object):
    def __init__(self, paths):
        self._paths = paths

    def __enter__(self):
        self._files = [open(path, 'w') for path in self._paths]
        for f in self._files:
            f.write("batch_id,time_delta,count\n")
        return self._files

    def __exit__(self, exc_type, exc_value, traceback):
        for f in self._files:
            f.close()


class Generator(object):
    MANDATORY = {}

    def __init__(self, **kwargs):
        if not self.MANDATORY.issubset(set(kwargs.keys())):
            raise ValueError(
                "config is missing mandatory fields: %s"
                % (",".join(self.MANDATORY - set(kwargs.keys())))
            )

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.validate_conf()

        self.load_defaults()

    def __getattr__(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            return None

    def load_defaults(self):
        raise NotImplemented()

    def validate_conf(self):
        raise NotImplemented()

    def generate(self):
        raise NotImplemented()

    def store_results(self):
        raise NotImplemented()

    @staticmethod
    def separate_counts_into_groups(
            group_count, element_count, min_group_size=0, max_elements=None):
        # get the length of the smallest binary notation
        window_size = len("{0:b}".format(group_count))
        # window_size / 2 < group_number <= window_size
        assigned = min_group_size * group_count
        res = {e: min_group_size for e in range(group_count)}
        while assigned < element_count:
            selected = random.getrandbits(window_size)
            if selected < group_count and (not max_elements or res[selected] < max_elements):
                res[selected] += 1
                assigned += 1
        return res


class RequestGenerator(Generator):
    MANDATORY = {
        'output_dir', 'clients', 'count'
    }

    def load_defaults(self):
        if "batch_count_max" not in self.__dict__:
            self.batch_count_max = self.count

        if "batch_count_min" not in self.__dict__:
            self.batch_count_min = self.count / self.batch_size_max + 1  \
                if "batch_size_max" in self.__dict__ else 1

    def validate_conf(self):

        if self.batch_count_min and self.batch_count_max:
            if self.batch_count_min > self.batch_count_max:
                raise ConfigError(
                    "batch_count_min > batch_count_max # (%%d > %d)" % (
                        self.batch_count_min, self.batch_count_max
                    )
                )

        if self.batch_size_max and self.batch_count_min:
            if self.batch_count_min * self.batch_size_max < self.count:
                raise ConfigError(
                    "batch_count_min * batch_size_max < count # (%d * %d < %d)" % (
                        self.batch_count_min, self.batch_size_max, self.count
                    )
                )

    @staticmethod
    def gen_batch_id():
        return "%s-%s-%s-%s" % (
            "%04x" % random.getrandbits(16),
            "%04x" % random.getrandbits(16),
            "%04x" % random.getrandbits(16),
            "%04x" % random.getrandbits(16),
        )

    def generate(self):
        batch_count = random.randrange(self.batch_count_min, self.batch_count_max + 1)
        # Generete n groups with at least one element
        batches = self.separate_counts_into_groups(
            batch_count, self.count, self.batch_size_min, self.batch_size_max
        )
        self._data = []
        for k, v in batches.items():
            self._data.append({
                "batch_id": self.gen_batch_id(),
                "client": random.randrange(self.clients),
                "count": v,
                "time_delta": random.randrange(self.within),
            })

    def store_results(self):

        if self.debug:
            for line in self._data:
                print line
            print "Batches generated: %d" % len(self._data)

        time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        paths = [
            os.path.join(self.output_dir, "%s_%s_%04d.csv" % (self.name, time, i))
            for i in range(self.clients)
        ]

        with FilesOpener(paths) as files:
            for line in self._data:
                files[line['client']].write(
                    ",".join(map(str, [line['batch_id'], line['time_delta'], line['count']])) +
                    "\n"
                )


class PacketGenerator(Generator):
    MANDATORY = {
        'count', 'output_file', 'wan_eth'
    }

    @staticmethod
    def gen_ipv4():
        r = random.getrandbits(32)
        return ".".join(["%d" % ((r >> i) & 0xFF) for i in reversed(range(0, 32, 8))])

    @staticmethod
    def gen_ipv6():
        r = random.getrandbits(128)
        return ":".join(["%04x" % ((r >> i) & 0xFFFF) for i in reversed(range(0, 128, 16))])

    def load_defaults(self):
        self.protocols = ['TCP', 'UDP'] if "protocols" not in self.__dict__ else self.protocols
        self.tcp_flags = [] if "tcp_flags" not in self.__dict__ else self.tcp_flags
        self.ports = None if "ports" not in self.__dict__ else self.ports
        self.ips = None if "ips" not in self.__dict__ else self.ips
        self.ip_type = [4, 6] if "ip_type" not in self.__dict__ else self.ip_type
        self.rule_ids = ["0FA7E000"] if "rule_ids" not in self.__dict__ else self.rule_ids

    def validate_conf(self):
        pass

    def generate(self):
        """
        Generate similar syslog output which should get parsed by nikola

        2016-02-12T09:44:18+01:00 turris-00000000: IN=ethX OUT=ethX SRC=0.0.0.0 DST=0.0.0.0
        PROTO=UDP SPT=80 DPT=80
        """
        time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')  # Time will be replaced later

        self._data = []
        for _ in range(self.count):
            tcp_flags = random.sample(self.tcp_flags, random.randrange(len(self.tcp_flags) + 1)) \
                if self.tcp_flags else ""
            tcp_flags = " ".join(tcp_flags)

            dev_in, dev_out = (self.wan_eth, "") if random.getrandbits(1) else ("", self.wan_eth)
            rule_id = random.choice(self.rule_ids)
            proto = random.choice(self.protocols)

            if random.choice(self.ip_type) == 6:
                ip_src, ip_dst = self.gen_ipv6(), self.gen_ipv6()
            else:
                ip_src, ip_dst = self.gen_ipv4(), self.gen_ipv4()

            port_dst = random.choice(self.ports) if self.ports else random.getrandbits(16)
            port_src = random.choice(self.ports) if self.ports else random.getrandbits(16)

            self._data.append(
                "%s turris-%s: IN=%s OUT=%s SRC=%s DST=%s SPT=%d DPT=%d PROTO=%s %s" % (
                    time, rule_id, dev_in, dev_out, ip_src, ip_dst, port_src, port_dst, proto,
                    tcp_flags
                )
            )

    def store_results(self):
        with open(self.output_file, 'w') as f:
            f.writelines("\n".join(self._data))
