.PHONY: all clean out

all: $(ZB_VERSION_FILE)
	$(ZB_PYTHON) ./download.py

$(ZB_VERSION_FILE): 
	mkdir -p $(ZB_OUT_DIR)
	echo 0 > $(ZB_VERSION_FILE)

clean:
	rm -rf $(ZB_OUT_DIR)

