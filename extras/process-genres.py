from tqdm import tqdm
#File opening
import tarfile
import subprocess
from os.path import isfile
#Data processing
import json
from collections import defaultdict
from pprint import pprint

filtered = list()
filtered_rock = list()
filtered_only_features = list()
counts = defaultdict(lambda: 0)
counts_rock = defaultdict(lambda: 0)

genres_map = defaultdict(lambda: defaultdict(lambda: 0))


for tar in ["tarxz/artist.tar.xz", "tarxz/work.tar.xz", "tarxz/release.tar.xz", "tarxz/recording.tar.xz"]:
    if not (isfile(tar) and tarfile.is_tarfile(tar)):
        print(tar, "is missing! Aborting to prevent bad surprises...")
        exit()

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
        line = line.decode("utf-8", errors = "replace").rstrip("\n")
        dictionary = json.loads(line)
        yield index, dictionary

    print("Closing subprocesses and pipes")
    tar_call.stdout.close()
    tar_call.wait()
    xz_call.wait()

for index, dictionary in tqdm(iter_in_file("tarxz/release-group.tar.xz", "mbdump/release-group"), total = 3746359):
    date = dictionary.get("first-release-date", "")
    if date == "" or not date[0].isdigit():
        date = ""
    else:
        date = int(date[:4])
    for genre in dictionary.get("genres", []):
        genres_map[genre["name"]][date] += genre["count"]

for genre in genres_map:
    for year in genres_map[genre].keys():
        if year != "total":
            genre["total"] += genre[year]

with open("output/genres_map.json", "w") as f:
    json.dump(genres_map, f, indent = 2)
