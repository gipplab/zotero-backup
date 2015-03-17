# zotero-backup

turn a zotero collection into a bibtex file for archival

This code basically just downloads a bibliography using the
[Zotero API](https://www.zotero.org/support/dev/web_api/v3/basics),
It asks Zotero politely whether the bibliography has changed since the last run, to keep things lightweight unless things have changed.


# requirements

* python 2.7.x (not tested on python 3)
* gnu make
* zotero API key (create one at https://www.zotero.org/settings/keys)


# install + configure

You probably should use a virtualenv, then:

    pip install -r requirements.txt

Edit `.env` directly or create `.env.local` to override the settings.  In particular, you will need to override the
zotero api key, the zotero search parameters, and the output paths.

If you're querying a group, you can find its id by visiting its page, then inspecting the URL for its RSS feed.


# run

    make

Probably, you'll want to run `make` in a cron job to keep the output up to date.

If you need to change the settings and re-run:

    make clean
    make
