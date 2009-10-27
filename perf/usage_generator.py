# Site Model

import networkx as nx
from model import *
from random import *
import datetime
import pickle 
import datetime
import os

VISIT_RATE = 4
VISIT_UNIT = "days"
NUM_USERS  = 20
PERCENT_NEW = 0.3

FROM_DATE = datetime.datetime(2010, 05, 01)
TO_DATE = datetime.datetime(2010, 05, 07)

BLOG = OnePageBlog('')

# http://marcua.csail.mit.edu:7000/blog/entries
TEMPLATE_ENNDPOINT = "/static/tokyo.tmpl"
DATA_ENNDPOINT = "/blog/entries"
PRERENDERED_ENNDPOINT = "/blog/traditional"

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
    elif strategy == 'traditional':
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
            strings.append("%s%s?%s" % (page.url, PRERENDERED_ENNDPOINT, query_for_visit(visit, strategy)))
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
def ensure_directory(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def write_test_files(directory_name, test_name, num_users, percent_new, num_visits, in_period):
    ensure_directory(directory_name)
    
    users = create_users(num_users, percent_new, num_visits, in_period)    
    visits = run_test(BLOG,users)
    
    for strategy in ('synckit', 'tokyo', 'traditional'):
        urls = []
        for visit in visits:
            urls.extend(url_strings_for_visit(visit, strategy))
            urls.append("")
        comments = "# Test Name: %s\n# Strategy: %s\n# Number Users: %s\n# Percent New: %s\n# Number Visits: %s / %s\n" % (test_name, strategy, str(num_users), str(percent_new), str(num_visits), str(in_period))
        write_url_file(urls, "%s/%s_%s.txt" % (directory_name, test_name, strategy), header=comments)

now = datetime.datetime.now()
dirname = now.strftime("%Y-%m-%d.%H:%M:%S")

write_test_files(dirname, "test_warmup_allnew", NUM_USERS, 1.0, VISIT_RATE, VISIT_UNIT)
write_test_files(dirname, "test_warmup_nonew", NUM_USERS, 0.0, VISIT_RATE, VISIT_UNIT)

write_test_files(dirname, "test_numusers_5", 5, 0.5, VISIT_RATE, VISIT_UNIT)
write_test_files(dirname, "test_numusers_10", 10, 0.5, VISIT_RATE, VISIT_UNIT)
write_test_files(dirname, "test_numusers_100", 100, 0.5, VISIT_RATE, VISIT_UNIT)

write_test_files(dirname, "test_freq_24_per_day", 20, 1.0, 24, "days")
write_test_files(dirname, "test_freq_12_per_day", 20, 1.0, 20, "days")
write_test_files(dirname, "test_freq_12_per_day", 20, 1.0, 16, "days")
write_test_files(dirname, "test_freq_12_per_day", 20, 1.0, 12, "days")
write_test_files(dirname, "test_freq_6_per_day", 20, 1.0, 8, "days")
write_test_files(dirname, "test_freq_6_per_day", 20, 1.0, 7, "days")
write_test_files(dirname, "test_freq_6_per_day", 20, 1.0, 6, "days")
write_test_files(dirname, "test_freq_5_per_day", 20, 1.0, 5, "days")
write_test_files(dirname, "test_freq_4_per_day", 20, 1.0, 4, "days")
write_test_files(dirname, "test_freq_3_per_day", 20, 1.0, 3, "days")
write_test_files(dirname, "test_freq_2_per_day", 20, 1.0, 2, "days")
write_test_files(dirname, "test_freq_1_per_day", 20, 1.0, 1, "days")
write_test_files(dirname, "test_freq_0.5_per_day", 20, 1.0, 0.5, "days")
write_test_files(dirname, "test_freq_0.25_per_day", 20, 1.0, 0.25, "days")


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
