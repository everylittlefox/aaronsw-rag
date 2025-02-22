import pickle
import sys

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("please provide a pickle file of posts")
        exit(1)

    with open(sys.argv[1], "rb") as f:
        posts = pickle.load(f)

    print(posts[0])
    print("num posts:", len(posts))
    print("num invalids:", len(list(filter(lambda p: p is None, posts))))
