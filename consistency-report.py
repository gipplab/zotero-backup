import json
import sys

filename = sys.argv[1]
with open(filename) as f:
    bibtex = json.loads(f.read())
    for entry in bibtex:
        tags = entry['data']['tags']
        if len(tags) == 0:
            print(entry['data']['key'] + "has not tags")
