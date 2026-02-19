#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Download PDF attachments for bibliography entries from the Zotero API.

For each item matching the given tag filter in the JSON data file, this script:
- Names the PDF using the BibTeX citation key (from the biblatex entry header)
- Skips download if the PDF already exists in the output directory
- Downloads the PDF from the Zotero API
- Updates the Zotero item with tex.preprint pointing to the hosted PDF URL
  if that field is not already set (controlled by --max-writes)

Usage:
    python download-pdfs.py <json_file> [--tag TAG] [--output-dir DIR] [--max-writes N]
"""

import argparse
import json
import os
import re
import sys

import requests

# local imports
import env

logger = env.logger()

PREPRINTS_BASE_URL = "https://ag-gipp.github.io/bib/preprints"
_BIBLATEX_KEY_RE = re.compile(r"@\w+\{([^,\s]+)")


def _api_headers(extra=None):
    """Build common Zotero API request headers."""
    api_key = os.getenv("ZB_API_KEY")
    if not api_key:
        logger.error("ZB_API_KEY environment variable is not set")
        return None
    headers = {
        "Zotero-API-Version": "3",
        "Authorization": "Bearer %s" % api_key,
    }
    if extra:
        headers.update(extra)
    return headers


def get_citation_key(entry):
    """Extract the BibTeX citation key from the biblatex entry header.

    Falls back to parsing the 'Citation Key' line in the extra field,
    and finally to None if neither source yields a key.
    """
    biblatex = entry.get("biblatex", "")
    if biblatex:
        m = _BIBLATEX_KEY_RE.match(biblatex)
        if m:
            return m.group(1)
    # Fallback: parse from extra field
    extra = entry.get("data", {}).get("extra", "") or ""
    for line in extra.split("\n"):
        if line.lower().startswith("citation key:"):
            return line.split(":", 1)[1].strip()
    return None


def has_preprint_field(data):
    """Return True if tex.preprint is already set in the extra field."""
    extra = data.get("extra", "") or ""
    for line in extra.split("\n"):
        if line.lower().startswith("tex.preprint:"):
            return True
    return False


def download_pdf(item_key, filename, output_dir):
    """Download the PDF for a given Zotero attachment key and save to output_dir."""
    prefix_uri = os.getenv("ZB_SEARCH_PREFIX_URI")
    if not prefix_uri:
        logger.error("ZB_SEARCH_PREFIX_URI environment variable is not set")
        return None
    headers = _api_headers()
    if headers is None:
        return None
    url = "https://api.zotero.org/%s/items/%s/file" % (prefix_uri, item_key)
    try:
        r = requests.get(url, headers=headers)
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


def update_preprint_url(item_key, item_version, current_extra, preprint_url):
    """Add tex.preprint to the Zotero item's extra field via the API."""
    prefix_uri = os.getenv("ZB_SEARCH_PREFIX_URI")
    if not prefix_uri:
        logger.error("ZB_SEARCH_PREFIX_URI environment variable is not set")
        return False
    headers = _api_headers({
        "If-Unmodified-Since-Version": str(item_version),
        "Content-Type": "application/json",
    })
    if headers is None:
        return False
    new_extra = current_extra.rstrip() + "\ntex.preprint: " + preprint_url if current_extra else "tex.preprint: " + preprint_url
    url = "https://api.zotero.org/%s/items/%s" % (prefix_uri, item_key)
    try:
        r = requests.patch(url, headers=headers, json={"extra": new_extra})
    except requests.RequestException as e:
        logger.warning("Network error updating %s: %s" % (item_key, e))
        return False
    if r.status_code == 204:
        logger.info("Updated tex.preprint for %s -> %s" % (item_key, preprint_url))
        return True
    else:
        logger.warning("Failed to update %s: HTTP %d" % (item_key, r.status_code))
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("json_file", help="Path to the JSON file produced by download.py")
    parser.add_argument("--tag", default=None,
                        help="Tag to filter items (e.g. '!ms_author')")
    parser.add_argument("--output-dir", default="bib/docs/preprints",
                        help="Directory to save downloaded PDFs (default: bib/docs/preprints)")
    parser.add_argument("--max-writes", type=int, default=None, metavar="N",
                        help="Maximum number of Zotero items to update with tex.preprint "
                             "(useful for testing; default: unlimited)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    with open(args.json_file) as f:
        items = json.loads(f.read())

    # Build a map of item key -> entry for parent lookups
    items_by_key = {entry["data"]["key"]: entry for entry in items}

    # Collect keys of items that match the tag filter
    matching_keys = set()
    for entry in items:
        data = entry["data"]
        if data["itemType"] in ("attachment", "note", "annotation"):
            continue
        if args.tag:
            tag_found = any(t["tag"] == args.tag for t in data.get("tags", []))
        else:
            tag_found = True
        if tag_found:
            matching_keys.add(data["key"])

    logger.info("Found %d items matching tag filter" % len(matching_keys))

    # Download PDF attachments for matching items
    downloaded = 0
    skipped = 0
    writes_done = 0
    for entry in items:
        data = entry["data"]
        if data["itemType"] != "attachment":
            continue
        if data.get("contentType") != "application/pdf":
            continue
        parent_key = data.get("parentItem")
        if parent_key not in matching_keys:
            continue

        parent_entry = items_by_key.get(parent_key)
        if not parent_entry:
            continue
        parent_data = parent_entry["data"]

        # Determine filename from citation key, fall back to original filename
        cite_key = get_citation_key(parent_entry)
        filename = (cite_key + ".pdf") if cite_key else (data.get("filename") or (data["key"] + ".pdf"))

        filepath = os.path.join(args.output_dir, filename)

        # Skip if already downloaded
        if os.path.exists(filepath):
            logger.info("Skipping %s (already exists)" % filepath)
            skipped += 1
            continue

        # Download the PDF
        result = download_pdf(data["key"], filename, args.output_dir)
        if result:
            downloaded += 1
            # Update tex.preprint in Zotero if not already set and writes remain
            if not has_preprint_field(parent_data):
                if args.max_writes is None or writes_done < args.max_writes:
                    preprint_url = "%s/%s" % (PREPRINTS_BASE_URL, filename)
                    if update_preprint_url(
                        parent_key,
                        parent_entry["version"],
                        parent_data.get("extra") or "",
                        preprint_url,
                    ):
                        writes_done += 1
                else:
                    logger.info("Skipping tex.preprint update for %s (max-writes reached)" % parent_key)

    logger.info("Downloaded %d new PDF(s), skipped %d existing, %d Zotero item(s) updated (dir: %s)"
                % (downloaded, skipped, writes_done, args.output_dir))


if __name__ == "__main__":
    main()

