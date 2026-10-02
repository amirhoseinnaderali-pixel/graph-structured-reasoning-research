import numpy as np
from graph_reasoning_research.graph.builders import knn_graph, threshold_graph

def test_threshold_weighted_and_unweighted():
    ids=('a','b','c'); s=np.array([[1,.8,.2],[.8,1,.7],[.2,.7,1.]]); g=threshold_graph(ids,s,.75,True); assert g.edges==(('a','b',.8),); g2=threshold_graph(ids,s,.75,False); assert g2.edges==(('a','b',1.0),)

def test_knn_edges_are_deterministic():
    ids=('a','b','c','d'); s=np.array([[1,.9,.8,.1],[.9,1,.2,.1],[.8,.2,1,.7],[.1,.1,.7,1.]]); g=knn_graph(ids,s,2,True); assert len(g.edges)>0; assert g.edges==knn_graph(ids,s,2,True).edges
