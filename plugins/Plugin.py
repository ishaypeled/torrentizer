class Plugin:
    def putMagnet(self, magnet, dry=False):
        raise("Not implemented")

    def _generateTorrent(self, magnet):
        """
        Make torrent from magnet
        """
        torrent = "d10:magnet-uri{}:{}e".format(len(magnet), magnet)
        return torrent
