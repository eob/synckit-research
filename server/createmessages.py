from django.core.management import setup_environ
import settings
setup_environ(settings)
from emailstubs.models import *
import datetime

# Creates 1000 email messages to fill a database

if __name__ == '__main__':
    now_time = datetime.datetime.now()
    for i in range(1000):
        m = Message()
        m.from_email = "john@doe.com"
        m.to_email = "jake@bob.com"
        m.subject = "hi there! %d" % (i)
        m.contents = "fwap! %d" % (i)
        m.date = now_time - i*datetime.timedelta(minutes = 5)
        m.save()

