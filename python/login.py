__author__ = 'jwjiang'

import cookielib
import urllib, urllib2
import sys
import re

class WebLogin(object):

    dmca_pattern = '<h1 style="text-align:center">(This download is no longer available)</h1>'

    def __init__(self, username, password, list=None):
        # login credentials
        self.username = username
        self.password = password

        # osu website
        self.url = "http://osu.ppy.sh"

        # login action
        self.login_action = "https://osu.ppy.sh/forum/ucp.php?mode=login"

        # file for storing cookies
        self.cookies = "osu.login.cookies"

        # set up a cookie jar to store cookies
        self.cj = cookielib.MozillaCookieJar(self.cookies)

        # set up opener to handle cookies, redirects etc
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cj)
        )

        # pretend we're a web browser and not a python script
        self.opener.addheaders = [('User-agent',
            'Mozilla/5.0')]

        # authenticate with site
        self.login()

        # test download
        #if list is None:
        #    self.download("https://osu.ppy.sh/b/653326", "test.zip")

        # download all beatmaps from provided list


    def login(self):
        login_action = self.login_action
        login_data = urllib.urlencode({
            'username' : self.username,
            'password' : self.password,
            'autologin' : 'on',
            'login' : 'login',
            'redirect' : '/',
            'sid' : ''
        })

        response = self.opener.open(login_action, login_data)
        self.cj.save()
        return response

    def download(self, url):
        dlresponse = self.opener.open(url)
        data = dlresponse.read()
        if re.findall(self.dmca_pattern, data):
            return None
        return data

    '''
    def download(self, url, filename):
        response = self.opener.open(url)
        source = response.read()
        downloadSuffix = re.findall('/d/([0-9]+)', source)
        if downloadSuffix:
            downloadUrl = 'https://osu.ppy.sh/d/' + downloadSuffix[0]
        urllib.urlretrieve(url, filename)
        dlresponse = self.opener.open(downloadUrl)
        data = dlresponse.read()
        with open(filename, 'wb') as beatmap:
            beatmap.write(data)
        print('Download completed')
    '''
if __name__ == "__main__":
    args = sys.argv

    # check for username and password
    if len(args) != 3:
        print "Incorrect number of arguments"
        print "Argument pattern: username password"
        exit(1)

    username = args[1]
    password = args[2]

    # initialise and login to the website
    WebLogin(username, password)
