import re, unicodedata, json, os
W='/tmp/claude-0/work'
def nfc(s): return unicodedata.normalize('NFC',s)
def base(s): return ''.join(c for c in unicodedata.normalize('NFD',s) if not unicodedata.combining(c))
# characters the game's long-press accent popup can type
ACC={'a':'àáâä','e':'éèêë','i':'îïíì','o':'ôóöò','u':'ùúûü','c':'ç','n':'ñ','y':'ÿ'}
TYPABLE=set('abcdefghijklmnopqrstuvwxyz')|set(''.join(ACC.values()))
def load(lang):
    path={'en':f'{W}/en/enable1.txt','es':f'{W}/es/expanded.txt','fr':f'{W}/fr/expanded.txt'}[lang]
    out=set()
    for w in open(path,encoding='utf8').read().split('\n'):
        w=nfc(w.strip())
        if len(w)<3: continue
        if not re.fullmatch(r'[a-zà-ÿ]+',w): continue
        if not all(c in TYPABLE for c in w): continue
        out.add(w)
    return out
def candidates(words,letters,center):
    L=set(letters)
    return {w for w in words if center in base(w) and set(base(w))<=L}
