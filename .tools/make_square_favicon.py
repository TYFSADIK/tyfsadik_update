#!/usr/bin/env python3
"""Build Google-eligible square favicons from the original orange brand mark.

The source favicon.png is 36x64 (portrait). Google Search requires a square
icon at a multiple of 48x48. This script:
  1. decodes the original PNG pixel-exactly,
  2. pads it with the brand orange on the left/right to a square 64x64,
  3. nearest-neighbor upscales to 48/192/512 (and 180 for apple-touch-icon),
     keeping the pixel-art edges perfectly crisp,
  4. writes proper PNG files. Original favicon.png is never modified.
"""
import struct
import zlib

def read_png(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos = 8
    idat = b''
    width = height = None
    bitdepth = colortype = None
    while pos < len(data):
        length = struct.unpack('>I', data[pos:pos+4])[0]
        ctype = data[pos+4:pos+8]
        chunk = data[pos+8:pos+8+length]
        if ctype == b'IHDR':
            width, height, bitdepth, colortype = struct.unpack('>IIBB', chunk[:10])
        elif ctype == b'IDAT':
            idat += chunk
        pos += 12 + length
    assert bitdepth == 8 and colortype == 6, f'expected RGBA8, got bd={bitdepth} ct={colortype}'
    raw = zlib.decompress(idat)
    stride = width * 4
    px = bytearray(width * height * 4)
    prev = bytearray(stride)
    ppos = 0
    for y in range(height):
        f = raw[ppos]; ppos += 1
        line = bytearray(raw[ppos:ppos+stride]); ppos += stride
        if f == 1:
            for i in range(4, stride): line[i] = (line[i] + line[i-4]) & 0xFF
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i-4] if i >= 4 else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i-4] if i >= 4 else 0
                b = prev[i]
                c = prev[i-4] if i >= 4 else 0
                p_ = a + b - c
                pa, pb, pc = abs(p_-a), abs(p_-b), abs(p_-c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        px[y*stride:(y+1)*stride] = line
        prev = line
    return width, height, bytes(px)

def write_png(path, width, height, px):
    raw = b''.join(b'\x00' + px[y*width*4:(y+1)*width*4] for y in range(height))
    def chunk(ctype, payload):
        c = struct.pack('>I', len(payload)) + ctype + payload
        return c + struct.pack('>I', zlib.crc32(ctype + payload) & 0xFFFFFFFF)
    out = b'\x89PNG\r\n\x1a\n'
    out += chunk(b'IHDR', struct.pack('>IIBB', width, height, 8, 6) + b'\x00\x00\x00')
    out += chunk(b'IDAT', zlib.compress(raw, 9))
    out += chunk(b'IEND', b'')
    open(path, 'wb').write(out)

def pad_square(w, h, px, rgba):
    side = max(w, h)
    xoff = (side - w) // 2
    yoff = (side - h) // 2
    out = bytearray(rgba * (side * side))
    for y in range(h):
        src = px[y*w*4:(y+1)*w*4]
        row = (yoff + y) * side * 4 + xoff * 4
        out[row:row+len(src)] = src
    return side, bytes(out)

def upscale(side, px, target):
    if target == side: return px
    out = bytearray(target * target * 4)
    for y in range(target):
        sy = y * side // target
        for x in range(target):
            sx = x * side // target
            si = (sy * side + sx) * 4
            di = (y * target + x) * 4
            out[di:di+4] = px[si:si+4]
    return bytes(out)

w, h, px = read_png('favicon.png')
print(f'source: {w}x{h}')
# brand orange sampled from the corner pixel of the original
orange = px[0:4]
print('background rgba:', list(orange))
side, sq = pad_square(w, h, px, orange)
for name, size in [('favicon-48.png', 48), ('icon-192.png', 192),
                   ('icon-512.png', 512), ('apple-touch-icon.png', 180)]:
    write_png(name, size, size, upscale(side, sq, size))
    print('wrote', name, f'{size}x{size}')
