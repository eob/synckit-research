import random
import string

def generate_string(length):
    int_length = int(length)
    return "".join([random.choice(string.ascii_lowercase) for i in xrange(int_length)])
