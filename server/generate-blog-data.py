from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import transaction
from server.blog.models import *

import datetime
import random
import string
import sys
import traceback

NUM_AUTHORS = 10
START_DATE = datetime.datetime(2009, 05, 01)
ENTRIES_PER_MINUTE = .06666666 # 4 / hour
NUM_DAYS = 30
ENTRY_LENGTH_MU = 1024
ENTRY_LENGTH_SIGMA = 1024
TITLE_LENGTH_MU = 50
TITLE_LENGTH_SIGMA = 25

@transaction.commit_manually
def generate_data():
    try:
        authors = generate_authors()
        generate_entries(authors)
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,
                                  file=sys.stdout)
        transaction.rollback()
    else:
        transaction.commit()

def generate_authors():
    for i in range(0, NUM_AUTHORS):
        name = "author%d" % (i)
        author = Author(name = name)
        author.save()
    return [author for author in Author.objects.all()]

def generate_entries(authors):
    date = START_DATE
    end_date = date + datetime.timedelta(days = NUM_DAYS)
    itercount = 0
    while date < end_date:
        minute_delta = random.expovariate(ENTRIES_PER_MINUTE)
        date += datetime.timedelta(minutes = minute_delta)
        entry = Entry()
        entry.author = random.sample(authors, 1)[0]
        entry.title = generate_string(\
            random.gauss(TITLE_LENGTH_MU, TITLE_LENGTH_SIGMA))
        entry.contents = generate_string(\
            random.gauss(ENTRY_LENGTH_MU, ENTRY_LENGTH_SIGMA))
        entry.date = date
        entry.save()
        if (itercount % 1000) == 0:
            print "Making entry for %s" % (str(date))
        itercount += 1

def generate_string(length):
    int_length = int(length)
    return "".join([random.choice(string.ascii_lowercase) for i in xrange(int_length)])

if __name__ == "__main__":
    generate_data()
