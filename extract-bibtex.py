import json
import sys

filename = sys.argv[1]
keyword = False
try:
    keyword = sys.argv[2]
except IndexError:
    pass

with open(filename) as f:
    bibtex = json.loads(f.read())
    for entry in bibtex:
        biblatex = entry['biblatex']
        if len(biblatex) > 3:
            if keyword:
                tag_found = False
                for tag in entry['data']['tags']:
                    if tag['tag'] == keyword:
                        tag_found = True
                        break
            else:
                tag_found = True
            if tag_found:
                print(biblatex)
