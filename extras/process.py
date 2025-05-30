#progressbar
from tqdm import tqdm
#File opening
import tarfile
import subprocess
#Data processing
import json
from collections import defaultdict
from pprint import pprint

#Different outputs of the script
filtered = list()
filtered_rock = list()
filtered_only_features = list()
artist_map = dict()
work_map = dict()

#Counting hash maps
counts = defaultdict(lambda: 0)
counts_rock = defaultdict(lambda: 0)


#It isnt possible to safely open the file with native python tools because
#we get a buffer in which we cant use seek, and so the python standard features
#to iter in the buffer will error out. So the approach is to use shell commands.
#they are wrapped here into an iterator to convenience
def iter_in_file(tar_name, file_name):
    if not tarfile.is_tarfile(tar_name):
        print(tar_name, "isn't a tar xz file!")
        exit()
    xz_call = subprocess.Popen(
        ["xz", "-dc", tar_name], #The command here is xz --decompress --stdout "tar file"
        stdout = subprocess.PIPE
    )

    tar_call = subprocess.Popen(
        ["tar", "-xO", "--file=-", file_name], #The command here is tar -x0 --file="the file inside thar"
        stdin = xz_call.stdout,
        stdout = subprocess.PIPE
    )

    xz_call.stdout.close()

    for index, line in enumerate(tar_call.stdout):
        yield index, line

    print("Closing subprocesses and pipes")
    tar_call.stdout.close()
    tar_call.wait()
    xz_call.wait()

autorship = ["autorship", "writer", "composer", "lyricist", "librettist", "revised by", "scriptwriter", "translator", "reconstructed by", "arranger", "instrument arranger", "orchestrator", "vocal arranger", "adapter", "previous attribution"]
performance = ["performance", "performer", "instrument", "vocal", "performing orchestra", "conductor", "chorus master", "concertmaster", "audio director"]


for index, line in tqdm(iter_in_file("tarxz/artist.tar.xz", "mbdump/artist"), total = 2557693):
    line = line.decode("utf-8", errors = "replace").rstrip("\n")
    dictionary = json.loads(line)
    if(len(dictionary["relations"]) > 0):
        entry = {
            "n": dictionary["name"],
            "ms": set(), #members
            "im": set(), #member of
            "cs": set(), #covers someone
            "gc": set(), #got covered by someone
        }
        for relation in dictionary["relations"]:
            if relation["target-type"] == "artist" and relation["type"] == "member of band":
                if relation["direction"] == "forward":
                    entry["im"].add(relation["artist"]["id"])
                elif relation["direction"] == "backward":
                    entry["ms"].add(relation["artist"]["id"])
    artist_map[dictionary["id"]] = entry

for index, line in tqdm(iter_in_file("tarxz/work.tar.xz", "mbdump/work"), total = 2322880):
    line = line.decode("utf-8", errors = "replace").rstrip("\n")
    dictionary = json.loads(line)
    if(len(dictionary["relations"]) > 0):
        entry = {
            "n": dictionary["title"],
            "a": defaultdict(lambda: 0)
        }
        # for relation in dictionary["relations"]:
        #     if relation["type"] in autorship:
        #         entry["a"].add(relation["artist"]["id"])
        work_map[dictionary["id"]] = entry

#map works to authors - different logic than just seeing relations to captude bands and such
for index, line in tqdm(iter_in_file("tarxz/release.tar.xz", "mbdump/release"), total = 4774602):
    line = line.decode("utf-8", errors = "replace").rstrip("\n")
    dictionary = json.loads(line)
    for media in dictionary.get("media", []):
        for track in media.get("tracks", []):
            for relation in track["recording"]["relations"]:
                if relation["target-type"] == "work" and not ("cover" in relation["attributes"]):
                    work_id = relation["work"]["id"]
                    for artist_meta in track["artist-credit"]:
                            work_map[work_id]["a"][artist_meta["artist"]["id"]] += 1 #autorship count


for index, line in tqdm(iter_in_file("tarxz/recording.tar.xz", "mbdump/recording"), total = 133144):
    line = line.decode("utf-8", errors = "replace").rstrip("\n")
    dictionary = json.loads(line)
    for relation in dictionary["relations"]:
        if relation["target-type"] == "work" and not ("cover" in relation["attributes"]):
            work_id = relation["work"]["id"]
            for artist_meta in dictionary["artist-credit"]:
                work_map[work_id]["a"][artist_meta["artist"]["id"]] += 1 #autorship count


for work in tqdm(work_map):
    total_sum = sum(work_map[work]["a"].values())
    true_authors = list()
    for artist, count in work_map[work]["a"].items():
        if count/total_sum > 0.1:
            true_authors.append(artist)
    work_map[work]["a"] = true_authors


for index, line in tqdm(iter_in_file("tarxz/release.tar.xz", "mbdump/release"), total = 4774602):
    line = line.decode("utf-8", errors = "replace").rstrip("\n")
    dictionary = json.loads(line)
    for media in dictionary.get("media", []):
        for track in media.get("tracks", []):
            for relation in track["recording"]["relations"]:
                if relation["target-type"] == "work" and "cover" in relation["attributes"]:
                    cover_of = relation["work"]["id"]
                    for cover_artist in track["artist-credit"]:
                        cover_artist = cover_artist["artist"]["id"]
                        for og_artist in work_map[cover_of]["a"]:
                            artist_map[cover_artist]["cs"].add(og_artist)
                            artist_map[og_artist]["gc"].add(cover_artist)


for index, line in tqdm(iter_in_file("tarxz/recording.tar.xz", "mbdump/recording"), total = 133144):
    line = line.decode("utf-8", errors = "replace").rstrip("\n")
    dictionary = json.loads(line)
    for relation in dictionary["relations"]:
        if relation["target-type"] == "work" and "cover" in relation["attributes"]:
            cover_of = relation["work"]["id"]
            for cover_artist in dictionary["artist-credit"]:
                cover_artist = cover_artist["artist"]["id"]
                for og_artist in work_map[cover_of]["a"]:
                    artist_map[cover_artist]["cs"].add(og_artist)
                    artist_map[og_artist]["gc"].add(cover_artist)

# for index, line in tqdm(iter_in_file("tarxz/recording.tar.xz", "mbdump/recording")):
#     line = line.decode("utf-8", errors = "replace").rstrip("\n")
#     dictionary = json.loads(line)
#             break


    # generos = dictionary.get("genres", list())
    # if len(generos) != 0:
    #     filtered.append(dictionary)
    #     new = {
    #         "genres": generos,
    #         "life-span": dictionary["life-span"],
    #         "name": dictionary["name"]
    #     }
    #     filtered_only_features.append(new)
    #     generos = [genero["name"] for genero in dictionary["genres"]]
    #     print(generos)
    #     tem_rock = 0
    #     for genero in generos:
    #         if "rock" in genero:
    #             counts_rock[genero] += 1
    #             tem_rock = 1
    #     if tem_rock:
    #         filtered_rock.append(dictionary)

print("Writing artists map to json")
for artist in artist_map:
    artist_map[artist]["ms"] = list(artist_map[artist]["ms"])
    artist_map[artist]["im"] = list(artist_map[artist]["im"])
    artist_map[artist]["cs"] = list(artist_map[artist]["cs"])
    artist_map[artist]["gc"] = list(artist_map[artist]["gc"])
with open("output/artist_map.json", "w") as f:
    json.dump(artist_map, f, indent = 2)

print("Writing work map to json")
# for work in work_map:
#     work_map[work]["a"] = list(work_map[work]["a"])
with open("output/work_map.json", "w") as f:
    json.dump(work_map, f, indent = 2)
# pprint(counts)
# pprint(counts_rock)
# print(index)
# print("escrevendo artistas")
# with open("artists.json", "w") as f:
#     json.dump(filtered, f)
# print("escrevendo artistas só três featuress")
# with open("features_artists.json", "w") as f:
#     json.dump(filtered_only_features, f, indent = 2)
# print("escrevendo artistas de rock")
# with open("rock_artists.json", "w") as f:
#     json.dump(filtered_rock, f)
# print("escrevendo counts")
# with open("counts.json", "w") as f:
#     json.dump(counts, f, indent = 2)
# print("escrevendo counts de rock")
# with open("rock_counts.json", "w") as f:
#     json.dump(counts_rock, f, indent = 2)


#
# with tarfile.open("artist.tar.xz", "r|xz") as compacted:
#     artists = compacted.getmember("mbdump/artist")
#     print("Got member info of artist file")
#     artists = compacted.extractfile(artists)
#     print("Got file representation of extractedfile")
#     read_buffer = b""
#     while True:
#         chunk = artists.read1(1024 * 1024 * 100) #100 MiB per read - since I have memory :D
#         if not chunk:
#             break
#         print(chunk)
#
#
# exit()
#
# with open("artist", "r") as f:
#     for index, line in enumerate(f):
