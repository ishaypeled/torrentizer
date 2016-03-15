class Adapter:
    def __init__(self, searchString, category, maxEntries):
        self._searchString = searchString
        self._category = category
        self._maxEntries = maxEntries

    def getAdapterName(self):
        raise("Not implemented")

    def getItems(self):
        raise("Not implemented")

    def refresh():
        raise("Not implemented")
