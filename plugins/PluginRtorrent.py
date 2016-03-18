from Plugin import Plugin
from uuid import uuid4
import logging
import os


class PluginRtorrent(Plugin):

    def __init__(self):
        """
        Initialize the rtorrent plugin
        """
        self._logger = logging.getLogger(__name__)
        self._name = "PluginRarbg"

    def putMagnet(self, magnet, dry=False):
        """
        Put magnet in rtorrent watch directory. If dry is set
        then just log it
        """
        torrent = self._generateTorrent(magnet)
        fileName = uuid4().hex + ".torrent"
        if (not dry):
            f = open(os.environ['HOME'] +
                     "/rtorrent/watch/" +
                     fileName, "w")
            f.write(torrent)
            f.close()
        else:
            self._logger.info("--=== DRY ===--")
            self._logger.info("magnet: "+magnet)
            self._logger.info("generated torrent name: "+fileName)
