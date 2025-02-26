import pickle
import sys
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')

def split_text_into_sentences(text: str):
    return nltk.sent_tokenize(text)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("please provide a pickle file of posts")
        exit(1)

    with open(sys.argv[1], "rb") as f:
        posts = pickle.load(f)

    for s in split_text_into_sentences(posts[0][2]):
        print(s)
        print()
        print()
