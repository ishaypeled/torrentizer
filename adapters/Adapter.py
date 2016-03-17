class Adapter:
    """
    These are definitions for entry lookup
    """
    TITLE = 'Title'
    MAGNET = 'Magnet'
    FILENAME = 'Filename'
    LINK = 'Link'
    IMDB = 'IMDB'
    DATE = 'Date'
    SIZE = 'Size'
    LEECHERS = 'Leechers'
    SEEDERS = 'Seeders'

    def __init__(self, searchString, category, maxEntries):
        self._searchString = searchString
        self._category = category
        self._maxEntries = maxEntries
        self._entries = []

    def getAdapterName(self):
        raise("Not implemented")

    def getItems(self):
        raise("Not implemented")

    def prettyPrintTorrents(self):
        for entry in self._entries:
            print '''
---['''+entry[Adapter.TITLE]+''']---
Magnet: {}
IMDB: {}
Date: {}
Size: {}
Seeders: {}
Leechers: {}'''.format(entry[Adapter.MAGNET],
                       entry[Adapter.IMDB],
                       entry[Adapter.DATE],
                       entry[Adapter.SIZE],
                       entry[Adapter.SEEDERS],
                       entry[Adapter.LEECHERS])

    def refresh(self):
        raise("Not implemented")

    def getTorrents(self):
        raise("Not implemented")
