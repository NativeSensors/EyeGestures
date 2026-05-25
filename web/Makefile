.PHONY: all clean min wasm

MINIFY = npx terser
MINIFY_FLAGS = --compress --mangle

SRC = src/eyegestures.js
MIN = $(SRC:.js=.min.js)

min:
	$(MINIFY) $(SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

wasm:
	cd ./engine && wasm-pack build --target web
	$(MINIFY) $(SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

clean:
	rm -f src/eyegestures.min.js