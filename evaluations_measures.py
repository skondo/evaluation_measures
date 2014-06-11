#!/usr/bin/python
from numpy import log2
from operator import div, add
from itertools import izip

# rr
def rr(ss):
    for i, s in enumerate(ss):
        i += 1
        if s == True:
            return 1.0 / float(i)
        else:
            pass

# mrr
def mrr(scores):
    result = 0.0
    for i, score in enumerate(scores):
        i += 1
        result  += rr(score)
    return result / i

# DCG (Microsoft version)
def dcg(r, max = 10):
    result = sum([pow(2, rel) / log2((rank + 1) + 1)
        for rank, rel in enumerate(r[:min(len(r), max)])])
    return result

# nDCG
def ndcg(r, arel, max = 10):
    result = dcg(r, max) / dcg(sorted(arel, reverse=True), len(arel))
    return result

# ERR (Expected Reciprocal Rank)
# NOTE: max_grade should be *2*
def err(ranking, max = 10, max_grade=2):
    if max is None:
        max = len(ranking)
    
    ranking = ranking[:min(len(ranking), max)]
    ranking = map(float, ranking)

    result = 0.0
    prob_step_down = 1.0
    
    for rank, rel in enumerate(ranking):
        rank += 1
        utility = (pow(2, rel) - 1) / pow(2, max_grade)
        result += prob_step_down * utility / rank
        prob_step_down *= (1 - utility) 
      
    return result

# session nDCG
def sessionndcg(rs, arel, max = 10):
    result = sum([ndcg(r, arel, max) / log2((rank + 1) + 1)
        for rank, r in enumerate(rs)])
    return result

# session ERR
def sessionerr(rs, max = 10, max_grade = 2):
    result = sum([err(r, max, max_grade) / log2((rank + 1) + 1)
        for rank, r in enumerate(rs)])
    return result

# return a list of session ERRs from session 1 to session k
def sessionerr_list(rs, max = 10):
    result = []
    for i in range(len(rs)):
        result.append(sessionerr(rs[:(i+1)], max))
    return result

def sessionndcg_list(rs, arel, max = 10):
    result = []
    for i in range(len(rs)):
        result.append(sessionndcg(rs[:(i+1)], arel, max))
    return result

def qmeasure(rs, arel):
    irel = sorted(arel, reverse=True)
    cbg = 0.0
    cig = 0.0
    cummurative = 0.0
    for rank, (r, ir) in enumerate(zip(rs, irel)):
        # cig: cummurative ideal gain
        cig += ir

        # bg(r) = g(r) + 1 if g(r) > 0
        if r > 0:
            bg = r + 1.0
            # cbg(r) = g(r) + cbg(r-1)
            cbg += bg
            # cbg(r) / (cig(r) + rank)
            cummurative += cbg / (cig + rank + 1)
        #print cbg, cig
    
    num_rel = len(filter(lambda x: x != 0.0, arel))
    result = cummurative / num_rel
    return result

if __name__ == "__main__":

    r = [0,1,1]
    print rr(r)

    m = [[1, 0, 0, 0, 0 ,0 ],
         [0, 0, 1, 0, 0 ,0 ]]
    print mrr(m)
    
    r = [3,0,2,1,1]
    arel = [3,3,2,3,0,2,1,1,1,1,3,3,5]

    print dcg(r)
    print err(r)
    print ndcg(r,arel)

    rs = [[3,0,2,1,1,2,2,2],[2,1,2,2,3,3,2,3]]
    print sessionerr_list(rs)
    print sessionerr(rs)
    

    r = [3,2,3,0,1,2]
    arel = [3,3,2,3,0,2,1,1,1,1,3,3,5]
    print dcg(r)
    print err(r)
    print ndcg(r,arel)
    
    rs = [[3,0,2,1,1,2,2,2],[2,1,2,2,3,3,2,3]]
    arel = [3,3,2,3,0,2,1,1,1,1,3,3,5]
    print sessionerr(rs)
    print sessionndcg(rs,arel)
    print sessionndcg_list(rs,arel)

    rs = [0,0,0,0,1] + [0] * 995
    arel = [1,1,1,1,1] + [0] * 995
    print qmeasure(rs, arel)
