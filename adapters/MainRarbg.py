#!/usr/bin/env python

import sys
from AdapterRarbg import AdapterRarbg

search = sys.argv[1]
adapter = AdapterRarbg(search, 5)
adapter.refresh()
