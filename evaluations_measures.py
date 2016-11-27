# coding: utf-8
#!/usr/bin/python
from numpy import log2
from operator import div, add
from itertools import izip
from types import FunctionType

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
def err(ranking, max = 10, max_grade=3):
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


'''
Risk Sensitive Measure Class
Arguments:
    queries as List
    your_contributed_effectiveness as FunctionType or Dict{query:value} 
    baseline_effectiveness as FunctionType or Dict{query:value}
    
    As for the effectivness functions, an argument is a query and a return value is a score.

Public method:
    get_risk_measure(alfa as Float, option as String)
        alfa is a risk-aversion parameter
        option is a difference/ratio parameter
'''
class RiskSensitiveMeasure():
    def __init__(self, queries, your_contributed_effectiveness, baseline_effectiveness):
        self.queries = queries
        self.your_contributed = your_contributed_effectiveness
        self.baseline = baseline_effectiveness
        self.__hurt_queries = []
        self.__unchanged_queries = []
        self.__improved_queries = []
        self._option = 'difference' # default
    
    def _calc_delta(self, query):
        ret = 0.0 # default        
        
        if isinstance(self.your_contributed, FunctionType) and isinstance(self.baseline, FunctionType):
            if self._option is 'difference':
                ret = self.your_contributed(query) - self.baseline(query)
            else:
                ret = self.your_contributed(query) / self.baseline(query)
        if isinstance(self.your_contributed, dict) and isinstance(self.baseline, dict):
            if query in self.your_contributed and query in self.baseline:
                if self._option is 'difference':
                    ret = self.your_contributed[query] - self.baseline[query]
                else:
                    ret = self.your_contributed[query] / self.baseline[query]
        
        return ret
    
    def _classify_queries(self):
        self.__improved_queries = []
        self.__hurt_queries = []
        self.__unchanged_queries = []
        
        for query in self.queries:
            delta = self._calc_delta(query) 
            if delta > 0:
                self.__improved_queries.append(query)
            elif delta < 0:
                self.__hurt_queries.append(query)
            else:
                # don't use
                self.__unchanged_queries.append(query)
    
    def get_risk_measure(self, alfa, option = None):
        improved_score = 0.0
        hurt_score = 0.0
        if option:
            self._option = option
        else:
            self._option = 'difference'
            
        self._classify_queries()
        for i_query in self.__improved_queries:
            improved_score += self._calc_delta(i_query)
        for h_query in self.__hurt_queries:
            hurt_score += self._calc_delta(h_query)
        
        return (improved_score - (alfa + 1) * hurt_score) / float(len(self.queries))

    #def get_hurt_queries(self):
    #    return self.__hurt_queries
    
    #def get_improved_queries(self):
    #    return self.__improved_queries
    
    #def get_unchanged_queries(self):
    #    return self.__unchanged_queries
    

# for debug
import random
def get_rnd(query):
    return random.random()



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
    
    print '\nrisk measure'
    q = ['aa', 'bb', 'cc', 'dd', 'ee', 'ff', 'gg']
    contri = {'aa':1.0, 'bb':1.0, 'cc':1.3, 'dd':1.4, 'ee':1.5, 'ff':0.9, 'gg':0.8}
    base = {'aa':2.1, 'bb':1.0, 'cc':0.1, 'dd':0.2, 'ee':0.8, 'ff':1.5, 'gg':1.1}
    rsm = RiskSensitiveMeasure(q, contri, base)
    
    print rsm.get_risk_measure(1.0)
    print rsm.get_risk_measure(1.0, "a")
    print rsm.get_risk_measure(5.0)
    #print rsm.get_risk_measure(5.0, "a")
    
    rsm2 = RiskSensitiveMeasure(q, get_rnd, get_rnd)
    print rsm2.get_risk_measure(3.0)




