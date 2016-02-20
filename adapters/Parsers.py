from HTMLParser import HTMLParser


# Raw page parser to get the torrent info
class MainHTMLParser(HTMLParser):
    def __init__(self, max_entries):
        self.go = 'NOOP'
        self.dictionary = []
        self.max_entries = max_entries
        self.current_entry = []
        HTMLParser.__init__(self)

    def _filter(self, entry):
        if ('YIFI' in entry['title']):
            return False
        # if (not 'GB' in entry['size']):
        #    print ("Size not in GB "+str(entry['size']))
        #    return False
        # clean_size = float(re.sub(' .*','',entry['size']))
        # if (clean_size < 3.8):
        #    print ("Size too small "+str(entry['size']))
        #    return False
        return True

    def _translate(self, entry):
        result = {}
        if (len(entry) < 7):
            # print "TRANSLATION LENGTH BAD {}".format(str(len(entry)))
            # print "================================"
            # print entry
            # print "================================"
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
        # Mark beginning of items
        if (self.go == 'NOOP' and tag == 'tr'):
            for i in attrs:
                if ('lista2' == i[1]):
                    self.go = 'ITEM'
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
            self.current_entry = []
            if (len(self.dictionary) == self.max_entries):
                self.go = 'ABORT'


# Parser for the torrent links extracted from pages
class MagnetizerHTMLParser(HTMLParser):
    def __init__(self, max_pages):
        self.max_entries = max_pages
        self.entry = 0
        self.go = 'GO'
        self.dictionary = []
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if (tag == 'a' and self.go == 'GO'):
            for i in attrs:
                if ('href' == i[0] and 'magnet' in i[1]):
                    self.dictionary.append(i[1])
                    if (len(self.dictionary) == self.max_entries):
                        # We have enough unique entries, stop here
                        self.go = 'ABORT'
