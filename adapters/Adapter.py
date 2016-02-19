class Adapter:
    def __init__(self, searchString, maxEntries):
        self._searchString = searchString
        self._maxEntries = maxEntries

    def getAdapterName(self):
        raise("Not implemented")

    def getItems(self):
        raise("Not implemented")

    def refresh():
        raise("Not implemented")
