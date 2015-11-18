__author__ = 'jwjiang'

import urllib2
import re

def getupdates():
    lastfile = open("last", "w+")
    last = lastfile.read()

    if last == "":
        return open("list").readlines()
        return firstrun(lastfile)

def firstrun(lastfile):
    page_num = 1
    baseurl = "https://osu.ppy.sh/p/beatmaplist&s=4&r=0"
    master_list = []

    source = urllib2.urlopen(baseurl).read()
    lastlinks = None
    links = getlinks(source)
    while links != lastlinks:
        lastlinks = links
        lastlink = ''
        for link in links:
            if ''.join([lastlink, 'n']) == link:
                master_list.pop()
            master_list.append(link)
            lastlink = link
        print(str(page_num))
        source = urllib2.urlopen(nexturl(baseurl, page_num)).read()
        links = getlinks(source)
        page_num += 1

    last = master_list[0]
    lastfile.write(last)
    lastfile.close()
    listfile = open("list", "w+")
    for line in master_list:
        listfile.write("%s\n" % line)
    listfile.close()
    return master_list

def nexturl(baseurl, current):
    next = current + 1
    return ''.join([baseurl, '&page=', str(next)])

def getlinks(source):
    links = re.findall('/d/([0-9]+n*)', source)
    return links

if __name__ == "__main__":
    getupdates()