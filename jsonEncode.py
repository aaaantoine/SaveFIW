import json
import datetime

# for serialization reference
from entry import Entry, Topic

class EntryEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Entry):
            return {
                'entryId': o.entryId,
                'userId': o.userId,
                'userName': o.userName,
                'date': o.date,
                'content': o.content 
            }
        elif isinstance(o, Topic):
            return {
                'topicId': o.topicId,
                'title': o.title,
                'subtitle': o.subtitle,
                'entries': o.entries
            }
        elif isinstance(o, datetime.date):
            return o.isoformat()
        else:
            return super().default(o)
    
def save(entries, filename):
    with open(filename, 'w') as outfile:
        json.dump(entries, outfile, cls=EntryEncoder)
