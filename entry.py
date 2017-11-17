class Entry:
    def __init__(self, entryId, topicId):
        self.entryId = entryId
        self.topicId = topicId
        self.userId = None
        self.userName = None
        self.date = None
        self.content = None
    
    def __str__(self):
        output = []
        output.append("## Entry {}".format(self.entryId))
        output.append("User: {} - {}".format(self.userId, self.userName))
        output.append("Date: {}".format(self.date))
        output.append("----")
        output.append(str(self.content))
        return '\n'.join(output)

class Topic:
    def __init__(self, topicId):
        self.topicId = topicId
        self.title = None
        self.subtitle = None
        self.category = None
        self.entries = []
