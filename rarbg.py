#!/usr/bin/env python
import httplib
import urllib
import random
import time
import re
import datetime
from HTMLParser import HTMLParser
#from datetime import date


def_headers = {'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 
'accept-encoding':'deflate', 
'accept-language':'en-US,en;q=0.8', 
'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

max_entries=5
max_entries_in_page=25
#entry_structure=[link, title, imdb, date, size, L, S, comments, comment_count, uploader]

# Raw page parser to get the torrent info
class MainHTMLParser(HTMLParser):
    def __init__(self, max_entries):
        self.go='NOOP'
        self.dictionary=[]
        self.max_entries = max_entries
        self.current_entry = []
        HTMLParser.__init__(self)

    def _filter(self, entry):
        if ('YIFI' in entry['title']):
            print ("YIFI FOUND!")
            return False
        if (not 'GB' in entry['size']):
            print ("Size not in GB "+str(entry['size']))
            return False
        clean_size = float(re.sub(' .*','',entry['size']))
        if (clean_size < 3.8):
            print ("Size too small "+str(entry['size']))
            return False
        return True

    def _translate(self, entry):
        result={}
        if (len(entry) < 7):
#            print "TRANSLATION LENGTH BAD {}".format(str(len(entry)))
#            print "================================"
#            print entry
#            print "================================"
            return False
        result['link'] = entry[0]
        result['title'] = entry[1]
        result['imdb'] = entry[2]
        result['date'] = entry[3]
        result['size'] = entry[4]
        result['L'] = entry[5]
        result['S'] = entry[6]
        return result

    def handle_starttag(self, tag, attrs):
        #Mark beginning of items
        if (self.go=='NOOP' and tag == 'tr'):
            for i in attrs:
                if ('lista2' == i[1]):
                    self.go='ITEM'
                    return

        if (self.go == 'ITEM'):
            if (tag == 'a'):
                for i in attrs:
                    if (i[0] == 'href' and 'torrent/' in i[1]):
                        self.current_entry.append(i[1])
    
    def handle_data(self, data):
        if ((self.go == 'ITEM') and (data.strip())):
            self.current_entry.append(data)
    
    def handle_endtag(self, tag):
        if ((self.go == 'ITEM') and (tag == 'tr')):
            entry = self._translate(self.current_entry)
            if (entry) and (self._filter(entry)):
                self.dictionary.append(self.current_entry)
            self.current_entry=[]
            if (len(self.dictionary) == self.max_entries):
                self.go='ABORT'

# Parser for the torrent links extracted from pages
class MagnetizerHTMLParser(HTMLParser):
    def __init__(self, max_entries):
        self.max_entries=max_entries
        self.entry=0
        self.go='GO'
        self.dictionary=[]
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if (tag == 'a' and self.go == 'GO'):
            for i in attrs:
                if ('href' == i[0] and 'magnet' in i[1]):
                    self.dictionary.append(i[1])
                    if (len(self.dictionary) == self.max_entries):
                        # We have enough unique entries, stop here
                        self.go='ABORT'

def generate_torrent(magnet, name, dry=False):
    torrent="d10:magnet-uri{}:{}e".format(len(magnet),magnet)
    if (not dry):
        for i in range(max_entries):
            f=open("/home/ishaypeled/rtorrent/watch/"+name+".torrent", "w")
            f.write(torrent)
            f.close()

def transact(headers, body='', method="GET", path="/"):
    time.sleep(random.randint(1,10))
    c = httplib.HTTPSConnection("rarbg.to")
    print "Making {} request to {}...".format(method, path)
    c.request(method=method, url=path, body=body, headers=headers)
    response = c.getresponse()
    print "Response status [{}] reason [{}]...".format(response.status, response.reason)
    # We didn't get the response we wanted
    if (response.status != 200):
        print 'Damn, Were caught! Status is '+str(response.status)
        return False
    return response.read()

def main():
    # This parser will handle each torrents page to extract torrent title and torrent link
    parser = MainHTMLParser(max_entries)
    # This parser will handle each torrent link to extract magnet info from. Initializing here to keep persistant
    magnets = MagnetizerHTMLParser(max_entries)
    i=0
    for i in parser.dictionary:
        print i
    while (len(parser.dictionary) < max_entries):
        page = transact(headers=def_headers, path="/torrents.php?category=45&page="+str(i))
        if (not page):
            # We're caught...
            print "Master, they're on to us at torrent page! Do something!"
            return
        parser.feed(page)
        i=i+1

    for i in parser.dictionary:
        # Get torrent page
        page=transact(headers=def_headers, body='', method="GET", path=i[0])
        if (not page):
            # We're caught...
            print "Master, they're on to us at torrent link! Do something!"
            break
        # Feed torrent page to the magnets parser
        magnets.feed(page)

    for i in range(len(magnets.dictionary)):
        print ("====================\nTitle: [{}]\nMagnet: [{}]\nFilename: {}".format(parser.dictionary[i][1], magnets.dictionary[i], parser.dictionary[i][0]+".torrent"))
        generate_torrent(magnets.dictionary[i], parser.dictionary[i][0].replace('/torrent/',''), True)
    
    with open('db.txt', 'a') as f:
        for item in (parser.dictionary):
            f.write(str(datetime.datetime.now()))
            for i in range(7):
                f.write(",,"+item[i])
            f.write('\n')

if (__name__ == '__main__'):
    main()
