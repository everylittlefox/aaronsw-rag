import pickle
import sys
import os
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama


SYSTEM_PROMPT = (
    "You are a helpful assistant designed to answer questions solely by referencing "
    "these snippets you found by searching the blog of Aaron Swartz.\n"
    "When generating your answer, follow these guidelines:\n"
    "- For each statement you make, indicate which snippet(s) you are referencing using a consistent format (e.g. '<snippet-1>' for 'Snippet 1').\n"
    "- Do not misrepresent or embellish the information in the snippets.\n"
    "- Your answer should be a synthesis of only the relevant snippets.\n"
    "- Do not just list facts, but present a narrative in the form of short paragraphs.\n"
    "- Base your answer exclusively on the information contained in the provided snippets.\n"
    "- Do not add, infer, or extrapolate any details not explicitly present in the snippets.\n"
    "- Present your answer in a friendly, clear, and easy-to-understand manner.\n"
    "- Use simple language and, when needed, include direct quotes or paraphrased content from the snippets.\n"
    "- If the snippets don't provide enough information, state that you do not have enough information available.\n"
    "- Do not incorporate any external knowledge beyond the provided snippets.\n"
    "- The user does not have access to the snippets, so restate them clearly but do not quote verbatim.\n"
    "- The snippets are in Markdown format. Pay attention to the formatting to gleam more information.\n"
)

def build_index(metadata):
    sentence_index = dict()
    for idx, m in enumerate(metadata):
        if m["link"] not in sentence_index:
            sentence_index[m["link"]] = {m["pos"]: idx}
        else:
            sentence_index[m["link"]].update({m["pos"]: idx})

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
    if len(sys.argv) < 3:
        print('please provide the embedding vectors and a query')
        exit(1)

    with open(sys.argv[1], "rb") as f:
        metadata = pickle.load(f)

    embeddings = np.array([d["embedding"] for d in metadata])

    neighbors = NearestNeighbors(n_neighbors=5, algorithm="brute", metric="cosine").fit(
        embeddings
    )
    smodel = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

    query = sys.argv[2]

    inp = smodel.encode([query])
    scores, idxs = neighbors.kneighbors(inp)

    documents = "\n-----\n".join([f"Snippet {j}: {retrieve_with_context(metadata, i)}" for j,i in enumerate(idxs[0])])
    print(documents)
    print("------")
    print()
    messages = [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\n"
                "Context:\n"
                f"{documents}"},
        {"role": "user", "content": query}
    ]

    ollama.pull("llama3.2:3b-instruct-q4_K_S")
    response = ollama.chat(
        model="llama3.2:3b-instruct-q4_K_S",
        messages=messages,
    )

    print(response.message.content)
