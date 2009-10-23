# Site Model

import networkx as nx
from model import *
from random import *
import datetime

VISIT_RATE = 1
VISIT_UNIT = "hours"
NUM_USERS  = 3
PERCENT_NEW = 0.3

FROM_DATE = datetime.datetime(2009, 05, 01)
TO_DATE = datetime.datetime(2009, 05, 02)

BLOG = OnePageBlog()

tick_hash = {VISIT_UNIT : 1}
all_visits = []


# Generate the users
users = []
for i in range(NUM_USERS):
    last_time = None
    if (random() >= PERCENT_NEW):        
        time_delta = expovariate(VISIT_RATE)
        delta_hash = {VISIT_UNIT : time_delta}
        last_time = FROM_DATE - datetime.timedelta(**delta_hash)
        user = User(VISIT_RATE, VISIT_UNIT, last_time)
        user.plan_next_visit()
        users.append(user)
    else:
        last_time = None
        user = User(VISIT_RATE, VISIT_UNIT, last_time)
        delta = random() * (FROM_DATE - TO_DATE).microseconds
        user.next_visit_time = FROM_DATE + datetime.timedelta(microseconds=delta)
        users.append(user)

# Now step forward in time
now = FROM_DATE
while now < TO_DATE:
    # For all users who have a planned visit 
    for user in users:
        if user.next_visit_time <= now:
            all_visits.append(user.perform_next_visit(BLOG))
        
    # Advance the clock    
    now += datetime.timedelta(**tick_hash)
    

# PRINT ALL USERS

#for i in range(len(users)):
#    user = users[i]
#    print "User " + str(i)
#    print "----------------------------"
#    for visit in user.visits:
#        print str(visit)

# PRINT ALL VISITS
for visit in all_visits:
    page = visit.click_trail.path[0]
    if visit.last_time == None:
        print page.url + "template_file.html"
        print "      " + page.url + "data_endpoint.json method=POST contents=query={\"Posts\":{\"now\":\"" + str(visit.this_time) + "\"}}"
        print 
    else:
        print page.url + "data_endpoint.json method=POST contents=query={\"Posts\":{\"max\":\"" + str(visit.last_time) + "\", \"now\":\"" + str(visit.this_time) + "\"}}"
        print
#    print str(visit)