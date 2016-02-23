#!/usr/bin/env python
import httplib
import urllib, urllib2
import lxml.html
from py_phone.menu import show_menu
# import random
# import time
# import re
import datetime
import sys, os
# from datetime import date
from Adapter import Adapter
from Parsers import MainHTMLParser, MagnetizerHTMLParser
try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract


def_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'accept-encoding': 'deflate',
    'accept-language': 'en-US,en;q=0.8',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

max_pages = 1
max_entries = 5
options = []
# entry_structure=
# [link, title, imdb, date, size, L, S, comments, comment_count, uploader]


def generate_torrent(magnet, name, dry=False):
    torrent = "d10:magnet-uri{}:{}e".format(len(magnet), magnet)
    if (not dry):
        for i in range(max_pages):
            f = open(os.environ['HOME'] + "/rtorrent/watch/"+name+".torrent", "w")
            f.write(torrent)
            f.close()


def transact(headers, body='', method="GET", path="/"):
    # time.sleep(random.randint(1,10))
    c = httplib.HTTPSConnection("rarbg.to")
    print "Making {} request to {}...".format(method, "rarbg.to"+path)
    c.request(method=method, url=path, body=body, headers=headers)
    response = c.getresponse()
    print "Response status [{}] reason [{}]...".format(response.status, response.reason)
    # We didn't get the response we wanted
    if (response.status != 200):
        print 'Damn, Were caught! Status is '+str(response.status)
        if response.status == 302:
            solve_captcha()
#         print response.getheaders()
        return False
    return response.read()


def get_captcha(url):
    """
    Grab the captcha from bot_check
    """
    req = urllib2.Request(url, None, def_headers)
    f = urllib2.urlopen(req)
    page = f.read()

    # Grab captcha image from url
    tree = lxml.html.fromstring(page)
    imgurl = "http://rarbg.to" + tree.xpath(".//img")[1].get('src')

    # Read the image and write to file
    req = urllib2.Request(imgurl, None, def_headers)
    f = urllib2.urlopen(req)
    img = f.read()

    open('out.png', 'wb').write(img)
    captcha = pytesseract.image_to_string(Image.open('out.png'), lang='eng')
    return captcha


def solve_captcha():
    """
    solve captcha and submit form
    """
    url = 'http://rarbg.to/bot_check.php'
    captcha = get_captcha(url)
    values = {'solve_string': captcha}

    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, def_headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    print("[+] " + captcha + " is your captcha, now do something with it")
    # TODO: input captcha in text field and submit form


def main(category):
    target = sys.argv[2:]
    # This parser will handle each torrents page to extract
    # torrent title and torrent link
    parser = MainHTMLParser(max_entries)
    # This parser will handle each torrent link to extract magnet info from.
    # Initializing here to keep persistant
    magnets = MagnetizerHTMLParser(max_entries)
    i = 0
    while (len(parser.dictionary) < max_pages):
        parameters = {
                'search': target,
                'category': category,
                'order': 'seeders',
                'by': 'DESC',
                'page': str(i)
                 }
        parameters = urllib.urlencode(parameters)
        path = "/torrents.php?"+parameters

        page = transact(headers=def_headers, path=path)
        if (not page):
            # We're caught...
            print "Master, they're on to us at torrent page! Do something!"
            return
        parser.feed(page)
        i = i+1

    for i in parser.dictionary:
        # Get torrent page
        page = transact(headers=def_headers, body='', method="GET", path=i[0])
        if (not page):
            # We're caught...
            print "Master, they're on to us at torrent link! Do something!"
            break
        # Feed torrent page to the magnets parser
        magnets.feed(page)

    for i in range(len(magnets.dictionary)):
        title = parser.dictionary[i][1]
        size = parser.dictionary[i][4]
        seeders = parser.dictionary[i][5]
#         print ("====================\nTitle: [{}]\nMagnet: [{}]\nFilename: {}".format(parser.dictionary[i][1], magnets.dictionary[i], parser.dictionary[i][0]+".torrent"))
        options.append(title + " | " + size + " | " + seeders + " seeders")

    # TODO: send and retrieve selection from DevopsBot
    print("----------------------------------------------------------------------")
    selection = show_menu(options, sort=False, location=True)
    try:
        generate_torrent(magnets.dictionary[selection], parser.dictionary[selection][0].replace('/torrent/', ''))
    except IndexError:
        print("Exiting")
        sys.exit(0)

    with open('db.txt', 'a') as f:
        for item in (parser.dictionary):
            f.write(str(datetime.datetime.now()))
            for i in range(7):
                f.write(",,"+item[i])
            f.write('\n')

def usage():
    msg = """Usage: """+sys.argv[0]+""" <option> <search>

options:
    -tv     -       search for TV shows
    -mv     -       search for movies"""
    print(msg)
    exit(1)

if (__name__ == '__main__'):
    if (len(sys.argv) < 3):
        usage()
    if "-mv" in sys.argv[1]:
        category = '44;45'
    elif "-tv" in sys.argv[1]:
        category = '18;41'
    else:
        print("Invalid option!")
        usage()
    main(category)
