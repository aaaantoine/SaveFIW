#!/usr/bin/env python3

import configparser
import re
import urllib.request
import os

from entry import Topic, Entry
import jsonEncode
import parsers

config = configparser.ConfigParser()
config.read('scrape.ini')
c = config['DEFAULT']
start=int(c['start'])
stop=int(c['stop'])
urlTemplate=c['urlTemplate']
encoding=c['encoding']
outputFolder=c['outputFolder']

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
    remainingPages = len([p for p, _ in pages if p > currentPage])
    if remainingPages > 0:
        print("Current page {}, {} additional pages found".format(
            currentPage, remainingPages))
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
    topic.category = parsers.getTopicCategory(text)
    for e in scrapeEntries(topicNum, text=text):
        topic.entries.append(e)
    
    return topic if len(topic.entries) > 0 else None

tokenRE = re.compile("&#[0-9A-F]+;")
def replaceTokens(val):
    return tokenRE.sub("_", val)

def makeFileSafe(val):
    val = replaceTokens(val)
    SAFE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    chars = []
    for char in val:
        chars.append(char if char in SAFE else "_")
    return "".join(chars)

def topicFileName(topic):
    # maxlen chosen for title because topic ID of up to 5 chars, plus hyphen,
    # plus '.json', and the goal is to keep the name under 80 chars.
    maxlen = 68
    return "{}-{}".format(
        topic.topicId,
        makeFileSafe(topic.title)[:maxlen])

def main():
    for n in range(start, stop+1):
        topic = visit(n)
        if topic != None:
            jsonEncode.save(
                topic,
                os.path.join(outputFolder, topicFileName(topic) + ".json"))

if __name__ == '__main__':
    main()
