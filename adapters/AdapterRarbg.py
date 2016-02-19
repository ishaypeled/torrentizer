import urllib
import httplib
from Adapter import Adapter
from Parsers import MainHTMLParser, MagnetizerHTMLParser


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

    def __init__(self, searchString, maxEntries):
        # super(AdapterRarbg, self).__init__(self, searchString, maxEntries)
        Adapter.__init__(self, searchString, maxEntries)
        self._entries = []
        self._defHeaders = {
            'accept': '''text/html,application/xhtml+xml,application/xml;q=0.9,
            image/webp,*/*;q=0.8''',
            'accept-encoding': 'deflate',
            'accept-language': 'en-US,en;q=0.8',
            'user-agent': '''Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'''}

    def getAdapterName(self):
        return "rarbg.to adapter"

    def getItems(self):
        return self._entries

    def _generateTorrent(self, magnet, name, dry=False):
        torrent = "d10:magnet-uri{}:{}e".format(len(magnet), magnet)
        if (not dry):
            for i in range(AdapterRarbg.MAX_PAGES):
                # XXX: This should probably not be here
                f = open("/home/ishaypeled/rtorrent/watch/" +
                         name +
                         ".torrent", "w")
                f.write(torrent)
                f.close()

    def _transact(self, headers, body='', method="GET", path="/"):
        # time.sleep(random.randint(1,10))
        c = httplib.HTTPSConnection("rarbg.to")
        print "Making {} request to {}...".format(method, "rarbg.to/"+path)
        c.request(method=method, url=path, body=body, headers=headers)
        response = c.getresponse()
        print "Response status [{}] reason [{}]...".format
        (response.status, response.reason)
        # We didn't get the response we wanted
        if (response.status != 200):
            print 'Damn, Were caught! Status is '+str(response.status)
            print response.getheaders()
            return False
        return response.read()

    def refresh(self):
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
                    'category': '18',
                    'category': '41',
                    'order': 'seeders',
                    'by': 'DESC',
                    'page': str(i)
                     }
            parameters = urllib.urlencode(parameters)
            path = "/torrents.php?"+parameters

            page = self._transact(headers=self._defHeaders, path=path)
            if (not page):
                # We're caught...
                print "Master, they're on to us at torrent page! Do something!"
                return
            parser.feed(page)
            i = i+1

        for i in parser.dictionary:
            # Get torrent page
            page = self._transact(headers=self._defHeaders,
                                  body='', method="GET", path=i[0])
            if (not page):
                # We're caught...
                print "Master, they're on to us at torrent link! Do something!"
                break
            # Feed torrent page to the magnets parser
            magnets.feed(page)

        for i in range(len(magnets.dictionary)):
            entry = {}
            entry[AdapterRarbg.FILENAME] = parser.dictionary[i][0]+".torrent"
            entry[AdapterRarbg.TITLE] = parser.dictionary[i][1]
            entry[AdapterRarbg.MAGNET] = magnets.dictionary[i]
            entry[AdapterRarbg.IMDB] = parser.dictionary[i][2]
            entry[AdapterRarbg.DATE] = parser.dictionary[i][3]
            entry[AdapterRarbg.SIZE] = parser.dictionary[i][4]
            entry[AdapterRarbg.LEECHERS] = parser.dictionary[i][5]
            entry[AdapterRarbg.SEEDERS] = parser.dictionary[i][6]
            print (
                    '''Title: [{}]\n
                    Magnet: [{}]\n
                    Filename: {}'''.format(parser.dictionary[i][1],
                                           magnets.dictionary[i],
                                           parser.dictionary[i][0]+".torrent"))
            self._generateTorrent(
                                 magnets.dictionary[i],
                                 parser.dictionary[i][0].
                                 replace('/torrent/', ''),
                                 True)
