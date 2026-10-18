# screensaver.py — "plaque" sleep screen: big AURELIUS on a black band,
# faded tiled background. Drawn into the display buffer; caller pushes it.
import framebuf

W, H = 296, 128
BLACK, WHITE = 0x00, 0xff

_tb = bytearray(64)                                   # 64x8 scratch: one 8-char word
_tf = framebuf.FrameBuffer(_tb, 64, 8, framebuf.MONO_HLSB)

def _big(epd, s, x, y, sx, sy, c):
    # built-in 8x8 font, each pixel scaled to an sx-by-sy block
    _tf.fill(0)
    _tf.text(s, 0, 0, 1)
    for py in range(8):
        for px in range(8 * len(s)):
            if _tf.pixel(px, py):
                epd.fill_rect(x + px * sx, y + py * sy, sx, sy, c)

def _tile(epd, word, shift):
    # repeat word across every text row, each row slid left by `shift` px
    word += " "
    n = 8 * len(word)
    for r, y in enumerate(range(0, H, 8)):
        x = -((r * shift) % n)
        while x < W:
            epd.text(word, x, y, BLACK)
            x += n

def _dither(epd, y0, y1):
    # checkerboard mask: every other pixel to white (50% grey look)
    for y in range(y0, y1):
        for x in range(y & 1, W, 2):
            epd.pixel(x, y, WHITE)

def draw(epd):
    epd.fill(WHITE)
    _tile(epd, "AURELIUS", 36)
    _dither(epd, 0, 38)
    _dither(epd, 90, H)
    epd.fill_rect(0, 38, W, 52, BLACK)                # the band
    epd.hline(0, 41, W, WHITE)                        # inner rules
    epd.hline(0, 86, W, WHITE)
    _big(epd, "AURELIUS", 20, 48, 4, 4, WHITE)        # 256x32, centred
