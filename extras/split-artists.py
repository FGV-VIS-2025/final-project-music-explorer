from tqdm import tqdm

from collections import defaultdict
import json

print("Reading unified file...")
with open("output/artist_map.json", "r") as f:
    artist_map = json.load(f)

alphabet_dict = defaultdict(lambda: dict())

print("Mapping alphabetic dictionaries...")
for artist_id, artist_dict in tqdm(artist_map.items()):
    alphabet_dict[artist_id[0]][artist_id] = artist_dict

print("Writing alphabetic split...")
for letter in tqdm(alphabet_dict):
    with open(f"output/{letter}_graph.json", "w") as f:
        json.dump(alphabet_dict[letter], f)
