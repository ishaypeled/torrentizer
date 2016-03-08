import urllib
import urllib2
import httplib
import lxml.html
import os
import pytesseract
import pyprind
from Adapter import Adapter
from ParsersRarbg import MainHTMLParser, MagnetizerHTMLParser
from PIL import Image


class AdapterRarbg(Adapter):
    TITLE = 'Title'
    MAGNET = 'Magnet'
    FILENAME = 'Filename'
    LINK = 'Link'
    IMDB = 'IMDB'
    DATE = 'Date'
    SIZE = 'Size'
    LEECHERS = 'Leechers'
    SEEDERS = 'Seeders'
    MAX_PAGES = 1

    def __init__(self, searchString, category, maxEntries):
        """
        Initialize the RarBg adapter
        """
        Adapter.__init__(self, searchString, category, maxEntries)
        self._defHeaders = {
            'accept': '''text/html,application/xhtml+xml,application/xml;q=0.9,
            image/webp,*/*;q=0.8''',
            'accept-encoding': 'deflate',
            'accept-language': 'en-US,en;q=0.8',
            'user-agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'''}

    def _getCaptcha(self, url):
        """
        Grab the captcha from bot_check
        """
        req = urllib2.Request(url, None, self._defHeaders)
        f = urllib2.urlopen(req)
        page = f.read()

        # Grab captcha image from url
        tree = lxml.html.fromstring(page)
        captcha_target = tree.xpath(".//img")[1].get('src')
        captcha_id = tree.xpath(".//input")[1].get('value')
        imgurl = "http://rarbg.to" + captcha_target

        # Read the image and write to file
        req = urllib2.Request(imgurl, None, self._defHeaders)
        f = urllib2.urlopen(req)
        img = f.read()

        open('out.png', 'wb').write(img)
        captcha = pytesseract.image_to_string(
                Image.open('out.png'), lang='eng')
        return (captcha, captcha_id)

    def _solveCaptcha(self):
        """
        Solve captcha and submit form
        """
        url = 'http://rarbg.to/bot_check.php'
        captcha, captcha_id = self._getCaptcha(url)
        print("Id: "+captcha_id)
        values = {'solve_string': captcha,
                  'captcha_id': captcha_id,
                  'submitted_bot_captcha': '1'}

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data, self._defHeaders)
        response = urllib2.urlopen(req)
        response.read()

        print("[+] " + captcha + " is your captcha. "
                                 "It has been submitted and you should "
                                 "be good to go!")

    def getAdapterName(self):
        """
        Identifier for this adapter
        """
        return "rarbg.to adapter"

    def getItems(self):
        """
        Found entries for this adapter
        """
        return self._entries

    def _generateTorrent(self, magnet, name, dry=False):
        """
        Make torrent from magnet
        XXX: Extract to another utility class
        """
        torrent = "d10:magnet-uri{}:{}e".format(len(magnet), magnet)
        if (not dry):
            for i in range(AdapterRarbg.MAX_PAGES):
                f = open(os.environ['HOME'] +
                         "/rtorrent/watch/" +
                         name +
                         ".torrent", "w")
                f.write(torrent)
                f.close()

    def _transact(self, headers, body='', method="GET", path="/"):
        """
        Make http transaction and return the response
        """
        c = httplib.HTTPSConnection("rarbg.to")
        c.request(method=method, url=path, body=body, headers=headers)
        response = c.getresponse()
        (response.status, response.reason)
        # We didn't get the response we wanted
        if (response.status != 200):
            print '\nDamn, Were caught! Status is '+str(response.status)
            if response.status == 302:
                self._solveCaptcha()
            return False
        return response.read()

    def refresh(self):
        """
        Populate entry list for specific search pattern
        """
        # This parser will handle each torrents page to extract
        # torrent title and torrent link
        parser = MainHTMLParser(self._maxEntries)
        # This parser will handle each torrent link to extract magnet info from
        # Initializing here to keep persistant
        magnets = MagnetizerHTMLParser(self._maxEntries)
        i = 0
        while (len(parser.dictionary) < AdapterRarbg.MAX_PAGES):
            parameters = {
                    'search': self._searchString,
                    'category': self._category,
                    'order': 'seeders',
                    'by': 'DESC',
                    'page': str(i)
                     }
            parameters = urllib.urlencode(parameters)
            path = "/torrents.php?"+parameters

            page = self._transact(headers=self._defHeaders, path=path)
            while (not page):
                # We're caught...
                print "Master, they're on to us at torrent page! Do something!"
                self._solveCaptcha()
                page = self._transact(headers=self._defHeaders,
                                      body='', method="GET", path=path)
            parser.feed(page)
            i = i+1

        bar = pyprind.ProgBar(len(parser.dictionary),
                              title="\nFetching results...",
                              width=70,
                              bar_char="*")
        for i in parser.dictionary:
            # Get torrent page
            page = self._transact(headers=self._defHeaders,
                                  body='', method="GET", path=i[0])
            while (not page):
                # We're caught...
                print "Master, they're on to us at torrent link! Do something!"
                self._solveCaptcha()
                page = self._transact(headers=self._defHeaders,
                                      body='', method="GET", path=i[0])
            # Feed torrent page to the magnets parser
            magnets.feed(page)
            bar.update()

        options = []
        for i in range(len(magnets.dictionary)):
            entry = {}
            entry[AdapterRarbg.FILENAME] = parser.dictionary[i][0]+".torrent"
            entry[AdapterRarbg.TITLE] = parser.dictionary[i][1]
            entry[AdapterRarbg.MAGNET] = magnets.dictionary[i]
            entry[AdapterRarbg.IMDB] = parser.dictionary[i][2]
            entry[AdapterRarbg.DATE] = parser.dictionary[i][3]
            entry[AdapterRarbg.SIZE] = parser.dictionary[i][4]
            entry[AdapterRarbg.SEEDERS] = parser.dictionary[i][5]
            entry[AdapterRarbg.LEECHERS] = parser.dictionary[i][6]

            options.append(entry[AdapterRarbg.TITLE])
            print '''
---['''+str(i)+''']---
Title: {}
Magnet: {}
IMDB: {}
Date: {}
Size: {}
Seeders: {}
Leechers: {}'''.format(entry[AdapterRarbg.TITLE],
                       entry[AdapterRarbg.MAGNET],
                       entry[AdapterRarbg.IMDB],
                       entry[AdapterRarbg.DATE],
                       entry[AdapterRarbg.SIZE],
                       entry[AdapterRarbg.SEEDERS],
                       entry[AdapterRarbg.LEECHERS])

            # XXX: Move this somewhere else
            self._generateTorrent(
                                    magnets.dictionary[i],
                                    parser.dictionary[i][0].
                                    replace('/torrent/', ''),
                                    True)
            print("Torrent added.")
