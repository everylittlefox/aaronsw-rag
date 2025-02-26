import pickle
import sys
import nltk
import re
from sentence_transformers import SentenceTransformer
import utils

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')


def split_text_into_sentences(text: str):
    # remove the last two sentences which are the call to follow on Twitter
    # and the date of publication
    if text is None:
        return []

    sentences = map(lambda s: s.strip(), nltk.sent_tokenize(text)[:-2])
    # remove new lines and the '====' used to delineate the heading of a post
    sentences = map(lambda s: re.sub(r"[\=\n]", "", s), sentences)

    return list(sentences)


# gives order to chunked sentences as well as attaches the locations of the
# sentences before and after
def contexify(embeddings):
    contexified = []
    for idx, (s, emb) in enumerate(embeddings):
        first = idx == 0
        last = idx == len(embeddings) - 1
        contexified.append(dict(embedding=emb,
                                text=s,
                                pos=idx,
                                before= (idx-1,) if not last else (idx-2,idx-1),
                                after= (1,2) if first
                                             else (idx + 1,) if not last
                                             else (-1,)))

    return contexified


def embed_sentences(sentences: list[str]):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L12-v2")

    return list(zip(sentences, model.encode(sentences)))


def vectorize(posts):
    print("making transformations...")
    transforms = utils.compose(contexify, embed_sentences, split_text_into_sentences)

    vp = [(p[0], p[1], transforms(p[2])) for p in posts]
    # filter out the posts that resulted in a 404
    # p[2] holds the sentences of the post
    vp = [p for p in vp if len(p[2]) > 0]

    print("adding metadata...")
    vp = [dict(**s, link=p[1], title=p[0]) for p in vp for s in p[2]]

    return vp


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("please provide a pickle file of posts")
        exit(1)

    print("loading posts...")
    with open(sys.argv[1], "rb") as f:
        posts = pickle.load(f)


    vp = vectorize(posts)
    print(f"embedded {len(vp)} sentences")

    file_name = sys.argv[2] if len(sys.argv) > 2 else "vectors_dump.pt"
    print("writing results...")
    with open(file_name, "wb") as f:
        pickle.dump(vp, f)

    print("done!")
