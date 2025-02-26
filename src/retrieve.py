import pickle
import sys
import os
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sentence_transformers import SentenceTransformer


def build_index(metadata):
    if os.path.exists("sentence_index.pt"):
        with open("sentence_index.pt", "rb") as f:
            sentence_index = pickle.load(f)

        return sentence_index

    sentence_index = dict()
    for idx, m in enumerate(metadata):
        if m["link"] not in sentence_index:
            sentence_index[m["link"]] = {m["pos"]: idx}
        else:
            sentence_index[m["link"]].update({m["pos"]: idx})

    with open("sentence_index.pt", "wb") as f:
        sentence_index = pickle.dump(sentence_index, f)

    return sentence_index


def retrieve_with_context(metadata, i):
    sentence_index = build_index(metadata)

    return (
        " ".join(
            [
                metadata[sentence_index[metadata[i]["link"]][b]]["text"]
                for b in metadata[i]["before"]
                if b > 0
            ]
        )
        + metadata[i]["text"]
        + " ".join(
            [
                metadata[sentence_index[metadata[i]["link"]][a]]["text"]
                for a in metadata[i]["after"]
                if a > 0
            ]
        )
    )


if __name__ == "__main__":
    with open(sys.argv[1], "rb") as f:
        metadata = pickle.load(f)

    embeddings = np.array([d["embedding"] for d in metadata])

    neighbors = NearestNeighbors(n_neighbors=5, algorithm="brute", metric="cosine").fit(
        embeddings
    )
    smodel = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

    inp = smodel.encode(["how do I read more books?"])
    scores, idxs = neighbors.kneighbors(inp)

    print("\n\n".join([retrieve_with_context(metadata, i) for i in idxs[0]]))
