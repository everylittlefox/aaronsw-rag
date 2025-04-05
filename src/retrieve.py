import pickle
import sys
import json
from sklearn.neighbors import NearestNeighbors
import numpy as np
from sentence_transformers import SentenceTransformer
import ollama
from peft import PeftModel
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# ollama.pull("llama3.2:3b-instruct-q4_K_S")

PROMPT = """
You are a factual answer generator that must respond only with information explicitly found in the provided retrieved documents. Do not include any external knowledge or assumptions. When constructing your answer, follow these guidelines:

1. Strict Document Reliance:
   Base all responses exclusively on the facts and data contained in the retrieved documents. If a piece of information is used, it must come from one of these documents.

2. Citation Style:
   For every factual statement or claim you include, append the corresponding document reference in angle brackets (e.g., <document-1>, <document-2>) immediately after the relevant sentence or clause.

3. Structured, Factual Language:
   Use clear, concise, and informative language. Model your responses after the following example:

   Rare earth metals are integral to various green technology applications, with specific elements serving crucial functions. Wind turbines utilize neodymium and dysprosium in their permanent magnets, enabling more efficient electricity generation without mechanical gearboxes <document-1>. These same magnetic properties make rare earths essential in electric vehicle motors, with each EV requiring approximately 1kg of these materials <document-1>.

   Energy-efficient LED lighting relies on europium, terbium, and yttrium, which significantly reduce energy consumption compared to traditional lighting options <document-1>.

   Energy storage represents another key application, with lanthanum being used in NiMH batteries that support hybrid vehicles and grid-scale renewable energy systems <document-2>. For emission reduction, cerium is incorporated into catalytic converters <document-2>. In specialized renewable energy applications where durability in extreme temperatures is required, samarium-cobalt magnets provide high efficiency for electric motors and generators <document-2>. Wind turbines specifically require substantial amounts of rare earth elements—approximately 600kg per turbine—with these materials enabling electricity generation in lower wind speeds while improving overall efficiency <document-3>. The rare earth elements also contribute to advanced photovoltaic systems, where lanthanum and cerium compounds are used in polishing powders for precision optical lenses, improving solar energy capture efficiency by 15-20% compared to conventional systems <document-4>.

4. Answering Questions:
   - If the user’s question can be fully answered by the retrieved documents, synthesize the relevant information and include the proper document citations.
   - If the question requires details that are not contained within the documents, respond that the available documents do not provide sufficient information.

5. Synthesis and Clarity:
   When combining information from multiple documents, ensure your answer remains clear and logically structured, with citations indicating which facts come from which documents.

Documents:
{documents}
"""

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
    return "\n---\n".join([f"Document {j}: {doc}" for j, doc in enumerate(documents)])


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
    # suggestions = prompt_model_for_questions(query, documents)
    # answer_documents = [
    #     d
    #     for s in suggestions
    #     for d in get_documents(s["suggested_query"], metadata, k=3)
    # ]
    print(format_documents(documents))
    print()
    print("[[prompting model for answers...]]")
    print("------")

    model_id = "HuggingFaceTB/SmolLM2-360M-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.add_special_tokens({"pad_token": "[PAD]"})
    pipeline_model = AutoModelForCausalLM.from_pretrained(
        model_id
    )  # , quantization_config=bnb_config)
    pipeline_model.resize_token_embeddings(len(tokenizer))
    pipeline_model = PeftModel.from_pretrained(pipeline_model, "./smol-finetuned-lora")

    generator = pipeline(
        "text-generation", model=pipeline_model, tokenizer=tokenizer, max_length=1536
    )

    messages = [
        {
            "role": "system",
            "content": PROMPT.format(documents=format_documents(documents)),
        },
        {"role": "user", "content": query},
    ]
    response = generator(messages, repetition_penalty=1.1)
    print()
    print()
    print(response[0]["generated_text"][-1]["content"])
