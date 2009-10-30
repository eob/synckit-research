import commands
import os
import re
import sys

LOWERBOUND = 10
UPPERBOUND = 200
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
    write_header(statistics_file)
    for filename in files:
        file = "%s/%s" % (test_dir, filename)
        (rate, lowerbound, upperbound) = reset_iteration()
        while not int(lowerbound) == int(upperbound):
            runstr = runcommand(rate, file)
            print "Running %s" % (runstr)
            (status, output) = commands.getstatusoutput(runstr)
            if status != 0:
                print "ERROR on %s with rate %d" % (file, rate)
                break
            statistics = extract_statistics(output)
            write_output(filename, rate, output, output_dir)
            write_statistics(statistics_file, statistics, filename, rate)
            (rate, lowerbound, upperbound) = update_rate(rate, lowerbound, upperbound, statistics)
        print "Optimal rate for %s is %d" % (filename, rate)
    statistics_file.close()

def reset_iteration():
    return (int(((LOWERBOUND + UPPERBOUND)*1.0)/2), LOWERBOUND, UPPERBOUND)

def runcommand(rate, file):
    return "httperf --hog --server marcua.csail.mit.edu --port 7000 --rate %d --wsesslog=10000,0,%s" % (rate, file)
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

def write_header(statistics_file):
    output = ",".join(header)
    print output
    statistics_file.write(output+'\n')
    statistics_file.flush()
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

def update_rate(rate, lowerbound, upperbound, statistics):
    if statistics["200_statuses"] == statistics["total_requests"]:
        lowerbound = rate + 1
    else:
        upperbound = rate - 1
    rate = int(((lowerbound + upperbound)*1.0) / 2)
    return (rate, lowerbound, upperbound)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "arguments: test-file-dir output-dir"
        sys.exit(0)
    runtests(sys.argv[1], sys.argv[2])
