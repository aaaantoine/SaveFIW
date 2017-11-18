from html.parser import HTMLParser
import re
from entry import Entry

def debug(text): pass #print(text)
def info(text): print(text)

entryStart = '\t<!--Begin Msg Number '

def getEntriesRaw(html):
    lines = html.split('\n')
    output = []
    collecting = False
    for line in lines:
        if line.startswith(entryStart):
            collecting = True
        if collecting:
            output.append(line)
            if line.startswith('    </table>'):
                yield '\n'.join(output)
                output = []
                collecting = False

def getEntryId(rawEntry):
    # sample format: <!--Begin Msg Number 40009379-->
    return rawEntry.split('\n')[0][len(entryStart):-3]

def getUser(rawEntry):
    np = NameParser()
    np.feed(rawEntry)
    return np.userId, np.userName
    
def getDate(rawEntry):
    dp = DateParser()
    dp.feed(rawEntry)
    return dp.date
    
def getContent(rawEntry):
    contentstart = "        <div class='postcolor'>"
    contentend = "</div>"
    lines = rawEntry.split('\n')
    for line in lines:
        if line.startswith(contentstart):
            return line[len(contentstart):-len(contentend)].strip()
    
def buildEntryFromRaw(topicId, rawEntry):
    e = Entry(getEntryId(rawEntry), topicId)
    
    e.userId, e.userName = getUser(rawEntry)
    e.date = getDate(rawEntry)
    e.content = getContent(rawEntry)
    
    return e

def getTopicTitleRaw(rawEntry):
    lines = rawEntry.split('\n')
    for line in lines:
        if line.startswith("    <div class='maintitle'>"):
            return line

titleRE = re.compile("    <div class='maintitle'>&nbsp;<b>([^<]*)</b>([^<]*)</div>")
def parseTopicTitle(titleRaw):
    m = titleRE.match(titleRaw)
    if m == None:
        return None, None
    title = m.group(1)
    subtitle = m.group(2)[2:]
    print("Title: {}".format(title))
    print("Subtitle: {}".format(subtitle))
    return title, subtitle
        
def getTopicTitle(rawEntry):
    titleRaw = getTopicTitleRaw(rawEntry)
    return (None, None) if titleRaw == None else parseTopicTitle(titleRaw)

def getTopicCategoryRaw(rawEntry):
    lines = rawEntry.split('\n')
    for line in lines:
        if line.startswith("<div id='navstrip'"):
            return line

catRE = re.compile("<a href='.*?(c=\d+|showforum=\d+)'>([^<]*)</a>")
def parseTopicCategory(categoryRaw):
    return catRE.findall(categoryRaw)

def getTopicCategory(rawEntry):
    categoryRaw = getTopicCategoryRaw(rawEntry)
    return None if categoryRaw == None else parseTopicCategory(categoryRaw)

pageRE = re.compile("<a href='([^']*)'>([^<]*)</a>")
def detectPages(html):
    def getPageLine(html):            
        lines = html.split('\n')
        for line in lines:
            if 'title="Jump to page..."' in line:
                return line
    
    line = getPageLine(html)
    if line == None:
        return 1, []
    
    pages = []
    bits = line.split('&nbsp;') # staple of the old-school web
    for bit in bits:
        if bit.startswith("<b>["):
            currentPage = int(bit.replace("<b>[", "").replace("]</b>", ""))
        elif bit.startswith("<a "):
            m = pageRE.match(bit)
            if m != None:
                url, pageNum = m.group(1, 2)
                if pageNum == "Last &raquo;" or pageNum == "&laquo; First":
                    continue
                url = url.replace("&amp;", "&")
                pages.append((int(pageNum), url))
    return currentPage, pages

def getAttribute(attrs, name):
    nv = [(a,v) for a, v in attrs if a == name]
    return nv[0][1] if len(nv) > 0 else None

def getQuerystringData(href):
    if "?" not in href:
        return {}
    qs = "?".join(href.split("?")[1:])
    pairs = qs.split("&")
    d = {}
    for pair in pairs:
        s = pair.split("=")
        d[s[0]] = "=".join(s[1:])
    return d



class NameParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.reading = False
        self.userId = None
        self.userName = None
    
    def handle_starttag(self, tag, attrs):
        if self.__detectNameStart(tag, attrs):
            debug("Start reading name")
            self.reading = True
        elif self.reading:
            userId = self.__getUserId(tag, attrs)
            if userId != None:
                self.userId = userId

    def handle_endtag(self, tag):
        if self.__detectNameEnd(tag):
            debug("End reading name")
            self.reading = False

    def handle_data(self, data):
        if self.reading:
            self.userName = data
        
    def __detectNameStart(self, tag, attrs):
        if self.reading or self.userName != None:
            return False
        if tag != "span":
            return False
        className = getAttribute(attrs, "class")
        return className != None and className in ("normalname", "unreg")
    
    def __getUserId(self, tag, attrs):
        if not self.reading:
            return None
        if tag != "a":
            return None
        href = getAttribute(attrs, "href")
        if href == None:
            return None
        qs = getQuerystringData(href)
        return qs["showuser"] if "showuser" in qs.keys() else None

    def __detectNameEnd(self, tag):
        if not self.reading:
            return False
        return tag == "span"

class DateParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.readingPostDetails = False     # precursor for reading date
        self.reading = False
        self.date = None
    
    def handle_starttag(self, tag, attrs):
        if self.__detectPostDetailsStart(tag, attrs):
            self.readingPostDetails = True

    def handle_endtag(self, tag):
        if self.__detectDateEnd(tag):
            debug("End reading date")
            self.reading = False
        if self.__detectPostDetailsEnd(tag):
            self.readingPostdetails = False

    def handle_data(self, data):
        if self.reading:
            self.date = data.strip() # TODO: actually store date format!
        elif self.__detectDateStart(data):
            debug("Start reading date")
            self.reading = True
        
    def __detectPostDetailsStart(self, tag, attrs):
        if self.date != None:
            return False
        if tag != "span":
            return False
        className = getAttribute(attrs, "class")
        return className == "postdetails"

    def __detectPostDetailsEnd(self, tag):
        if not self.readingPostDetails:
            return False
        return tag == "span"

    def __detectDateStart(self, data):
        if not self.readingPostDetails:
            return False
        return data == "Posted:"

    def __detectDateEnd(self, tag):
        if not self.reading:
            return False
        return tag == "span"
