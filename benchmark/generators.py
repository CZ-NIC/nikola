import random
import os
from datetime import datetime

class ConfigError(Exception):
    pass


# open files
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


class RequestGenerator(object):
    MANDATORY = {
        'output_dir', 'clients', 'count'
    }

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
                    ",".join(map(str, [line['batch_id'], line['time_delta'], line['count']])) + "\n"
                )
