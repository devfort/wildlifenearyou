#!/usr/bin/python

import sys
import re
from BeautifulSoup import BeautifulSoup as BS

f = open(sys.argv[1])

soup = BS(f)


for s in soup.findAll('script', {'type':re.compile('javascript')}):
    if s.contents:
        for c in s.contents:
            print c
