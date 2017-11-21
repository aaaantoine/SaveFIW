#!/usr/bin/env python3

import configparser
import os
import re
import sys
import urllib.request

from entry import Topic, Entry
import jsonEncode
import parsers

class Config:
    def __init__(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        c = config['DEFAULT']
        self.start = int(c['start'])
        self.stop = int(c['stop'])
        self.urlTemplate = c['urlTemplate']
        self.encoding = c['encoding']
        self.outputFolder = c['outputFolder']

def getPage(url, encoding):
    print("Visiting {}".format(url))
    with urllib.request.urlopen(url) as r:
        return r.read().decode(encoding, 'replace')

def scrapeEntries(topicNum, config, url=None, text=None):
    if text == None:
        if url == None:
            url = config.urlTemplate.format(topicNum)
        text = getPage(url, config.encoding)
    
    for entry in parsers.getEntriesRaw(text):
        yield parsers.buildEntryFromRaw(topicNum, entry)
    currentPage, pages = parsers.detectPages(text)
    remainingPages = len([p for p, _ in pages if p > currentPage])
    if remainingPages > 0:
        print("Current page {}, {} additional pages found".format(
            currentPage, remainingPages))
    for pageNum, pageUrl in pages:
        if pageNum == currentPage + 1:
            for entry in scrapeEntries(topicNum, config, pageUrl):
                yield entry
        
def visit(topicNum, config):
    topic = Topic(topicNum)
    print("Topic {}".format(topicNum))
    url = config.urlTemplate.format(topicNum)
    text = getPage(url, config.encoding)
    topic.title, topic.subtitle = parsers.getTopicTitle(text)
    topic.category = parsers.getTopicCategory(text)
    for e in scrapeEntries(topicNum, config, text=text):
        topic.entries.append(e)
    
    return topic if len(topic.entries) > 0 else None

tokenRE = re.compile("&#[0-9A-F]+;")
def replaceTokens(val):
    return tokenRE.sub("_", val)

def makeFileSafe(val):
    val = replaceTokens(val)
    SAFE = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(c if c in SAFE else "_" for c in val)

def topicFileName(topic):
    # maxlen chosen for title because topic ID of up to 5 chars, plus hyphen,
    # plus '.json', and the goal is to keep the name under 80 chars.
    maxlen = 68
    return "{}-{}".format(
        topic.topicId,
        makeFileSafe(topic.title)[:maxlen])

def main(config):
    for n in range(config.start, config.stop+1):
        topic = visit(n, config)
        if topic != None:
            jsonFile = os.path.join(
                config.outputFolder,
                topicFileName(topic) + ".json")
            jsonEncode.save(topic, jsonFile)

if __name__ == '__main__':
    if "--help" in sys.argv or len(sys.argv) > 2:
        print("Usage: scrape.py [CONFIGFILE.INI]", file=sys.stderr)
        sys.exit(1)
    cfgfile = sys.argv[1] if len(sys.argv) > 1 else 'scrape.ini'
    config = Config(cfgfile)
    main(config)
