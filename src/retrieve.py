import pickle
import sys
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sentence_transformers import SentenceTransformer

def build_index(metadata):
    sentence_index = dict()

    for idx, m in enumerate(metadata):
        if m['link'] not in sentence_index:
            sentence_index[m['link']] = {m['pos']: idx}
        else:
            sentence_index[m['link']].update({m['pos']: idx})

    return sentence_index

if __name__ == "__main__":
    with open(sys.argv[1], "rb") as f:
        metadata = pickle.load(f)

    sentence_index = build_index(metadata)
    embeddings = np.array([d['embedding'] for d in metadata])

    neighbors = NearestNeighbors(n_neighbors=10, algorithm='brute', metric='cosine').fit(embeddings)
    smodel = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

    inp = smodel.encode(['how do I read more books?'])
    scores, idxs = neighbors.kneighbors(inp)

    print("\n\n".join([metadata[i]['link'] + ":   " + " ".join([metadata[sentence_index[metadata[i]['link']][b]]['text'] for b in metadata[i]['before'] if b > 0])
                       + metadata[i]['text']
                        + " ".join([metadata[sentence_index[metadata[i]['link']][a]]['text'] for a in metadata[i]['after'] if a > 0])
                        for i in idxs[0]]))
