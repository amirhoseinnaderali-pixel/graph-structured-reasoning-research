from __future__ import annotations
import numpy as np
def cosine_similarity_matrix(embeddings:np.ndarray)->np.ndarray:
    x=np.asarray(embeddings,dtype=np.float64)
    if x.ndim!=2: raise ValueError('embeddings must be a 2D array')
    norms=np.linalg.norm(x,axis=1,keepdims=True); safe=np.divide(x,np.maximum(norms,1e-12)); sim=safe@safe.T; np.fill_diagonal(sim,1.0); return np.clip(sim,-1.0,1.0)
