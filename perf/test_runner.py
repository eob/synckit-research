import commands
import os
import re
import sys

LOWERBOUND = 40
UPPERBOUND = 1000
header = ["file", "rate", "total_requests", "concurrent_connections", "request_rate", "reply_rate_avg", "reply_rate_stdev", "reply_samples", "total_size", "200_statuses", "net_io"]

total_pattern = re.compile("Total: connections \S+ requests (\S+) replies \S+")
connection_pattern = re.compile("\S+ ms/conn, <=(\S+) concurrent connections")
request_pattern = re.compile("Request rate: (\S+) req/s")
reply_pattern = re.compile("Reply rate \[replies/s\]: min \S+ avg (\S+) max \S+ stddev (\S+) \((\S+) samples\)")
size_pattern = re.compile("Reply size \[B\]: header \S+ content \S+ footer \S+ \(total (\S+)\)")
status_pattern = re.compile("Reply status: 1xx=\S+ 2xx=(\S+)")
io_pattern = re.compile("Net I/O: (\S+\s+\S+)")

def runtests(test_dir, output_dir):
    files = os.listdir(test_dir)
    statistics_file = open("%s/statistics.csv" % (output_dir), "w")
    rates_file = open("%s/rates.csv" % (output_dir), "w")
    write_statistics_header(statistics_file)
    write_rates_header(rates_file)
    for filename in files:
        file = "%s/%s" % (test_dir, filename)
        (rate, highest_rate, avg_data, lowerbound, upperbound) = reset_iteration()
        while not lowerbound == upperbound:
            runstr = runcommand(rate, file)
            print "Running %s" % (runstr)
            (status, output) = commands.getstatusoutput(runstr)
            if status != 0:
                print "ERROR on %s with rate %d" % (file, rate)
                break
            statistics = extract_statistics(output)
            write_output(filename, rate, output, output_dir)
            write_statistics(statistics_file, statistics, filename, rate)
            (rate, highest_rate, avg_data, lowerbound, upperbound) = \
                update_rate(rate, highest_rate, avg_data, lowerbound, upperbound, statistics)
        write_finalrate(rates_file, filename, highest_rate, rate, avg_data)
    statistics_file.close()
    rates_file.close()

def reset_iteration():
    return (int(((LOWERBOUND + UPPERBOUND)*1.0)/2), 0.0, 0.0, LOWERBOUND, UPPERBOUND)

def runcommand(rate, file):
#Profiling workload:
#    return "httperf --hog --server marcua.csail.mit.edu --port 7000 --rate %d --wsesslog=1000,0,%s" % (rate, file)
# Real workload:
    return "httperf --hog --server marcua.csail.mit.edu --port 7000 --rate %d --wsesslog=10000,0,%s" % (rate, file)
# For testing:
#    return "httperf --hog --server marcua.csail.mit.edu --port 7000 --rate %d --wsesslog=5,0,%s" % (rate, file)

def extract_statistics(output):
    statistics = {}
    extract_data(total_pattern, output, ["total_requests"], statistics)
    extract_data(connection_pattern, output, ["concurrent_connections"], statistics)
    extract_data(request_pattern, output, ["request_rate"], statistics)
    extract_data(reply_pattern, output, ["reply_rate_avg", "reply_rate_stdev", "reply_samples"], statistics)
    extract_data(size_pattern, output, ["total_size"], statistics)
    extract_data(status_pattern, output, ["200_statuses"], statistics)
    extract_data(io_pattern, output, ["net_io"], statistics)
    return statistics

def extract_data(pattern, val, fields, dict):
    m = pattern.search(val)
    if not m == None:
        for i, field in enumerate(fields):
            dict[field] = m.group(i+1)
    else:
        for field in fields:
            dict[field] = "???"

def write_statistics_header(statistics_file):
    output = ",".join(header)
    print output
    statistics_file.write(output+'\n')
    statistics_file.flush()
    sys.stdout.flush()

def write_rates_header(rates_file):
    # Note the addition of strategy and frequency here.
    output = "file,strategy,frequency,highest_rate,attempted_rate,avg_data"
    print output
    rates_file.write(output+'\n')
    rates_file.flush()
    sys.stdout.flush()

def write_output(file, rate, output, output_dir):
    file = open("%s/%s_%d" % (output_dir, file, rate), "w")
    file.write(output)
    file.close()

def write_statistics(statistics_file, statistics, filename, rate):
    statistics["file"] = filename
    statistics["rate"] = str(rate)
    vals = [statistics[field] for field in header]
    output = ",".join(vals)
    print output
    statistics_file.write(output+'\n')
    statistics_file.flush()
    sys.stdout.flush()

def write_finalrate(rates_file, filename, highest_rate, attempted_rate, avg_data):
    # We're going to depend on the file having a predictable
    # name to extract the hosting style and the frequency from
    # the filename
    # i,e,
    # test_freq_12_per_day_traditional.txt
    # test_freq_2_per_day_tokyo.txt
    # test_freq_24_per_day_synckit.txt
    strategy = filename.split("_")[5].split(".")[0]    
    frequency = filename.split("_")[2]
    
    if strategy == "synckit":
        strategy = "Sync Kit"
    elif strategy == "traditional":
        strategy = "Traditional"
    elif strategy == "tokyo":
        strategy = "Flying Templates"
    output = "%s,%s,%s,%f,%d,%f" % (filename, strategy, frequency, highest_rate, attempted_rate, avg_data)
    print output
    rates_file.write(output+'\n')
    rates_file.flush()
    sys.stdout.flush()

def update_rate(rate, highest_rate, avg_data, lowerbound, upperbound, statistics):
    if can_handle(rate, statistics):
        lowerbound = rate + 1
        req_rate = float(statistics["request_rate"])
        if req_rate > highest_rate:
            highest_rate = req_rate
            avg_data = float(statistics["total_size"])
    else:
        upperbound = rate - 1
    if upperbound < lowerbound:
        upperbound = lowerbound
    rate = int(((lowerbound + upperbound)*1.0) / 2)
    return (rate, highest_rate, avg_data, lowerbound, upperbound)

def can_handle(rate, statistics):
    diff = float(statistics["request_rate"]) - rate
    error = (1.0 * diff)/rate
    return (statistics["200_statuses"] == statistics["total_requests"]) \
           and (error > -.02) 

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "arguments: test-file-dir output-dir"
        sys.exit(0)
    runtests(sys.argv[1], sys.argv[2])
