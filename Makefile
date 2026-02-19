.PHONY: all clean out

all: $(ZB_FILE)
	$(ZB_PYTHON) ./consistency-report.py $(ZB_FILE) > $(ZB_OUT_DIR)/report.txt

$(ZB_VERSION_FILE): 
	mkdir -p $(ZB_OUT_DIR)
	echo 0 > $(ZB_VERSION_FILE)

$(ZB_FILE): $(ZB_VERSION_FILE)
	$(ZB_PYTHON) ./download.py

bib: $(ZB_FILE)
	$(ZB_PYTHON) ./extract-bibtex.py $(ZB_FILE)

pdfs: $(ZB_FILE)
	mkdir -p bib/docs/preprints
	$(ZB_PYTHON) ./download-pdfs.py $(ZB_FILE) $(ZB_SEARCH_TAG) bib/docs/preprints

clean:
	rm -rf $(ZB_OUT_DIR)

