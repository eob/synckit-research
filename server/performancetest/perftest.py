import commands
import sys
import re

sizes = [1,10,100,1000,10000]
cmd = 'ab -c 10 -n 10000 http://%s/performancetest/bytes?num_bytes=%d'

if len(sys.argv) != 2:
    print "Run with host:post as an argument"
    sys.exit(0)

hostport = sys.argv[1]
p = re.compile("Time per request\:\s+(\S+)\s+\[ms\] \(mean, across all concurrent requests\)")

for size in sizes:
    execline = cmd % (hostport, size)
    print "Running '%s'" % (execline)
    output = commands.getoutput(execline)
    m = p.search(output)
    if not m == None:
        print m.group(1)
