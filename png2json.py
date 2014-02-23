#!/usr/bin/env python
"""
png2json

This script takes a TagPro map PNG file and outputs starter
JSON with the x, y locations of all buttons, gates and portals
pre-filled.
"""
from __future__ import division
from collections import OrderedDict

import copy
import sys
import json
import urllib
import cStringIO
import re

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
            "gates": [],
            "bombs": []
        }

def usage():
    print 'Usage: {} PNG > JSON'.format(sys.argv[0])



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
        map_data = self._gen_data()
        map_data = self._sort_data(map_data)
        map_json = self._format_json(map_data)
        return map_json

    def _gen_data(self):
        map_data = copy.copy(DEFAULTS)
        for x in range(self.max_x):
            for y in range(self.max_y):
                key = (x, y)
                color = self.pixels[x, y][:3]
                if color == self.colormap['button']:
                    map_data['switches'][key] = {"toggle": [],}
                if color == self.colormap['gate']:
                    map_data['fields'][key] = {"defaultState": "off"}
                    map_data['gates'].append({"pos": {"x": x, "y": y}})
                if color == self.colormap['portal']:
                    map_data['portals'][key] = { "destination": {}, "cooldown": 20 }
                if color == self.colormap['bomb']:
                    map_data['bombs'].append({"pos": {"x": x, "y": y}})
        return map_data

    def _sort_data(self, map_data):
        def contiguous_comparator((x1, y1), (x2, y2)):
            diff = x2-x1 + y2-y1
            if -2 <= diff <= 2:
                return 0
            return diff

        def pos_key(d):
            return (d['pos']['x'], d['pos']['y'])

        map_data['fields'] = OrderedDict(sorted(OrderedDict(map_data['fields']).iteritems(), cmp=contiguous_comparator, key=lambda d: d[0]))
        map_data['gates'] = sorted(map_data['gates'], cmp=contiguous_comparator, key=pos_key)
        map_data['bombs'] = sorted(map_data['bombs'], cmp=contiguous_comparator, key=pos_key)
        return map_data

    def _stringify_keys(self, d):
        new_d = OrderedDict()
        if type(d) == dict:
            for k, v in d.iteritems():
                new_d['%s,%s'%(k[0], k[1])] = v
        if type(d) == OrderedDict:
            for k, v in d.iteritems():
                new_d['%s,%s'%k] = v
        return new_d

    def _format_json(self, map_data):
        map_data['switches'] = self._stringify_keys(map_data['switches'])
        map_data['fields'] = self._stringify_keys(map_data['fields'])
        map_data['portals'] = self._stringify_keys(map_data['portals'])
        data_str = json.dumps(map_data, indent=4, separators=(',', ': '))

        pos_search = re.compile(r'^ {8}\{\n {12}"pos": \{\n {16}("[x,y]": \d+,)\n {16}("[x,y]": \d+)\n {12}}\n {8}}', re.MULTILINE)
        pos_replace = r'        {"pos": {\1 \2}}'

        switch_search = re.compile(r'^ {8}("\d+,\d+": \{)\n {12}("defaultState": "\w+")\n {8}\}', re.MULTILINE)
        switch_replace = r'        \1\2}'

        data_str = re.sub(pos_search, pos_replace, data_str)
        data_str = re.sub(switch_search, switch_replace, data_str)

        return data_str

def main():
    if len(sys.argv) < 2:
        usage()
        return 1

    pngpath = sys.argv[1]

    map_ = Map(pngpath)
    json_data = map_.gen_json()

    sys.stdout.write(json_data)


if '__main__' == __name__:
    main()
    exit(0)
