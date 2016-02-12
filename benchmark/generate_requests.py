#!/usr/bin/python

import sys
import os
import json

from generators import RequestGenerator


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: %s config_file" % sys.argv[0])
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        conf = json.load(f)

    generator = RequestGenerator(
        name=".".join(os.path.splitext(os.path.basename(sys.argv[1]))[:-1]), **conf)

    generator.generate()
    generator.store_results()
