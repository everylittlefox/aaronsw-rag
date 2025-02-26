import pickle
import sys
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

def split_text_into_sentences(text: str):
    # remove the last two sentences which are the call to follow on Twitter
    # and the date of publication
    return list(map(lambda s: s.strip(), nltk.sent_tokenize(text)[:-2]))

# gives order to chunked sentences as well as attaches the locations of the
# sentences before and after
def contexify(sentences: list[str]):
    contexified = []
    for idx, s in enumerate(sentences):
        contexified.append(dict(value=s,
                                pos=idx,
                                before=idx-1,
                                after= -1 if idx == len(sentences) - 1 else idx + 1))

    return contexified


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("please provide a pickle file of posts")
        exit(1)

    with open(sys.argv[1], "rb") as f:
        posts = pickle.load(f)

    cnt = contexify(split_text_into_sentences(posts[75][2]))

    print(cnt[1])
