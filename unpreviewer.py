#!/usr/bin/env python
"""
unpreviewer

Take a preview of a TagPro map and turn it into a source
PNG file.  png2json can then be used to init the JSON.
"""
from __future__ import division

import cgi
import cStringIO
import json
from os import path
from hashlib import md5
import posixpath
import sys
import urlparse
import urllib

from PIL import Image, ImageDraw, ImageChops

from util import NoIndent, TagProEncoder

TILESIZE = 40


def usage():
    print 'Usage: {} PREVIEW PNG JSON'.format(sys.argv[0])

class Map():
    """A preview generator for tagpro."""

    tiles = Image.open('tiles.png')
    speedpad = Image.open('speedpad.png')
    portal = Image.open('portal.png')
    BG, WALL, TILE, SPIKE, BUTTON, POWERUP_TP, POWERUP_JJ, POWERUP_RB,\
    GATE_OFF, GATE_ON, GATE_RED, GATE_BLUE, BLUE, RED, BOOST, BOMB,\
    BLUETILE, REDTILE, PORTAL, REDSPAWN, BLUESPAWN = range(21)
    gate_defaults = {
        GATE_OFF: "off",
        GATE_ON: "on",
        GATE_RED: "red",
        GATE_BLUE: "blue"
    }
    colormap = {
        BG: (0, 0, 0),
        WALL: (120, 120, 120),
        TILE: (212, 212, 212),
        SPIKE: (55, 55, 55),
        BUTTON: (185, 122, 87),
        POWERUP_TP: (0, 255, 0),
        POWERUP_JJ: (0, 255, 0),
        POWERUP_RB: (0, 255, 0),
        GATE_OFF: (0, 117, 0),
        GATE_ON: (0, 117, 0),
        GATE_RED: (0, 117, 0),
        GATE_BLUE: (0, 117, 0),
        BLUE: (0, 0, 255),
        RED: (255, 0, 0),
        BOOST: (255, 255, 0),
        BOMB: (255, 128, 0),
        BLUETILE: (187, 184, 221),
        REDTILE: (220, 186, 186),
        PORTAL: (202, 192, 0),
        REDSPAWN: (155, 0, 0),
        BLUESPAWN: (0, 0, 155)
    }
    tilemap = [
        [WALL, None, WALL,   WALL,     WALL, WALL, WALL,      None,    RED,     BLUE,    None],
        [None, None, WALL,   REDTILE,  WALL, None, WALL,      None,    None,    None,    GATE_OFF],
        [WALL, None, TILE,   BLUETILE, WALL, None, REDSPAWN,  None,    None,    None,    GATE_ON],
        [WALL, None, SPIKE,  None,     WALL, None, BLUESPAWN, WALL,    None,    None,    GATE_RED],
        [WALL, WALL, WALL,   WALL,     WALL, WALL, WALL,      WALL,    None,    None,    GATE_BLUE],
        [WALL, None, BUTTON, None,     WALL, BOMB, BOMB,      WALL,    None,    None,    None],
        [WALL, None, None,   None,     WALL, None, None,      None,    WALL,    WALL,    None],
        [None, None, WALL,   None,     WALL, None, WALL,      None,    None,    None,    None],
        [None, None, WALL,   WALL,     WALL, WALL, WALL,      POWERUP_TP, POWERUP_JJ, POWERUP_RB, None]
    ]
    json = {
            "info": {
                "name": "Map Name Here",
                "author": "Your Name Here"
            },
            "switches": {},
            "fields": {},
            "marsballs": [],
            "portals": {},
        }


    def __init__(self, previewpath, pngpath=None, jsonpath=None):
        pfilename = None
        if 'http' in previewpath:
            presponse = urllib.urlopen(previewpath)
            try:
                _, pparams = presponse.headers.get('Content-Disposition', '')
                pfilename = pparams['filename']
            except ValueError:
                ppath = urlparse.urlsplit(previewpath).path
                pfilename = posixpath.basename(ppath)
            pfile = cStringIO.StringIO(presponse.read())
            preview = Image.open(pfile)
        else:
            preview = Image.open(previewpath)
        self.preview = preview
        self.pixels = preview.load()

        if pngpath is None:
            if pfilename is not None:
                preview_name = path.splitext(pfilename)[0]
                self.pngpath = ".".join([preview_name, "png"])
            else:
                preview_dir = path.dirname(previewpath)
                preview_name = path.splitext(path.basename(previewpath))[0]
                self.pngpath = path.join(preview_dir, ".".join([preview_name, "png"]))
        else:
            self.pngpath = pngpath

        if jsonpath is None:
            png_dir = path.dirname(self.pngpath)
            png_name = path.splitext(path.basename(self.pngpath))[0]
            print png_name, self.pngpath, path.splitext(path.basename(self.pngpath))
            self.jsonpath = path.join(png_dir, ".".join([png_name, "json"]))
        else:
            self.jsonpath = jsonpath

        self.json['info']['name'] = path.splitext(path.basename(self.pngpath))[0]
        self.json['info']['author'] = "Generated from %s" % previewpath
        self.init_tile_crops()

    def get_floor(self):
        return self.tiles.crop((
            2*TILESIZE, 2*TILESIZE,
            2*TILESIZE + TILESIZE,2*TILESIZE+TILESIZE))

    def get_hash(self, im):
        return md5(im.tostring()).hexdigest()

    def init_tile_crops(self):
        self.crops = {}
        for y, row in enumerate(self.tilemap):
            for x, tile in enumerate(row):
                if tile is not None:
                    newtile = self.get_floor()
                    crop = self.tiles.crop((
                        x*TILESIZE, y*TILESIZE,
                        x*TILESIZE + TILESIZE, y*TILESIZE + TILESIZE))
                    newtile.paste(crop, (0,0), crop)
                    self.crops[self.get_hash(newtile)] = tile
        speedpad = self.get_floor()
        crop = self.speedpad.crop((0, 0, TILESIZE, TILESIZE))
        speedpad.paste(crop, (0,0), crop)
        portal = self.get_floor()
        crop = self.portal.crop((0, 0, TILESIZE, TILESIZE))
        portal.paste(crop, (0,0), crop)

        self.crops.update({
            self.get_hash(speedpad): self.BOOST,
            self.get_hash(portal): self.PORTAL})

    def undraw(self, tile):
        return self.crops.get(self.get_hash(tile), self.BG)

    def _undraw_all(self):
        for i in range(self.max_x):
            for j in range(self.max_y):
                tile = self.preview.crop((
                    i * TILESIZE, j * TILESIZE,
                    i * TILESIZE + TILESIZE, j * TILESIZE + TILESIZE))
                tile_type = self.undraw(tile)
                try:
                    self.png.putpixel((i, j), self.colormap[tile_type])
                    self.update_json((i, j), tile_type)
                except IndexError, e:
                    print e, i, j

    def update_json(self, (x, y), tile_type):
        key = "%i,%i" % (x, y)
        if tile_type == self.BUTTON:
            self.json['switches'][key] = {"toggle": [NoIndent({"pos": {'x': None, 'y': None}})]}
        if self.GATE_OFF <= tile_type <= self.GATE_BLUE:
            self.json['fields'][key] = NoIndent({"defaultState": self.gate_defaults[tile_type]})
        if tile_type == self.PORTAL:
            self.json['portals'][key] = NoIndent({"destination": {"x": None, "y": None}, "cooldown": None})

    def get_json(self):
        return json.dumps(self.json, indent=4, cls=TagProEncoder, separators=(',', ': '))

    def write_png(self):
        fp = open(self.pngpath, 'wb')
        self.png.save(fp, 'PNG')
        fp.close()

    def write_json(self):
        fp = open(self.jsonpath, 'wb')
        fp.write(self.get_json())
        fp.close()

    def unpreview(self):
        preview_max_x, preview_max_y = self.preview.size
        self.max_x, self.max_y = png_max_x, png_max_y = int(preview_max_x/TILESIZE), int(preview_max_y/TILESIZE)
        self.png = Image.new('RGBA', (png_max_x, png_max_y))
        self._undraw_all()


def main():
    if len(sys.argv) < 2:
        usage()
        return 1

    previewpath = sys.argv[1]
    jsonpath = (sys.argv[2] if len(sys.argv) > 2 else None)

    map_ = Map(previewpath, jsonpath)
    map_.unpreview()
    map_.write_png()
    map_.write_json()


if '__main__' == __name__:
    status = main()
    sys.exit(status)
