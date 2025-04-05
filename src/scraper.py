import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify as md
import pickle
import sys


def scrape(url, func):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        return func(url, soup)
    else:
        return None


def get_posts_archive(url: str, soup: BeautifulSoup):
    archive = soup.select("div.content p a:first-child")

    return map(lambda post: (post.text, urljoin(url, post.attrs["href"])), archive)


def embed_footnote(url, fn, fns, body_text, soup):
    inner_fns = fn.find_all("sup")

    if len(inner_fns) > 0:
        for inner_fn in inner_fns:
            inner_fn_id = inner_fn.find("a").attrs["href"][1:]
            inner_fn = fns.select(f'li[id="{inner_fn_id}"]')[0].extract()
            embed_footnote(url, inner_fn, fns, fn, soup)

    fn_reference = fn.select('p:last-child a[rev="footnote"]')[0].extract()
    fn_reference = fn_reference.attrs["href"]
    fn_text = f" ({fn.text.strip()})"
    fn_text = soup.new_string(fn_text)
    fn_reference = fn_reference[1:]

    body_text.select(f'sup[id="{fn_reference}"]')[0].replace_with(fn_text)


def parse_post(url: str, soup: BeautifulSoup):
    post_content = soup.select("div.content")[0]

    # remove the script tags from the post
    for s in post_content.find_all("script"):
        s.decompose()

    # remove comments section
    post_content.select("div#comments_body")[0].decompose()

    # embed footnotes in text
    footnotes = post_content.select("div.footnotes")
    if len(footnotes) > 0:
        footnotes = footnotes[0].extract()
        fn = footnotes.select("li")[0]
        while fn is not None:
            embed_footnote(url, fn, footnotes, post_content, soup)
            fn = fn.find_next_sibling()

    return post_content.text


if __name__ == "__main__":
    print("getting posts...")
    posts = scrape("http://www.aaronsw.com/weblog/fullarchive", get_posts_archive)
    posts = filter(lambda p: p is not None, posts)

    print("fetching and parsing post contents...")
    # expand posts with their markdown contents
    posts = list(map(lambda p: p + (scrape(p[1], parse_post),), posts))

    print("writing results to file...")
    file_name = sys.argv[1] if len(sys.argv) > 1 else "posts_dump.pt"
    with open(file_name, "wb") as f:
        pickle.dump(posts, f)

    print(posts[-1])
    print("done!")
