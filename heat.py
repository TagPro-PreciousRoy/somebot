#!/usr/bin/env python

import sys
import json

import heatmap
from PIL import Image, ImageDraw

# remove white from classic color scheme
heatmap.colorschemes.schemes['classic'] = [
(255, 67, 67),
(255, 58, 58),
(255, 48, 48),
(255, 40, 40),
(255, 32, 32),
(255, 26, 26),
(255, 21, 21),
(255, 17, 17),
(255, 14, 14),
(255, 11, 11),
(255, 8, 8),
(255, 6, 6),
(255, 5, 5),
(255, 4, 4),
(255, 2, 2),
(255, 2, 2),
(255, 2, 2),
(255, 1, 1),
(255, 1, 1),
(255, 0, 0),
(255, 0, 0),
(255, 0, 0),
(255, 0, 0),
(255, 0, 0),
(255, 0, 0),
(255, 0, 0),
(255, 0, 0),
(255, 0, 0),
(255, 1, 0),
(255, 4, 0),
(255, 6, 0),
(255, 9, 0),
(255, 13, 0),
(255, 16, 0),
(255, 20, 0),
(255, 24, 0),
(255, 27, 0),
(255, 32, 0),
(255, 36, 0),
(255, 41, 0),
(255, 44, 0),
(255, 50, 0),
(255, 55, 0),
(255, 60, 0),
(255, 65, 0),
(255, 70, 0),
(255, 76, 0),
(255, 82, 0),
(255, 86, 0),
(255, 93, 0),
(255, 98, 0),
(255, 104, 0),
(255, 109, 0),
(255, 115, 0),
(255, 121, 0),
(255, 127, 0),
(255, 133, 0),
(255, 138, 0),
(255, 144, 0),
(255, 150, 0),
(255, 155, 0),
(255, 161, 0),
(255, 167, 0),
(255, 172, 0),
(255, 178, 0),
(255, 183, 0),
(255, 188, 0),
(255, 193, 0),
(255, 198, 0),
(255, 203, 0),
(255, 207, 0),
(255, 212, 0),
(255, 216, 0),
(255, 220, 0),
(255, 224, 0),
(255, 229, 0),
(255, 233, 0),
(255, 235, 0),
(255, 238, 0),
(255, 242, 0),
(255, 245, 0),
(255, 246, 0),
(255, 249, 0),
(255, 251, 0),
(254, 251, 0),
(252, 252, 0),
(250, 252, 1),
(248, 252, 2),
(244, 252, 2),
(241, 252, 3),
(238, 252, 3),
(234, 252, 3),
(231, 252, 4),
(227, 252, 4),
(223, 252, 4),
(219, 252, 5),
(215, 252, 5),
(211, 252, 6),
(206, 252, 7),
(201, 252, 7),
(198, 252, 8),
(193, 251, 8),
(187, 250, 9),
(183, 248, 9),
(178, 247, 9),
(173, 246, 10),
(168, 244, 11),
(164, 242, 11),
(158, 240, 12),
(152, 238, 13),
(147, 237, 14),
(142, 234, 14),
(137, 232, 15),
(131, 230, 15),
(126, 227, 16),
(120, 225, 17),
(115, 223, 18),
(110, 221, 19),
(105, 218, 20),
(100, 216, 21),
(94, 215, 22),
(90, 212, 23),
(85, 210, 24),
(79, 208, 24),
(74, 206, 25),
(70, 203, 26),
(65, 202, 28),
(60, 200, 30),
(55, 198, 31),
(51, 196, 33),
(46, 195, 34),
(42, 192, 35),
(38, 190, 36),
(34, 189, 38),
(30, 188, 39),
(26, 187, 41),
(22, 185, 43),
(19, 184, 44),
(15, 183, 46),
(12, 182, 48),
(10, 181, 50),
(7, 181, 52),
(4, 180, 54),
(2, 180, 56),
(1, 180, 58),
(0, 180, 60),
(0, 180, 62),
(0, 180, 65),
(0, 181, 68),
(0, 182, 70),
(0, 182, 73),
(0, 183, 76),
(0, 184, 78),
(0, 184, 82),
(0, 185, 85),
(0, 186, 89),
(0, 187, 92),
(0, 188, 95),
(0, 190, 99),
(0, 191, 103),
(0, 192, 107),
(0, 194, 110),
(0, 195, 114),
(0, 197, 118),
(0, 199, 121),
(0, 200, 126),
(0, 201, 129),
(0, 203, 134),
(0, 205, 138),
(0, 207, 142),
(0, 208, 146),
(0, 210, 149),
(0, 212, 153),
(0, 214, 158),
(0, 215, 161),
(0, 216, 166),
(0, 219, 171),
(0, 222, 178),
(0, 224, 183),
(0, 226, 189),
(0, 228, 195),
(0, 230, 200),
(0, 232, 206),
(0, 233, 211),
(0, 234, 216),
(0, 234, 221),
(0, 234, 225),
(0, 234, 230),
(0, 234, 233),
(0, 234, 237),
(0, 234, 241),
(0, 234, 244),
(0, 234, 247),
(0, 234, 249),
(0, 234, 252),
(0, 234, 254),
(0, 234, 255),
(0, 232, 255),
(0, 229, 255),
(0, 225, 255),
(0, 221, 255),
(0, 216, 255),
(0, 211, 253),
(0, 206, 251),
(0, 200, 249),
(0, 194, 247),
(0, 188, 244),
(0, 181, 240),
(0, 174, 237),
(0, 166, 233),
(0, 159, 230),
(0, 151, 225),
(0, 144, 220),
(0, 136, 216),
(0, 128, 212),
(0, 121, 208),
(0, 117, 205),
(0, 112, 203),
(0, 108, 200),
(0, 101, 197),
(0, 95, 194),
(0, 90, 191),
(0, 83, 187),
(0, 76, 183),
(0, 70, 179),
(0, 64, 175),
(0, 58, 171),
(0, 53, 167),
(0, 47, 163),
(0, 42, 159),
(0, 37, 154),
(0, 32, 150),
(0, 28, 145),
(0, 25, 140),
(0, 21, 135),
(0, 18, 131),
(0, 15, 126),
(0, 12, 121),
(0, 10, 116),
(1, 8, 112),
(1, 7, 108),
(1, 5, 104),
(1, 5, 99),
(2, 4, 96),
(3, 4, 91),
(4, 5, 89),
(5, 5, 85),
(6, 6, 82),
(7, 7, 80),
(8, 8, 77),
(9, 9, 77),
(11, 11, 77),
(13, 13, 77),
(14, 14, 76),
(16, 16, 74),
(19, 19, 73)
]

def main():
    shift = 20
    splats_file = sys.argv[1]
    map_prev_file = sys.argv[2]
    with open(splats_file) as f:
        splats = json.load(f)

    preview = Image.open(map_prev_file)
    size = preview.size
    pts = [(p['x'] + shift, (size[1] - (p['y'] + shift))) for p in splats]

    hm = heatmap.Heatmap()
    img = hm.heatmap(pts, dotsize=200, size=size, scheme='classic', area=((0, 0), size))
    img.save('classic.png')


if __name__ == '__main__':
    status = main()
    sys.exit(status)
