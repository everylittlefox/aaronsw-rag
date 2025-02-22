import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify as md

def scrape(url, func):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        return func(url, soup)
    else:
        return None

def get_posts_archive(url: str, soup: BeautifulSoup):
    archive = soup.select('div.content p a:first-child')

    return map(lambda post: (post.text, urljoin(url, post.attrs['href'])), archive)

def parse_post(url: str, soup: BeautifulSoup):
    post_content = soup.select('div.content')[0]

    # remove comments section
    post_content.select('div#comments_body')[0].decompose()

    # remove the script tags from the post
    for s in post_content.find_all('script'):
        s.decompose()

    return md(str(post_content))

if __name__ == "__main__":
    print("getting posts...")
    posts = scrape("http://www.aaronsw.com/weblog/fullarchive", get_posts_archive)
    posts = filter(lambda p: p is not None, posts)

    print("fetching and parsing post contents...")
    # expand posts with their markdown contents
    posts = list(map(lambda p: p + (scrape(p[1], parse_post),), posts))

    print(posts[56][2])
