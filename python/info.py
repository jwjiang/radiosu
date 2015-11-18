__author__ = 'jwjiang'

import urllib2
import re
import HTMLParser
import eyed3
import eyed3.mp3
import eyed3.id3
import threading
from multiprocessing import Lock
import time
import Queue
import sys
from bs4 import BeautifulSoup
import requests
import grequests

start_time = 0
global_counter = 0
total_dl_time = 0

baseurl = 'https://osu.ppy.sh/s/'
title_pattern = "<td width=0%>Title:</td><td class=\"colour\"><a href='/p/beatmaplist\?q=.*'>(.*)</a></td>"
artist_pattern = "<td width=0%>Artist:</td><td width=23% class='colour'><a href='/p/beatmaplist\?q=.*'>(.*)</a></td>"
genre_pattern = "<td width=0%>Genre:</td><td class=\"colour\"><a href='/p/beatmaplist\?g=.*'>(.*)</a> \(<a href=\'" \
                "/p/beatmaplist\?la=.*'>.*</a>\)</td>"


def parseWorker(meta_list, session, listlock, total, stepsize):
    global global_counter
    global start_time
    parser = HTMLParser.HTMLParser()

    #opener = urllib2.build_opener()
    #opener.addheaders = [('User-agent', 'Mozilla/5.0')]

    while not dlqueue.empty():
        try:
            next = dlqueue.get()
        except IndexError:
            return

        parse(next, session, parser, meta_list, listlock)

        if global_counter % stepsize == 0 or global_counter == total:
            runtime = time.time() - start_time
            time_left = (total-global_counter)/(global_counter/runtime)
            print(str(global_counter) + '/' + str(total) + ' processed, ' +
                             'estimated time remaining: %.0f seconds' % time_left)
        dlqueue.task_done()

def parse(url, session, parser, meta_list, listlock):
    global global_counter
    #r = urllib2.Request(url=url)
    #r.add_header('User-Agent', 'Mozilla/5.0')
    #response = urllib2.urlopen(r)
    #source = response.read()
    headers = {'user-agent': 'Mozilla/5.0'}
    source = session.get(url, headers=headers, stream=False).text
    # source = requests.get(url).text
    # source = opener.open(url).read()

    title = parser.unescape(re.search(title_pattern, source).group(1))
    artist = parser.unescape(re.search(artist_pattern, source).group(1))
    genre = parser.unescape(re.search(genre_pattern, source).group(1))

    listlock.acquire()
    meta_list.append((title, artist, genre))
    global_counter += 1
    listlock.release()

def parse_bs(parser, source):
    '''
    souped = BeautifulSoup(source, "html.parser")
    songinfo = souped.find('table', { 'id' : 'songinfo'})
    artist = songinfo.find(text='Artist:').findNext('a', text=True)
    title = songinfo.find(text='Title:').findNext('a', text=True)
    genre = songinfo.find(text='Genre:').findNext('a', text=True)
    '''
    title = parser.unescape(re.search(title_pattern, source).group(1))
    artist = parser.unescape(re.search(artist_pattern, source).group(1))
    genre = parser.unescape(re.search(genre_pattern, source).group(1))

    meta_tuple = (title, artist, genre)
    return meta_tuple

def getinfo(list, count=None):
    global start_time
    start_time = time.time()


    return grequests_download(list)
    #return pooled_download(list)

    if count is None or count > 100:
        return multi_download(list)
    else:
        # can just use sequential for small numbers of downloads
        return seq_download(list)

def grequests_download(list):
    global start_time
    newlist = []
    for item in list:
        newlist.append(''.join([baseurl, item]))
    rs = (grequests.get(url) for url in newlist)
    newnewlist = grequests.map(rs, size=2)
    runtime = time.time() - start_time
    print("Total links scraped: " + str(len(newnewlist)))
    print("Total scrape time: " + str(runtime))
    print("Links per second: " + str((len(newnewlist)/runtime)))

    return rs

def pooled_download(list):
    global start_time
    global global_counter
    meta_list = []
    total = len(list)
    stepsize = int(total/200)
    if stepsize == 0:
        stepsize = 10

    session = requests.Session()
    headers = {'user-agent': 'Mozilla/5.0'}
    parser = HTMLParser.HTMLParser()

    for item in list:
        req = session.get(''.join([baseurl, item]), headers=headers, stream=False)
        source = req.text
        meta_tuple = parse_bs(parser, source)
        meta_list.append(meta_tuple)
        global_counter += 1
        if global_counter % stepsize == 0 or global_counter == total:
            runtime = time.time() - start_time
            time_left = (total-global_counter)/(global_counter/runtime)
            print(str(global_counter) + '/' + str(total) + ' processed, ' +
                             'estimated time remaining: %.0f seconds' % time_left)
    return meta_list

dlqueue = Queue.Queue()
def multi_download(list):
    meta_list = []
    workers = []
    listlock = Lock()
    count = len(list)
    stepsize = int(count/200)
    if stepsize == 0:
        stepsize = 10

    session = requests.Session()

    for item in list:
        dlqueue.put(''.join([baseurl, item]))

    for i in range(10):
        worker = threading.Thread(target=parseWorker, args = [meta_list, session, listlock, count, stepsize])
        worker.daemon = True
        workers.append(worker)
        worker.start()

    while not dlqueue.empty():
        time.sleep(0.5)

    return meta_list

def seq_download(list):
    meta_list = []
    parser = HTMLParser.HTMLParser()
    current = 0
    count = len(list)
    total_parse_time = 0
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0')]
    for item in list:
        before_parse = time.time()

        source = opener.open(''.join([baseurl, item])).read()

        title = parser.unescape(re.search(title_pattern, source).group(1))
        artist = parser.unescape(re.search(artist_pattern, source).group(1))
        genre = parser.unescape(re.search(genre_pattern, source).group(1))

        parse_time = time.time() - before_parse
        total_parse_time += parse_time
        meta_tuple = (title, artist, genre)
        meta_list.append(meta_tuple)
        current += 1
        # print progress

        if current % 10 == 0 or current == count:
            runtime = time.time() - start_time
            print(str(current) + '/' + str(count) + ' processed.')
            # print("--- %s seconds ---" % (runtime))
            time_left = (count-current)/(current/runtime)
            print("Estimated time remaining: %.0f seconds\n" % time_left)
    sys.stdout.flush()
    return meta_list

def setinfo(file, infotuple):
    eyed3.log.setLevel("ERROR")
    mp3file = eyed3.load(file)
    mp3file.tag = eyed3.id3.Tag()
    mp3file.tag.title = unicode(infotuple[0])
    mp3file.tag.artist = unicode(infotuple[1])
    mp3file.tag.genre = unicode(infotuple[2])
    mp3file.tag.save(filename=file)

if __name__ == "__main__":
    list = open("list").readlines()
    getinfo(list)