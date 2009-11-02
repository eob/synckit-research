import feedparser
import urllib
import libxml2dom
import datetime
import numpy

feeds = (
         {
            "name":"Tech Crunch",
            "url":"http://feedproxy.google.com/TechCrunch",
            "class":"entry",
            "entries":[]
         },
         {
            "name":"ReadWriteWeb",
            "url":"http://feeds.feedburner.com/readwriteweb",
            "class":"asset-content",
            "entries":[]
         },
         {
            "name":"Slashdot",
            "url":"http://rss.slashdot.org/Slashdot/slashdot",
            "class":"body",
            "entries":[]
         },
         {
            "name":"Consumerist",
            "url":"http://consumerist.com/index.xml",
            "class":"entry",
            "entries":[]
         },
         {
            "name":"Politico",
            "url":"http://www.politico.com/rss/politicopicks.xml",
            "class":"story-wrapper",
            "entries":[]
         },         
         {
            "name":"Gizmodo",
            "url":"http://feeds.gawker.com/gizmodo/full",
            "class":"entry",
            "entries":[]
         },         
         {
            "name":"Engadget",
            "url":"http://www.engadget.com/rss.xml",
            "class":"post",
            "entries":[]
         }
)

for (site) in feeds:
    feed = feedparser.parse(site['url'])
    for entry in feed.entries:
        f = urllib.urlopen(entry.link)
        content = f.read()
        f.close()
        doc = libxml2dom.parseString(content, html=1)
        for div in doc.getElementsByTagName("div"):
            # if it has the right class
            if div.getAttribute("class") == site['class']:
                site["entries"].append({"date":datetime.datetime(*entry.date_parsed[:6]), "content":div.toString()})


    differences = []
    lengths = []
    last_post = None
    
    for entry in site["entries"]:
        print entry.keys()

        lengths.append(len(entry["content"]))
        if (last_post != None):
            differences.append((last_post - entry["date"]).seconds)
        last_post = entry["date"]
    
    print site["name"]
    print "-----------------------------"
    print "Average len of article (kb): %f" % (numpy.average(lengths)/1024.0)
    print "Standard Dev len of article: %f" % (numpy.std(lengths)/1024.0)
    print "Average Delta (minutes): %i" % (numpy.average(differences)/60.0)
    print "Standard Dev: %i" % (numpy.std(differences)/60.0)
    print "Number Posts: %i" % (len(differences) + 1)
    print
    print
