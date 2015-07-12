#!/usr/bin/python

import io
import os
import sys
import time
import random

DIRNAME = os.path.dirname(__file__)
DATA_ROOT_PATH = os.path.join(DIRNAME, "data")


if __name__ == "__main__":
    to_write_fmt = u"%f %f %f\n"
    try:
        time.sleep(3)
        while True:
            with io.open(os.path.join(DATA_ROOT_PATH, "probe1"), "a") as w_f:
                to_write = to_write_fmt % (
                    time.time(), random.random(), random.random())
                w_f.write(to_write)
                time.sleep(0.5)
    except KeyboardInterrupt:
        sys.exit(2)
