# display.py — draws Aurelius screens on the e-ink display
from epd_2in9 import EPD_2in9_Landscape
import lists

W, H = 296, 128
BLACK, WHITE = 0x00, 0xff
HEADER_H = 16
ROW_H = 14
TOP_Y = HEADER_H + 2
ROWS = (H - TOP_Y) // ROW_H      # 7 visible items
MAX_CHARS = (W - 30) // 8        # characters that fit after the checkbox
FULL_EVERY = 10                  # full refresh every N updates (clears ghosting)

epd = EPD_2in9_Landscape()
_count = 0     # updates since last full refresh
_top = 0       # index of first visible item (scroll position)

def _fit(text, n):
    return text if len(text) <= n else text[:n - 2] + ".."

def _header(title, right):
    epd.fill_rect(0, 0, W, HEADER_H, BLACK)
    epd.text(_fit(title, 28), 4, 4, WHITE)
    epd.text(right, W - 4 - 8 * len(right), 4, WHITE)

def _row(y, item, selected):
    fg = WHITE if selected else BLACK
    if selected:
        epd.fill_rect(0, y, W - 6, ROW_H, BLACK)   # highlight bar
    epd.rect(6, y + 3, 8, 8, fg)                   # checkbox
    if item["done"]:
        epd.fill_rect(8, y + 5, 4, 4, fg)          # filled = done
    text = _fit(item["text"], MAX_CHARS)
    epd.text(text, 22, y + 3, fg)
    if item["done"]:
        epd.hline(22, y + 7, 8 * len(text), fg)    # strike-through

def _scrollbar(n):
    if n <= ROWS:
        return
    track = H - TOP_Y
    size = max(6, track * ROWS // n)
    y = TOP_Y + (track - size) * _top // (n - ROWS)
    epd.fill_rect(W - 3, y, 3, size, BLACK)

def _push(full):
    global _count
    if full or _count == 0 or _count >= FULL_EVERY:
        epd.init()
        epd.display_Base(epd.buffer)
        _count = 1
    else:
        epd.display_Partial(epd.buffer)
        _count += 1

def draw_list(selected=0, full=False):
    global _top
    items = lists.items()
    n = len(items)
    if selected < _top:
        _top = selected
    elif selected >= _top + ROWS:
        _top = selected - ROWS + 1
    _top = max(0, min(_top, n - ROWS))

    epd.fill(WHITE)
    done = sum(1 for it in items if it["done"])
    _header(lists.current_name(), "%d/%d" % (done, n))
    if n == 0:
        epd.text("Empty list", 22, TOP_Y + 3, BLACK)
    for i in range(_top, min(_top + ROWS, n)):
        _row(TOP_Y + (i - _top) * ROW_H, items[i], i == selected)
    _scrollbar(n)
    _push(full)

def sleep():
    global _count
    epd.sleep()
    _count = 0     # next draw wakes it with a full refresh
