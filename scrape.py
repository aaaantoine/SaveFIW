#!/usr/bin/env python3

import urllib.request
import os

from entry import Topic, Entry
import jsonEncode
import parsers

start=1
stop=30000
urlTemplate='http://z4.invisionfree.com/FIWII/index.php?showtopic={}'
encoding='cp1252'
outputFolder='data'

def getPage(url):
    print("Visiting {}".format(url))
    with urllib.request.urlopen(url) as r:
        return r.read().decode(encoding, 'replace')

def scrapeEntries(topicNum, url=None, text=None):
    if text == None:
        if url == None:
            url = urlTemplate.format(topicNum)
        text = getPage(url)
    
    for entry in parsers.getEntriesRaw(text):
        yield parsers.buildEntryFromRaw(topicNum, entry)
    currentPage, pages = parsers.detectPages(text)
    print()
    print("Current page {}, {} additional pages found".format(
        currentPage, len([p for p, _ in pages if p > currentPage])))
    for pageNum, pageUrl in pages:
        if pageNum == currentPage + 1:
            for entry in scrapeEntries(topicNum, pageUrl):
                yield entry
        
def visit(topicNum):
    topic = Topic(topicNum)
    print("Topic {}".format(topicNum))
    url = urlTemplate.format(topicNum)
    text = getPage(url)
    topic.title, topic.subtitle = parsers.getTopicTitle(text)
    for e in scrapeEntries(topicNum, text=text):
        topic.entries.append(e)
    
    return topic if len(topic.entries) > 0 else None

def main():
    for n in range(start, stop+1):
        topic = visit(n)
        if topic != None:
            jsonEncode.save(
                topic,
                os.path.join(outputFolder, str(n) + ".json")) 

if __name__ == '__main__':
    main()
