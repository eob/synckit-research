import commands
import sys
import re

#sizes = [1,10,100,500,1000,1100,1200,1300,1400,1500,1600,1700,1800,1900,2000,5000,7500,10000]
#sizes = [2000,2500,3000,3500,4000,4500,5000,5500,6000,6500,7000,7500,8000,8500,9000,9500,10000]
sizes = [1, 10000, 100000, 1000000]
cmd = 'ab -n 200 http://%s/performancetest/bytes?num_bytes=%d'

if len(sys.argv) != 2:
    print "Run with host:post as an argument e.g. marcua.csail.mit.edu:7000"
    sys.exit(0)

hostport = sys.argv[1]
p = re.compile("Time per request\:\s+(\S+)\s+\[ms\] \(mean, across all concurrent requests\)")

# For measuring latency, send 1 byte
# For measuring bandwidth, send 100k bytes b/c/ this is ~= wikipedia payload size

for size in sizes:
    execline = cmd % (hostport, size)
    print "Running " + execline
#    print "Running '%s'" % (execline)
    output = commands.getoutput(execline)
    m = p.search(output)
    if not m == None:
        print "bytes: %d, milliseconds: %s  ;; EQUALS seconds: %f, bandwidth (b/s): %f" % (
             size, 
             m.group(1), 
             (float(m.group(1)) / 1000.0),
             (size / (float(m.group(1)) / 1000.0))
            )
