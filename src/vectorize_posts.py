import pickle
import sys
import re

def split_text_into_sentences(text: str):
    pattern = re.compile(r'(?<!\w\.\w.)(?<!\b[A-Z][a-z]\.)(?<![A-Z]\.)(?<=\.|\?)\s|\\n')

    return list(map(lambda s: s.strip().replace("\n", ""), pattern.split(text)))

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("please provide a pickle file of posts")
        exit(1)

    with open(sys.argv[1], "rb") as f:
        posts = pickle.load(f)

    for p in posts:
        if "censorship-resistant" in p[0].lower():
            print(p[2])
