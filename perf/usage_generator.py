# Site Model

import networkx as nx
from model import *
from random import *
import datetime
import pickle 

VISIT_RATE = 2
VISIT_UNIT = "hours"
NUM_USERS  = 20
PERCENT_NEW = 0.3

FROM_DATE = datetime.datetime(2010, 05, 01)
TO_DATE = datetime.datetime(2010, 05, 02)

BLOG = OnePageBlog('')

# http://marcua.csail.mit.edu:7000/blog/entries
TEMPLATE_ENNDPOINT = "/blog/entries"
DATA_ENNDPOINT = "/blog/entries"
PRERENDERED_ENNDPOINT = "/prerendered"

tick_hash = {VISIT_UNIT : 1}

def create_users(number, percent_new, visit_rate, visit_unit):
    # Generate the users
    users = []
    for i in range(number):
        last_time = None
        if (random() >= percent_new):        
            time_delta = expovariate(visit_rate)
            delta_hash = {visit_unit : time_delta}
            last_time = FROM_DATE - datetime.timedelta(**delta_hash)
            user = User(visit_rate, visit_unit, last_time)
            user.plan_next_visit()
            users.append(user)
        else:
            last_time = None
            user = User(visit_rate, visit_unit, last_time)
            delta = random() * (FROM_DATE - TO_DATE).microseconds
            user.next_visit_time = FROM_DATE + datetime.timedelta(microseconds=delta)
            users.append(user)
    return users

def saveToFile(obj, filename):
    output = open(filename, 'wb')
    pickle.dump(obj, output)
    output.close()

def loadFromFile(filename):
    input = open(filename, 'rb')
    data = pickle.load(input)
    input.close()
    return data

def run_test(site, users):
    all_visits = []
    # Now step forward in time
    now = FROM_DATE
    while now < TO_DATE:
        # For all users who have a planned visit 
        for user in users:
            if user.next_visit_time <= now:
                all_visits.append(user.perform_next_visit(BLOG))
        # Advance the clock    
        now += datetime.timedelta(**tick_hash)
    return all_visits

def query_for_visit(visit, strategy):
    if strategy == 'tokyo':
        return 'queries={"Posts":{"now":"%s"}}' % (str(visit.this_time))
    else:
        if visit.last_time == None:
            return 'queries={"Posts":{"now":"%s"}}' % (str(visit.this_time))
        else:
            return 'queries={"Posts":{"now":"%s", "max":"%s"}}' % (str(visit.this_time), str(visit.last_time))        

def url_strings_for_visit(visit, strategy):
    page = visit.click_trail.path[0]
    strings = []
    if strategy == 'traditional':
        strings.append(page.url + PRERENDERED_ENNDPOINT)
    else:        
        if visit.last_time == None:
            strings.append(page.url + TEMPLATE_ENNDPOINT)
            strings.append("      %s%s method=POST contents='%s'" % (page.url, DATA_ENNDPOINT, query_for_visit(visit, strategy)))
        else:
            strings.append("%s%s method=POST contents='%s'" % (page.url, DATA_ENNDPOINT, query_for_visit(visit, strategy)))
    return strings

def write_url_file(urls, filename, header=""):
    output = open(filename, 'wb')
    if len(header) > 0:
        output.write(header)
    for url in urls:
        output.write(url + '\n')
    output.close()
            
# --------------------------------------------------------------------------------                      
# | The Test
# --------------------------------------------------------------------------------                      

def write_test_files(test_name, num_users, percent_new, num_visits, in_period):
    users = create_users(num_users, percent_new, num_visits, in_period)    
    visits = run_test(BLOG,users)
    
    for strategy in ('synckit', 'tokyo', 'traditional'):
        urls = []
        for visit in visits:
            urls.extend(url_strings_for_visit(visit, strategy))
            urls.append("")
        comments = "# Test Name: %s\n# Strategy: %s\n# Number Users: %s\n# Percent New: %s\n# Number Visits: %s / %s\n" % (test_name, strategy, str(num_users), str(percent_new), str(num_visits), str(in_period))
        write_url_file(urls, "%s_%s.txt" % (test_name, strategy), header=comments)


write_test_files("test", NUM_USERS, PERCENT_NEW, VISIT_RATE, VISIT_UNIT)
# PRINT ALL USERS

#for i in range(len(users)):
#    user = users[i]
#    print "User " + str(i)
#    print "----------------------------"
#    for visit in user.visits:
#        print str(visit)

# PRINT ALL VISITS
#for visit in all_visits:
#    page = visit.click_trail.path[0]
#    if visit.last_time == None:
#        print page.url + "template_file.html"
#        print "      " + page.url + "data_endpoint.json method=POST contents=queries={\"Posts\":{\"now\":\"" + str(visit.this_time) + "\"}}"
#        print 
#    else:
#        print page.url + "data_endpoint.json method=POST contents=queries={\"Posts\":{\"max\":\"" + str(visit.last_time) + "\", \"now\":\"" + str(visit.this_time) + "\"}}"
#        print
#    print str(visit)
