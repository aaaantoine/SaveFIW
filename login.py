import getpass
import requests

from config import Config
import parsers

def promptCredentials():
    username = input("Username: ")
    password = getpass.getpass()
    return username, password

def sendLoginRequest(url, creds):
    uname, pw = creds
    data = parsers.getLoginData(uname, pw)
    r = requests.post(url, data=data)
    return r.text, r.cookies

def tryLogin(url):
    creds = promptCredentials()
    response, cookies = sendLoginRequest(url, creds)
    errs = parsers.getErrors(response)
    if errs == None:
        return cookies
    else:
        print(errs)
        return None

if __name__ == '__main__':
    config = Config("scrape.ini")
    r = tryLogin(config.loginUrl)
    print(r)
