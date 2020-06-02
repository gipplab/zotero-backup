import json
import sys

filename = sys.argv[1]
with open(filename) as f:
    bibtex = json.loads(f.read())
    for entry in bibtex:
        biblatex = entry['biblatex']
        if len(biblatex) > 3:
            print(biblatex)
