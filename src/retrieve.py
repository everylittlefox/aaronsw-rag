import pickle
import sys
import json
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama

ollama.pull("llama3.2:3b-instruct-q4_K_S")

SYSTEM_PROMPT = (
    "You are a helpful assistant that has found the following text excerpts from different articles"
    " by Aaron Swartz after running the user's question through a search algorithm.\n"
    "When generating your answer, follow these guidelines:\n"
    "- Do not add, infer, or extrapolate any details not explicitly present in the snippets.\n"
    "- For each statement you make, indicate which snippet(s) you are referencing using a consistent format (e.g. '<snippet-1>' for 'Snippet 1').\n"
    "- Do not misrepresent or embellish the information in the snippets.\n"
    "- Ensure that references are correctly attributed. That is, do not quote Excerpt 1 when you mean to quote Excerpt 3."
    "- Your answer should be a synthesis of only the relevant snippets.\n"
    "- Do not just list facts, but present a narrative in the form of short paragraphs.\n"
    "- Base your answer exclusively on the information contained in the provided snippets.\n"
    "- Present your answer in a friendly, clear, and easy-to-understand manner.\n"
    "- Use simple language and, when needed, include direct quotes or paraphrased content from the snippets.\n"
    "- If the snippets don't provide enough information, state that you do not have enough information available.\n"
    "- Do not incorporate any external knowledge beyond the provided snippets.\n"
    "- The user does not have access to the snippets, so restate them clearly but do not quote verbatim.\n"
    "- The snippets are in Markdown format. Pay attention to the formatting to gleam more information.\n"
)

SYSTEM_PROMPT_Q = (
    "You are a helpful assistant that has found the following text excerpts from different articles"
    " by Aaron Swartz after running the user's question through a search algorithm.\n"
    "Based on the user's question and the results of your search, do the following:\n"
    "- Decompose the original question into at least two (2) logical parts.\n"
    "- For each part, come up with search queries to feed into the algorithm.\n"
    "- Back your decomposition and suggested query with a reason.\n"
    "- Do not repeat ideas.\n"
    "- Respond in the following JSON list format with the following object fields: 'title', 'suggested_query', 'reason'."
    "For example:\n"
    """[
  {
    "title": "Critique of corporate control",
    "suggested_query": "corporate control over information criticism",
    "reason": "what importance does this query have to the original question?",
  },
]\n"""
    "Only respond in this format.\n"
    "- Aaron's blog is searched through with the queries, so avoid using his name in them."
    " For example, say 'corporate power criticism' instead of 'Aaron Swartz corporate power criticism'."
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


def get_documents(query, metadata, k=5):
    embeddings = np.array([d["embedding"] for d in metadata])

    print("[[fetching documents...]]")
    neighbors = NearestNeighbors(n_neighbors=k, algorithm="brute", metric="cosine").fit(
        embeddings
    )
    smodel = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

    inp = smodel.encode([query])
    _, idxs = neighbors.kneighbors(inp)

    return [retrieve_with_context(metadata, i) for i in idxs[0]]


def format_documents(documents: list[str]):
    return "\n-----\n".join([f"Excerpt {j}: {doc}" for j, doc in enumerate(documents)])


def prompt_model_for_questions(query: str, documents: list[str]):
    print("[[prompting model for questions...]]")
    messages = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT_Q}\n\n"
            "Search Results:\n"
            f"{format_documents(documents)}",
        },
        {"role": "user", "content": query},
    ]

    failures = 0
    while True:
        response = ollama.chat(
            model="llama3.2:3b-instruct-q4_K_S",
            messages=messages,
        )

        response = response.message.content

        try:
            suggestions = json.loads(response)

            for su in suggestions:
                print(f"[{su['suggested_query']}]")

            return suggestions
        except:
            failures += 1
            print(f"[[Failures: {failures}]]")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("please provide the embedding vectors and a query")
        exit(1)

    with open(sys.argv[1], "rb") as f:
        metadata = pickle.load(f)

    query = sys.argv[2]
    documents = get_documents(query, metadata)
    suggestions = prompt_model_for_questions(query, documents)
    answer_documents = [
        d
        for s in suggestions
        for d in get_documents(s["suggested_query"], metadata, k=3)
    ]
    print(format_documents(answer_documents))
    print()
    print("[[prompting model for answers...]]")
    print("------")
    print()
    messages = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}\n\n"
            "Search Results:\n"
            f"{format_documents(answer_documents)}",
        },
        {"role": "user", "content": query},
    ]

    response = ollama.chat(
        model="llama3.2:3b-instruct-q4_K_S",
        messages=messages,
    )

    print(response.message.content)
