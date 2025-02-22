import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def scrape(url, func):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        return func(url, soup)
    else:
        return None

def get_posts_archive(url: str, soup: BeautifulSoup):
    archive = soup.select('div.content p a:first-child')

    return list(map(lambda post: (post.text, urljoin(url, post.attrs['href'])), archive))


if __name__ == "__main__":
    posts = scrape("http://www.aaronsw.com/weblog/fullarchive", get_posts_archive)

    print(posts[0])
