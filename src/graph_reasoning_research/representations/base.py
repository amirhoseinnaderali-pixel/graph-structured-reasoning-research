from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
import numpy as np
from graph_reasoning_research.types import CandidateSet, RepresentationBatch
class RepresentationProvider:
    method='abstract'; model_id='UNSET'
    def encode(self,candidate_set:CandidateSet)->RepresentationBatch: raise NotImplementedError
@dataclass
class HashEmbeddingProvider(RepresentationProvider):
    dimension:int=32; model_id:str='mock-hash-embedding-v1'; method:str='hash_embedding'
    def encode(self,candidate_set:CandidateSet)->RepresentationBatch:
        rows=[]
        for text in [c.text for c in candidate_set.candidates]:
            row=np.zeros(self.dimension,dtype=np.float64)
            for token in text.lower().split():
                h=hashlib.sha256(token.encode()).digest(); idx=int.from_bytes(h[:4],'little')%self.dimension; row[idx]+=1.0 if h[4]%2 else -1.0
            norm=np.linalg.norm(row)
            if norm: row/=norm
            rows.append(row)
        mat=np.vstack(rows) if rows else np.empty((0,self.dimension)); config_hash=hashlib.sha256(json.dumps({'dimension':self.dimension},sort_keys=True).encode()).hexdigest(); rep_hash=hashlib.sha256(mat.tobytes()).hexdigest()
        return RepresentationBatch(self.method,self.model_id,config_hash,mat,tuple(c.text for c in candidate_set.candidates),rep_hash)
