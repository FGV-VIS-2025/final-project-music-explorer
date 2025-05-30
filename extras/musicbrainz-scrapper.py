from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
from tqdm import tqdm
import json
from pprint import pprint

url = "https://musicbrainz.org/genres"
url_genre = "https://musicbrainz.org"
page = urlopen(url)

html_bytes = page.read()
html = html_bytes.decode("ISO-8859-1")

soup = BeautifulSoup(html, "html.parser")

links = soup.find("div", id="content").find_all("li")

genres_dict = dict()

def extract(link):
    if link:
        content = link.find_next("td").find_all("a")
        content = [link.text for link in content]
        return content
    return None

def get_info(link):
    page_genre = urlopen(link)
    html_genre = page_genre.read().decode()
    soup_genre = BeautifulSoup(html_genre, "html.parser")

    info = {"ref": link}

    link_from = soup_genre.find("th", string="from:")
    link_parent = soup_genre.find("th", string="subgenre of:")
    link_fusion = soup_genre.find("th", string="fusion of:")
    link_influeces = soup_genre.find("th", string="influenced by:")

    info["from"] = extract(link_from)
    info["parent"] = extract(link_parent)
    info["fused"] = extract(link_fusion)
    info["influence"] = extract(link_influeces)

    return info

for i in tqdm(range(len(links))):
    href_genre = links[i].find("a")["href"]
    genre_name = links[i].get_text()
    link = url_genre + href_genre
    genres_dict[genre_name] = get_info(link)

    # if i > 10:
    #     break

json_genres = json.dumps(genres_dict, indent=4, ensure_ascii=False)
with open("output/genres.json", "w", encoding="utf-8") as f:
    f.write(json_genres)
