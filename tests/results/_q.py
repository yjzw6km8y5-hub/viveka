import json
d = {x["id"]: x for x in json.load(open("data/tests/situations.json", encoding="utf8"))}
for i in ["T010", "T037", "T029", "T098", "T094", "T003"]:
    print(i, d[i]["expect"]["principles_any"])
