#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Download a bibliography from zotero, write the output to a bibtex file.

Zotero has a way of checking if things have changed, which we use. If the bibliography has not changed, then
we do not write anything to the file.

Docs:
* https://www.zotero.org/support/dev/web_api/v3/basics
* https://www.zotero.org/settings/keys
"""

import io
import os
import requests

# local imports
import env

logger = env.logger()


def _write_current_version(version_id):
    with open(os.getenv("ZB_VERSION_FILE"), "w") as version_file:
        version_file.write(str(version_id))


def _read_current_version():
    ver = 0
    try:
        with open(os.getenv("ZB_VERSION_FILE"), "r") as version_file:
            ver = int(version_file.read())
    except IOError:
        pass
    return ver


def get_bib_from_zotero(min_version=0, offset=0):
    """fetch bibliography as csljson, returns the next offset or None if we're done"""
    url = "https://api.zotero.org/%s/items" % os.environ["ZB_SEARCH_PREFIX_URI"]
    url_params = {
        "sort": "date",
        "tag": os.getenv("ZB_SEARCH_TAG"),
        "format": "bibtex",
        "start": offset,
        "limit": 100
    }
    url_headers = {
        "Zotero-API-Version": 3,
        "Authorization": "Bearer %s" % os.getenv("ZB_API_KEY"),
        "If-Modified-Since-Version": str(min_version)
    }
    r = requests.get(url, params=url_params, headers=url_headers)

    bibtex = None
    if r.status_code == 200:
        new_version = r.headers["Last-Modified-Version"]
        if offset == 0:
            logger.info("downloading new version of bibliography. new version: %s" % new_version)
            _write_current_version(new_version)
        bibtex = r.text
    elif r.status_code == 304:
        # bibliography has not changed
        logger.info("no change. current version: %d" % min_version)
    else:
        logger.info("other error: %d" % r.status_code)

    return bibtex


def main():
    logger.info("starting")
    min_version = _read_current_version()

    offset = 0
    responses_from_zotero = []
    while offset is not None:
        logger.info("requesting offset {}".format(offset))
        response_body = get_bib_from_zotero(min_version, offset)
        if response_body:
            offset += 100
            responses_from_zotero.append(response_body)
        else:
            offset = None

    if len(responses_from_zotero) > 0:
        new_min_version = _read_current_version()
        fn = "%s-v%05d.bib" % (os.getenv("ZB_BIBTEX_FILE"), int(new_min_version))
        with io.open(fn, "w", encoding="UTF-8") as out:
            for rsp in responses_from_zotero:
                out.write(rsp)

    exit(0)


if __name__ == "__main__":
    main()
