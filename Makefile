include .env*

.PHONY: all clean FORCE pip test

all: $(ZB_HTML_FILE)

$(ZB_VERSION_FILE):
	echo 0 > $(ZB_VERSION_FILE)

out:
	mkdir -p out

# always run
FORCE:

$(ZB_JSON_FILE): FORCE out $(ZB_VERSION_FILE)
	$(ZB_PYTHON) ./download_bib.py --out=$@

$(ZB_HTML_FILE): $(ZB_JSON_FILE)
	cat $(ZB_JSON_FILE) | $(ZB_PYTHON) ./bib2html.py --out=$@
	# deploy it
	cp $(ZB_HTML_FILE) $(ZB_DEPLOY_TARGET)

test:
	$(ZB_PYTHON) -m doctest download_bib.py

clean:
	rm -rf $(ZB_OUT_DIR)

