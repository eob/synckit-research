#!/usr/bin/env python

import random
import string
import sys

if len(sys.argv) != 2:
    print "Argument: length_of_string"
    sys.exit(-1)

desired_length = int(sys.argv[1])

print "".join([random.choice(string.letters+string.digits) for x in range(desired_length)])
