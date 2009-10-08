from django.core.management import setup_environ
import settings
setup_environ(settings)

from django.db import transaction
from emailstubs.models import *
import datetime
import sys
import traceback

# Creates 1000 email messages to fill a database
@transaction.commit_manually
def createmessages():
    now_time = datetime.datetime.now()
    for i in range(1000):
        i += 1
        m = Message()
        m.from_email = "john@doe.com"
        m.to_email = "jake@bob.com"
        m.subject = "hi there! %d" % (i)
        m.contents = "these are the contents of message %d" % (i)
        m.date = now_time + i*datetime.timedelta(minutes = 5)
        m.save()
    transaction.commit()

@transaction.commit_manually
def createtags():
    try: 
        for m in Message.objects.all():
            tag = Tag()
            tag.save()
            tag.message_set.add(m)
            tag.text = "tag %d" % (tag.id)
            tag.save()
            tag = Tag()
            tag.save()
            tag.message_set.add(m)
            tag.text = "tag %d" % (tag.id)
            tag.save()
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,
                                  file=sys.stdout)
        transaction.rollback()
    else:
        transaction.commit()
    

if __name__ == '__main__':
    createmessages()
    createtags()
