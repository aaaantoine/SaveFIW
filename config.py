import configparser

class Config:
    def __init__(self, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        c = config['DEFAULT']
        self.start = int(c['start'])
        self.stop = int(c['stop'])
        self.loginUrl = c['loginUrl'] if 'loginUrl' in c else None
        self.urlTemplate = c['urlTemplate']
        self.outputFolder = c['outputFolder']

