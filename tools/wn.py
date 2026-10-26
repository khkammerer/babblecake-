# Build {synset_id: {lang: set(lemmas)}} from Princeton WordNet (en) + OMW (es: MCR, fr: WOLF)
from lib import *
import collections, pickle
syn=collections.defaultdict(lambda: collections.defaultdict(set))
def clean(w): return nfc(w.replace('_',' ').lower())
for pos,ch in (('noun','n'),('verb','v'),('adj','a'),('adv','r')):
    for line in open(f'{W}/omw/wn/wordnet/data.{pos}',encoding='utf8'):
        if line.startswith('  '): continue
        p=line.split(' ')
        off,ss=p[0],p[2]; n=int(p[3],16)
        ss='a' if ss=='s' else ss
        for i in range(n):
            syn[off+'-'+ss]['en'].add(clean(p[4+2*i]))
for lang,f,key in (('es',f'{W}/omw/omw/omw-1.4/mcr/wn-data-spa.tab','lemma'),('fr',f'{W}/omw/omw/omw-1.4/fra/wn-data-fra.tab','fra:lemma')):
    for line in open(f,encoding='utf8'):
        if line.startswith('#'): continue
        p=line.rstrip('\n').split('\t')
        if len(p)<3 or p[1]!=key: continue
        syn[p[0]][lang].add(clean(p[2]))
syn={k:{l:v for l,v in d.items()} for k,d in syn.items()}
print(len(syn), sum('en' in d for d in syn.values()), sum('es' in d for d in syn.values()), sum('fr' in d for d in syn.values()))
pickle.dump(syn,open('syn.pkl','wb'))
