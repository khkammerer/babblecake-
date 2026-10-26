from lib import *
import pickle, collections, itertools, random
syn=pickle.load(open('syn.pkl','rb'))
def lev(a,b):
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]
        for j,cb in enumerate(b,1):
            cur.append(min(prev[j]+1,cur[j-1]+1,prev[j-1]+(ca!=cb)))
        prev=cur
    return prev[-1]
def similar(a,b):
    A,B=base(a),base(b)
    if min(len(A),len(B))<4 or A[0]!=B[0]: return False
    d=lev(A,B)
    return d<=3 and d/max(len(A),len(B))<=0.34 and (d<2 or min(len(A),len(B))>=5)
def pairs():
    """yield (w1,l1,w2,l2,pos) for translation pairs that are spelled alike"""
    seen=set()
    for sid,d in syn.items():
        pos=sid[-1]
        for l1,l2 in (('en','es'),('en','fr'),('es','fr')):
            if l1 in d and l2 in d:
                for a in d[l1]:
                    if not re.fullmatch(r'[^\W\d_]+',a): continue
                    for b in d[l2]:
                        if not re.fullmatch(r'[^\W\d_]+',b): continue
                        if (a,l1,b,l2,pos) in seen: continue
                        if similar(a,b): seen.add((a,l1,b,l2,pos)); yield (a,l1,b,l2,pos)
if __name__=='__main__':
    P=list(pairs()); print(len(P))
    random.seed(3)
    for p in random.sample(P,40): print(p)
    ex=[p for p in P if p[0] in ('alert','antenna','internal','linear','lateral','retina','talent','latent','elite','pelican','canine')]
    for p in ex: print(p)
