from django.core.management import setup_environ
import settings

setup_environ(settings)

from django.db import transaction
from server.wiki.models import *
from text_tools import generate_string

import datetime
import random
import sys
import text_tools
import traceback

# wiki
# link structure---http://users.on.net/~henry/home/wikipedia.htm
TODAY = datetime.datetime(2009, 05, 01)
DAYMATH_MU = 0
DAYMATH_SIGMA = 10
# page size---http://mituzas.lt/2007/12/10/wikipedia-page-counters/ 
#PAGE_LENGTH_MU = 46007.655379
#PAGE_LENGTH_SIGMA = 103839.904207
# better page size data: http://stats.wikimedia.org/EN/TablesArticlesBytesPerArticle.htm
PAGE_LENGTH_MU = 3276
PAGE_LENGTH_SIGMA = 100
TITLE_LENGTH_MU = 21.655587
TITLE_LENGTH_SIGMA = 12.872105
NUM_PAGES = 10000
NUM_LINKS_PER_PAGE = 23
START_DIVISOR = 10 # start page 1 at probability 1/START_DIVISOR

@transaction.commit_manually
def generate_data():
    try:
        print "Building pages"
        page_probs = generate_pages()
#        print "Adding links"
#        build_links(page_probs)
    except:
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        traceback.print_exception(exceptionType, exceptionValue, exceptionTraceback,
                                  file=sys.stdout)
        transaction.rollback()
    else:
        transaction.commit()

def generate_pages():
    today = datetime.datetime.today()
    pageids = []
    probs = [1.0/i for i in xrange(START_DIVISOR,NUM_PAGES+START_DIVISOR)]
    sumprob = sum(probs)
    probs = [prob/sumprob for prob in probs]
    for i in xrange(1, NUM_PAGES+1):
        #delta = datetime.timedelta(days = random.gauss(DAYMATH_MU, DAYMATH_SIGMA))
        #date = today + delta
        #title = generate_string(\
        #    random.gauss(TITLE_LENGTH_MU, TITLE_LENGTH_SIGMA))
        contents = generate_string(\
            random.gauss(PAGE_LENGTH_MU, PAGE_LENGTH_SIGMA))
        prob = probs[i-1]
        #page = Page(title=title, contents=contents, date=date, access_probability=prob)
        page = Page.objects.get(id=i)
        page.contents = contents
        page.save()
        pageids.append((i, prob))
    return pageids

def build_links(page_probs):
    links_made = 0
    links_to_make = NUM_PAGES*NUM_LINKS_PER_PAGE
    while links_made < links_to_make:
        from_id = random.randint(1,NUM_PAGES)
        to_id = rand_node(page_probs)
        if Page.objects.filter(id = from_id).filter(outlinks__id = to_id).count() == 0:
            from_page = Page.objects.filter(id = from_id).defer('contents', 'title')[0]
            to_page = Page.objects.filter(id = to_id).defer('contents', 'title')[0]
            from_page.outlinks.add(to_page)
            from_page.save()
            links_made += 1

def rand_node(page_probs):
    rand = random.random()
    sum = 0
    for pageid, prob in page_probs:
        sum += prob
        if rand < sum:
            return pageid

if __name__ == "__main__":
    generate_data()
