import json
import sys

filename = sys.argv[1]
keyword = False
try:
    keyword = sys.argv[2]
except IndexError:
    pass


def undo_better_bibtex_hack(biblatex, extra=""):
    biblatex = biblatex[:-2]
    for line in extra.split("\n"):
        if line.startswith("tex."):
            payload = line[4:]
            key, value = payload.split(": ", 1)
            biblatex += f"\n\t{key} = {{{value}}},"
    return biblatex+"\n}"


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
                extra_ = entry['data']['extra']
                if extra_:
                    biblatex = undo_better_bibtex_hack(biblatex, extra_)
                print(biblatex)
