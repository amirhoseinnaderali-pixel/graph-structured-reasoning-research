from __future__ import annotations
from graph_reasoning_research.types import GraphData
def adjacency(graph):
    a={n:{} for n in graph.nodes}
    for u,v,w in graph.edges: a[u][v]=w; a[v][u]=w
    return a
def weighted_degree(graph): return {n:sum(a.values()) for n,a in adjacency(graph).items()}
def degree_centrality(graph):
    a=adjacency(graph); denom=max(len(graph.nodes)-1,1); return {n:len(neigh)/denom for n,neigh in a.items()}
def pagerank(graph,damping=0.85,iterations=100,tol=1e-12):
    a=adjacency(graph); nodes=graph.nodes
    if not nodes: return {}
    rank={n:1.0/len(nodes) for n in nodes}
    for _ in range(iterations):
        new={n:(1-damping)/len(nodes) for n in nodes}
        for u in nodes:
            denom=sum(max(w,0.0) for w in a[u].values())
            if denom<=0:
                for v in nodes: new[v]+=damping*rank[u]/len(nodes)
            else:
                for v,w in a[u].items(): new[v]+=damping*rank[u]*max(w,0.0)/denom
        if max(abs(new[n]-rank[n]) for n in nodes)<tol: rank=new; break
        rank=new
    return rank
def local_neighborhood_agreement(graph):
    a=adjacency(graph); scores={}
    for u in graph.nodes:
        neigh=set(a[u])
        if len(neigh)<2: scores[u]=0.0; continue
        total=pairs=0
        for v in neigh:
            for w in neigh:
                if v>=w: continue
                pairs+=1; total+=1.0 if v in a.get(w,{}) else 0.0
        scores[u]=total/pairs if pairs else 0.0
    return scores
