from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from graph_reasoning_research.types import GraphData
@dataclass(frozen=True)
class GraphBuilder:
    name:str; threshold:float|None=None; k:int|None=None; weighted:bool=True
    def build(self,node_ids:tuple[str,...],similarity:np.ndarray)->GraphData:
        n=len(node_ids)
        if similarity.shape!=(n,n): raise ValueError('similarity shape must match node count')
        edges=set()
        if self.name=='threshold':
            if self.threshold is None: raise ValueError('threshold graph requires threshold')
            for i in range(n):
                for j in range(i+1,n):
                    if similarity[i,j]>=self.threshold: edges.add((i,j))
        elif self.name=='knn':
            if self.k is None or self.k<1: raise ValueError('kNN graph requires k >= 1')
            for i in range(n):
                order=np.argsort(-similarity[i]); selected=0
                for j in order:
                    j=int(j)
                    if j==i: continue
                    a,b=sorted((i,j))
                    if (a,b) not in edges: edges.add((a,b)); selected+=1
                    if selected>=self.k: break
        else: raise ValueError(f'unknown graph builder: {self.name}')
        materialized=[]
        for i,j in sorted(edges): materialized.append((node_ids[i],node_ids[j],float(similarity[i,j]) if self.weighted else 1.0))
        return GraphData(node_ids,tuple(materialized),self.weighted,self.name,self.__dict__.copy())
def threshold_graph(node_ids,similarity,threshold,weighted): return GraphBuilder('threshold',threshold=threshold,weighted=weighted).build(node_ids,similarity)
def knn_graph(node_ids,similarity,k,weighted): return GraphBuilder('knn',k=k,weighted=weighted).build(node_ids,similarity)
