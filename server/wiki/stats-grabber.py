import numpy
import sys

title_lengths = []
article_lengths = []
for line in open(sys.argv[1]):
    parts = line.split()
    if len(parts) != 4:
        print "'%s' is broken!" % (line)
        continue
    title_lengths.append(len(parts[1]))
    article_lengths.append(int(parts[3]))

article_lengths.sort()
article_lengths = article_lengths[:int(len(article_lengths)*.99)]


print "title: avg=%f stdev=%f" % (numpy.average(title_lengths), numpy.std(title_lengths))
print "article: avg=%f stdev=%f" % (numpy.average(article_lengths), numpy.std(article_lengths))
    
