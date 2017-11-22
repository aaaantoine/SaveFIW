#!/usr/bin/env python3

import os
import re
import requests
import sys

from config import Config
from entry import Topic, Entry
import jsonEncode
import login
import parsers

def getPage(url, cookies):
    print("Visiting {}".format(url))
    r = requests.get(url, cookies=cookies)
    return r.text

def scrapeEntries(topicNum, config, cookies, url=None, text=None):
    if text == None:
        if url == None:
            url = config.urlTemplate.format(topicNum)
        text = getPage(url, cookies)
    
    for entry in parsers.getEntriesRaw(text):
        yield parsers.buildEntryFromRaw(topicNum, entry)
    currentPage, pages = parsers.detectPages(text)
    remainingPages = len([p for p, _ in pages if p > currentPage])
    if remainingPages > 0:
        print("Current page {}, {} additional pages found".format(
            currentPage, remainingPages))
    for pageNum, pageUrl in pages:
        if pageNum == currentPage + 1:
            for entry in scrapeEntries(topicNum, config, cookies, pageUrl):
                yield entry
        
def visit(topicNum, config, cookies):
    topic = Topic(topicNum)
    print("Topic {}".format(topicNum))
    url = config.urlTemplate.format(topicNum)
    text = getPage(url, cookies)
    topic.title, topic.subtitle = parsers.getTopicTitle(text)
    topic.category = parsers.getTopicCategory(text)
    for e in scrapeEntries(topicNum, config, cookies, text=text):
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
    cookies = None
    if config.loginUrl != None:
        cookies = login.tryLogin(config.loginUrl)
        if cookies == None:
            print("Failed login.")
            return

    for n in range(config.start, config.stop+1):
        topic = visit(n, config, cookies)
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
