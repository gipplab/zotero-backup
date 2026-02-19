#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Download PDF attachments for bibliography entries from the Zotero API.

For each item matching the given tag filter in the JSON data file, this script
downloads the PDF attachment (if any) from the Zotero API and saves it to the
specified output directory.

Usage:
    python download-pdfs.py <json_file> [<tag>] [<output_dir>]

Arguments:
    json_file   Path to the JSON file produced by download.py
    tag         Optional tag to filter items (e.g. '!ms_author')
    output_dir  Directory to save downloaded PDFs (default: bib/preprints)
"""

import json
import os
import sys

import requests

# local imports
import env

logger = env.logger()


def download_pdf(item_key, filename, output_dir):
    """Download the PDF for a given Zotero attachment key and save to output_dir."""
    prefix_uri = os.getenv("ZB_SEARCH_PREFIX_URI")
    if not prefix_uri:
        logger.error("ZB_SEARCH_PREFIX_URI environment variable is not set")
        return None
    api_key = os.getenv("ZB_API_KEY")
    if not api_key:
        logger.error("ZB_API_KEY environment variable is not set")
        return None
    url = "https://api.zotero.org/%s/items/%s/file" % (prefix_uri, item_key)
    url_headers = {
        "Zotero-API-Version": "3",
        "Authorization": "Bearer %s" % api_key,
    }
    try:
        r = requests.get(url, headers=url_headers)
    except requests.RequestException as e:
        logger.warning("Network error downloading %s: %s" % (item_key, e))
        return None
    if r.status_code == 200:
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(r.content)
        logger.info("Downloaded %s -> %s" % (item_key, filepath))
        return filepath
    else:
        logger.warning("Failed to download %s: HTTP %d" % (item_key, r.status_code))
        return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    json_file = sys.argv[1]
    tag = sys.argv[2] if len(sys.argv) > 2 else None
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "bib/preprints"

    os.makedirs(output_dir, exist_ok=True)

    with open(json_file) as f:
        items = json.loads(f.read())

    # Collect keys of items that match the tag filter
    matching_keys = set()
    for entry in items:
        data = entry["data"]
        if data["itemType"] in ("attachment", "note", "annotation"):
            continue
        if tag:
            tag_found = any(t["tag"] == tag for t in data.get("tags", []))
        else:
            tag_found = True
        if tag_found:
            matching_keys.add(data["key"])

    logger.info("Found %d items matching tag filter" % len(matching_keys))

    # Download PDF attachments for matching items
    downloaded = 0
    for entry in items:
        data = entry["data"]
        if data["itemType"] != "attachment":
            continue
        if data.get("contentType") != "application/pdf":
            continue
        parent_key = data.get("parentItem")
        if parent_key in matching_keys:
            filename = data.get("filename") or (data["key"] + ".pdf")
            result = download_pdf(data["key"], filename, output_dir)
            if result:
                downloaded += 1

    logger.info("Downloaded %d PDF(s) to %s" % (downloaded, output_dir))


if __name__ == "__main__":
    main()
