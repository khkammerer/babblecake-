"""Build the PUZZLES data for babblecake from the full word lists.

Pipeline:  word lists -> letter-set filter -> offensive-word filter -> cognate links -> puzzle JSON
"""
from lib import *
from cog import pairs
import collections, json, random, subprocess, sys

LANGS = ('en', 'es', 'fr')
STEP = 15

# (letters, center, outer-letter order for the board)
ORIGINAL = [
    ('aeilnrt', 'e', 'ailnrt'),
    ('aeilnot', 't', 'ilnoae'),
    ('aceilnp', 'a', 'npceil'),
    ('aelnost', 't', 'aelnos'),
]
NEW = [x for x in sys.argv[1].split(',')] if len(sys.argv) > 1 and sys.argv[1] else []
SETS = list(ORIGINAL)
rng = random.Random(2026)
for s in NEW:
    letters, center = s.split(':')
    outer = [c for c in letters if c != center]
    rng.shuffle(outer)
    SETS.append((letters, center, ''.join(outer)))

# ---------------------------------------------------------------- offensive words
def read_ldnoobw(l):
    return {nfc(x.strip().lower()) for x in open(f'{W}/bad/{l}.txt', encoding='utf8') if x.strip() and ' ' not in x.strip()}

# Words on the open LDNOOBW list that are ordinary, clinical or harmless, so we keep them.
ALLOW = {
 'en': set('''anus bondage butt domination escort eunuch fecal genitals incest intercourse nipple nipples nude nudity
              panties panty penis rape raping rapist rectum scat semen sex sexual sexuality sexually sexy suck sucks swastika
              topless undressing vagina vulva clitoris ejaculation erotic erotism lovemaking playboy sadism voyeur
              strappado bastinado snatch escort hardcore domination figging grope spastic'''.split()),
 'es': set('''asesinato asno concha drogas esperma heroína infierno martillo maldito nazi orina pervertido pinche pis racista
              sexo vulva idiota imbécil sádico travesti prostituta'''.split()),
 'fr': set('''baiser bander bourré bourrée clitoris con folle gerbe gerber gueule pipi tanche suce péter ramoner
              jouir salaud'''.split()),
}
# Extra offensive words we add (slurs, profanity, vulgar slang), with their forms.
EXTRA = {
 'en': set('''arse arsehole bugger bollock wanker wank prick chink gook wop dago kraut nigga niggas retard retarded tranny
              shemale homo lesbo dyke paki polack spaz goddamn jackass dumbass dipshit horseshit piss pissed turd skank
              fuckin fucker fuckers fucked mofo dyke dykes negress tittie titties shittiest shittier caca'''.split()),
 'es': set('''puta puto putada joder jodido jodida cojones cabrona hijoputa maricas mariconada zorra zorras pajero pinga chingar
              chingada chinga pichula sudaca negrata cagar mierdas polla pollas culo culos coño coños verga vergas follar folla
              pendeja pendejos cabrones putos putas capullo capullos mamón gilipollas tontopollas teta tetas meo mea'''.split()),
 'fr': set('''putain pute putes merde merdes salope salopes salopard enculer niquer nique foutre pédé pédale couillon couillons
              chiant chiante chiants chiantes connerie conneries pétasse garce fiotte négro bougnoule youpin bamboula
              branleur enfoirés enfoirées merder merdier merdiers merdé merdée merdés merdées cacaille'''.split()),
}
# Forms of blocked English words (no stemmer used for English)
def en_forms(b):
    out = {b, b+'s', b+'es', b+'ed', b+'ing', b+'er', b+'ers', b+'y', b+'ie', b+'ies'}
    if b[-1] not in 'aeiouy' and len(b) > 2:
        out |= {b+b[-1]+'ed', b+b[-1]+'ing', b+b[-1]+'er', b+b[-1]+'ers', b+b[-1]+'y'}
    if b.endswith('y'): out |= {b[:-1]+'ies', b[:-1]+'ied'}
    if b.endswith('e'): out |= {b[:-1]+'ing', b[:-1]+'ed', b[:-1]+'er'}
    return out

def blocklist(l):
    return (read_ldnoobw(l) - ALLOW[l]) | EXTRA[l]

def stems(l, words):
    """Root words ('stems') for every word, using the Hunspell tool and the same dictionary."""
    d = {'es': f'{W}/es/package/index', 'fr': f'{W}/fr/package/index'}[l]
    inp = '\n'.join(sorted(words)) + '\n'
    out = subprocess.run(['hunspell', '-d', d, '-i', 'UTF-8', '-s'], input=inp, capture_output=True, text=True, encoding='utf8').stdout
    m = collections.defaultdict(set)
    for line in out.split('\n'):
        p = line.split(' ')
        if len(p) == 2: m[nfc(p[0])].add(nfc(p[1].lower()))
    return m

# ---------------------------------------------------------------- word lists
# Consonant pairs a Spanish / French word can start with. Anything else is an abbreviation (tpo, rte, ppal...).
ONSETS = {
 'es': set('pr pl br bl tr dr cr cl gr gl fr fl ch ll ps pn pt gn kr kl'.split()),
 'fr': set('pr pl br bl tr dr cr cl gr gl fr fl ch ph th sc sp st sk sl sm sn ps pn pt tm gn kr kl vr tw sw sq sh'.split()),
}
def junk(w, l):
    b = base(w)
    if not any(c in 'aeiouy' for c in b) or re.search(r'(.)\1\1', b): return True
    return l != 'en' and len(b) > 1 and b[0] not in 'aeiouy' and b[1] not in 'aeiouy' and b[:2] not in ONSETS[l]

ALL = {l: {w for w in load(l) if not junk(w, l)} for l in LANGS}
ALL['en'] |= {'entrail'}   # in the original hand-made list, missing from ENABLE
cand = {}   # (letters,center) -> {lang: set(words)}
for L, c, _ in SETS:
    cand[(L, c)] = {l: candidates(ALL[l], L, c) for l in LANGS}

removed = {l: collections.defaultdict(set) for l in LANGS}
STEMS = {}
for l in ('es', 'fr'):
    allw = set().union(*[cand[k][l] for k in cand])
    STEMS[l] = stems(l, allw)
BLOCK = {l: blocklist(l) for l in LANGS}
BLOCKFORMS_EN = set().union(*[en_forms(b) for b in BLOCK['en']])
# a few English words that look like a blocked form but are ordinary
EN_OK = set('''ass asses assess hell bitter bitten bites bitty cocky cockle cocoa cocks hens titer titers titan
               scatter scattered scatty coony cumin cummer fagged fagot fagoting spic spice spicy sucker suckers suckered
               hookers hookey hooker horny hornier hornet hornets analyst titter titters tittered'''.split())

def is_bad(l, w):
    if l == 'en':
        return w in BLOCKFORMS_EN and w not in EN_OK and w not in {'ass'} or w in {'ass', 'asses'} and False
    return w in BLOCK[l] or bool(STEMS[l].get(w, set()) & BLOCK[l])

DICT = {}
for (L, c), per in cand.items():
    d = collections.defaultdict(list)
    for l in LANGS:
        for w in sorted(per[l]):
            if is_bad(l, w): removed[l][(L, c)].add(w); continue
            d[w].append(l)
    DICT[(L, c)] = dict(d)

# ---------------------------------------------------------------- cognates
# 1. Translation pairs from WordNet that are spelled alike (cog.py), plus their plural / feminine forms.
# 2. "Triangulation": if a meaning is confirmed in two languages, a headword in the third language that is
#    spelled very close to both counts too (this is how alerta joins alert + alerte).
SYNPAIRS = list(pairs())
def plural(w, l):
    if l == 'en': return w+'es' if re.search(r'(s|x|z|ch|sh)$', w) else w[:-1]+'ies' if re.search(r'[^aeiou]y$', w) else w+'s'
    if l == 'es': return w+'s' if w[-1] in 'aeiouáéíóú' else w[:-1]+'ces' if w.endswith('z') else w+'es'
    if l == 'fr': return w[:-2]+'aux' if w.endswith('al') else w if re.search(r'[sxz]$', w) else w+'s'
def forms(w, l, pos):
    """[(spelling, number)] - the word plus its gender / plural forms where that makes sense."""
    out = [(w, 's')]
    if l == 'es' and pos == 'a' and w.endswith('o'): out += [(w[:-1]+'a', 's'), (w+'s', 'p'), (w[:-1]+'as', 'p')]
    elif l == 'fr' and pos == 'a' and not w.endswith('e'): out += [(w+'e', 's'), (plural(w, l), 'p'), (plural(w+'e', l), 'p')]
    elif pos == 'n' or (pos == 'a' and l != 'en'): out.append((plural(w, l), 'p'))
    return out

def strict(a, b):
    A, B = base(a), base(b)
    if min(len(A), len(B)) < 4 or A[0] != B[0]: return False
    dd = lev(A, B)
    return dd <= 2 and dd / max(len(A), len(B)) <= 0.25
from cog import lev

def cognate_groups(d):
    """Components of (spelling, language) nodes that are translations of each other. Returns lists of spellings."""
    parent = {}
    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    def union(x, y): parent[find(x)] = find(y)
    for a, l1, b, l2, pos in SYNPAIRS:
        for x, nx in forms(a, l1, pos):
            if l1 not in d.get(x, ()): continue
            for y, ny in forms(b, l2, pos):
                if nx == ny and x != y and l2 in d.get(y, ()): union((x, l1), (y, l2))
    comps = collections.defaultdict(set)
    for n in list(parent): comps[find(n)].add(n)
    comps = [c for c in comps.values() if len({w for w, _ in c}) > 1]
    # the "alert / alerte / alerta" pattern: two languages linked by a translation, the third one is spelled the
    # same way with its usual ending (en X, fr X+e, es X+a) - add it only if it is a headword in the word list
    for c in comps:
        sp = collections.defaultdict(set)
        for w, l in c: sp[l].add(w)
        if len(sp) != 2: continue
        add = []
        if 'en' in sp and 'fr' in sp:
            add += [(w + 'a', 'es') for w in sp['en'] if w + 'e' in sp['fr']]
        if 'en' in sp and 'es' in sp:
            add += [(w + 'e', 'fr') for w in sp['en'] if w + 'a' in sp['es']]
        if 'es' in sp and 'fr' in sp:
            add += [(w[:-1], 'en') for w in sp['es'] if w.endswith('a') and w[:-1] + 'e' in sp['fr']]
        for z, l in add:
            if l in d.get(z, ()) and (l == 'en' or z in STEMS[l].get(z, ())): c.add((z, l))
    # merge components that now overlap
    merged = []
    for c in comps:
        for m in merged:
            if m & c: m |= c; break
        else: merged.append(set(c))
    return [{w for w, _ in c} for c in merged if len({w for w, _ in c}) > 1]

def lp(w): return 10 if len(w) > 7 else len(w) - 2

PUZZLES = []
for n, (L, c, outer) in enumerate(SETS, 1):
    d = DICT[(L, c)]
    comps = cognate_groups(d)
    cousin = sorted(set().union(*comps)) if comps else []
    cs = set(cousin)
    inc = set(cousin)
    groups = []
    for comp in sorted(comps, key=lambda s: (-len(s), sorted(s)[0])):
        items = sorted(comp, key=lambda w: (LANGS.index(d[w][0]), base(w), w))
        groups.append([[w, d[w]] for w in items])
    singles = sorted((w for w in d if len(d[w]) > 1 and w not in cs), key=lambda w: (base(w), w))
    groups += [[[w, d[w]]] for w in singles]
    pans = sorted(w for w in d if set(base(w)) == set(L))
    top = sum(lp(w) + (len(d[w]) - 1) + (1 if w in cs else 0) for w in d)
    PUZZLES.append({'id': f'{L}-{c}', 'num': n, 'center': c, 'outer': list(outer), 'letters': sorted(L),
                    'words': dict(sorted(d.items(), key=lambda kv: (LANGS.index(kv[1][0]), base(kv[0]), kv[0]))),
                    'cousin': cousin, 'groups': groups, 'top': top, 'pangrams': pans})

# ---------------------------------------------------------------- report
def report():
    for p in PUZZLES:
        d = p['words']; cs = set(p['cousin'])
        per = {}
        for l in LANGS:
            ws = [w for w in d if l in d[w]]
            per[l] = (len(ws), sum(lp(w) + (1 if w in cs else 0) for w in ws), sum(1 for w in ws if set(base(w)) == set(p['letters'])))
        ngroups = sum(1 for g in p['groups'] if len(g) > 1)
        print(p['id'], 'words', len(d), 'cognate groups', ngroups, 'cognate words', len(cs), 'top', p['top'],
              {l: f'{per[l][0]}w/{per[l][1]}pts/{per[l][2]}pan' for l in LANGS}, 'bad removed', {l: len(removed[l][(p["letters"] and ''.join(p["letters"]), p["center"])]) for l in LANGS})
if __name__ == '__main__':
    report()
    json.dump(PUZZLES, open(f'{W}/puzzles.json', 'w', ensure_ascii=False) if False else open(f'{W}/puzzles.json', 'w', encoding='utf8'), ensure_ascii=False, separators=(',', ':'))
    json.dump({l: {f'{k[0]}-{k[1]}': sorted(v) for k, v in removed[l].items()} for l in LANGS}, open(f'{W}/removed.json', 'w', encoding='utf8'), ensure_ascii=False)
