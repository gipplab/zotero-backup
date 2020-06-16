import json
import re
import sys

filename = sys.argv[1]
log = {}


def get_user(meta):
    if 'createdByUser' in meta:
        user_info = meta['createdByUser']
        if 'name' in user_info:
            return user_info['name']


def log_problem(e, msg):
    current_key = e['data']['key']
    link = e['data']['parentItem'] if 'parentItem' in e['data'] else current_key
    usr = get_user(e['meta'])
    string = log.get(usr, '')
    string += f'[{current_key}](https://www.zotero.org/groups/2480461/ag-gipp/items/{link}/item-details) {msg} (' \
              f'{usr})\n\n'
    log[usr] = string


def parse_extra_field(d, ent):
    extra = d.split('\n')
    extra_dictionary = {}
    for e in extra:
        if len(e.strip()) > 0:
            parts = e.split(':', 1)
            if len(parts) == 2:
                extra_dictionary[parts[0].strip()] = parts[1].strip()
            else:
                log_problem(ent, 'information in extra field not formatted as key:value pair: ' + e)
    return extra_dictionary


with open(filename) as f:
    bibtex = json.loads(f.read())
    file_pat = re.compile('--[a-zA-Z]{2,}--')
    for entry in bibtex:
        data = entry['data']
        tags = data['tags']
        biblatex = entry['biblatex']
        if len(tags) == 0 and len(biblatex) > 3:
            log_problem(entry, "has no tags")
        if 'extra' in data:
            edict = parse_extra_field(data['extra'], entry)
            if 'Citation Key' in edict:
                cite_key = edict['Citation Key']
                if len(cite_key) < 3:
                    log_problem(entry, cite_key + ' is too short as a citation key.')
        if 'filename' in data:
            fname = data['filename']
            if not file_pat.search(fname):
                if "Snapshot" not in fname + data.get('title', ''):
                    log_problem(entry, "does not comply with file naming convention:" + fname)

    for key, value in log.items():
        print(f'### {key}\n\n{value}\n\n')
