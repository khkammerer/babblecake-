"""Swap the PUZZLES data inside babblecake.html. Nothing else in the file changes except an invisible credits comment."""
import json, re, sys
SRC = '/home/user/babblecake-/babblecake.html'
OUT = sys.argv[1] if len(sys.argv) > 1 else SRC
CREDITS = open('/tmp/claude-0/work/credits_comment.txt', encoding='utf8').read()

html = open(SRC, encoding='utf8').read()
puzzles = json.load(open('/tmp/claude-0/work/puzzles.json', encoding='utf8'))
data = json.dumps(puzzles, ensure_ascii=False, separators=(', ', ': ') if False else (',', ':'))
assert '</script' not in data

new, n = re.subn(r'const PUZZLES = \[.*?\];\n\(function', lambda m: 'const PUZZLES = ' + data + ';\n(function', html, count=1, flags=re.S)
assert n == 1
if '<!-- WORD LISTS' not in new:
    new = new.replace('<head>\n', '<head>\n' + CREDITS + '\n', 1)
open(OUT, 'w', encoding='utf8').write(new)
print('wrote', OUT, len(new.encode('utf8')) // 1024, 'KB')
