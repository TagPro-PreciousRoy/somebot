#!/usr/bin/env python
"""
png2json

This script takes a TagPro map PNG file and generates a starter
JSON with the x, y locations of all buttons, gates and portals
pre-filled.
"""
from __future__ import division

import copy
import sys
import json
import urllib
import cStringIO

from PIL import Image, ImageDraw


TILESIZE = 40
DEFAULTS = {
            "info": {
                "name": "Map Name Here",
                "author": "Your Name Here"
            },
            "switches": {},
            "fields": {},
            "marsballs": [],
            "portals": {},
        }

def usage():
    print 'Usage: {} PNG'.format(sys.argv[0])


class Map():
    """A preview generator for tagpro."""

    tiles = Image.open('tiles.png')
    speedpad = Image.open('speedpad.png')
    colormap = {
        'black': (0, 0, 0),
        'wall': (120, 120, 120),
        'tile': (212, 212, 212),
        'spike': (55, 55, 55),
        'button': (185, 122, 87),
        'powerup': (0, 255, 0),
        'gate': (0, 117, 0),
        'blueflag': (0, 0, 255),
        'redflag': (255, 0, 0),
        'speedpad': (255, 255, 0),
        'bomb': (255, 128, 0),
        'bluetile': (187, 184, 221),
        'redtile': (220, 186, 186),
        'portal': (202, 192, 0),
    }

    def __init__(self, pngpath):
        if 'http' in pngpath:
            pfile = cStringIO.StringIO(urllib.urlopen(pngpath).read())
            png = Image.open(pfile)
        else:
            png = Image.open(pngpath)
        self.png = png
        self.pixels = png.load()
        self.max_x, self.max_y = self.png.size

    def gen_json(self):
        map_json = copy.copy(DEFAULTS)
        for x in range(self.max_x):
            for y in range(self.max_y):
                key = "%i,%i" % (x, y)
                color = self.pixels[x, y][:3]
                if color == self.colormap['button']:
                    map_json['switches'][key] = {"toggle": [{"pos": {"x": None, "y": None}}],}
                if color == self.colormap['gate']:
                    map_json['fields'][key] = {"defaultState": "off"}
                if color == self.colormap['portal']:
                    map_json['portals'][key] = { "destination": { "x": None, "y": None }, "cooldown": None }
        return json.dumps(map_json, indent=4, separators=(',', ': '))


def main():
    if len(sys.argv) < 2:
        usage()
        return 1

    pngpath = sys.argv[1]

    map_ = Map(pngpath)
    json = map_.gen_json()

    sys.stdout.write(json)


if '__main__' == __name__:
    main()
    exit(0)
