#!/usr/bin/env python

import sys
from AdapterRarbg import AdapterRarbg

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
    search = sys.argv[2:]
    adapter = AdapterRarbg(search, category, 5)
    adapter.refresh()
