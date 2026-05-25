.PHONY: format format_check test min wasm python


format:
	isort eyeGestures
	black eyeGestures

format_check:
	isort eyeGestures --check
	black eyeGestures --check

check: format_check
	pylint eyeGestures
	flake8 eyeGestures
	mypy eyeGestures

# Web build

MINIFY = npx terser
MINIFY_FLAGS = --compress --mangle
JS_SRC = web/src/eyegestures.js
MIN = $(JS_SRC:.js=.min.js)

min:
	$(MINIFY) $(JS_SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

wasm:
	cd ./engine && wasm-pack build --target web
	$(MINIFY) $(JS_SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

# Python buil
PYTHON = uv run

python:
	cd ./engine && maturin develop --release --no-default-features --features python

clean:
	rm -f src/eyegestures.min.js

test:
	${PYTHON} -m unittest tests/test_*