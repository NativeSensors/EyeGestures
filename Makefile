# Python build
FORMAT_TOOLS = uv run --with isort --with black
CHECK_TOOLS = uv run --with pylint --with flake8 --with mypy --with isort --with black

MINIFY = npx terser
MINIFY_FLAGS = --compress --mangle
JS_SRC = web/src/eyegestures.js
MIN = $(JS_SRC:.js=.min.js)

.PHONY: format format_check test min wasm python python-help

format:
	$(FORMAT_TOOLS) python -m isort eyeGestures
	$(FORMAT_TOOLS) python -m black eyeGestures

format_check:
	$(CHECK_TOOLS) python -m isort eyeGestures --check
	$(CHECK_TOOLS) python -m black eyeGestures --check

check: format_check
	$(CHECK_TOOLS) python -m pylint eyeGestures
	$(CHECK_TOOLS) python -m flake8 eyeGestures
	$(CHECK_TOOLS) python -m mypy eyeGestures

# Web build
min:
	$(MINIFY) $(JS_SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

wasm:
	cd ./engine && wasm-pack build --target web
	$(MINIFY) $(JS_SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

# Python build
PYTHON = uv run
MATURIN_PYTHON_FLAGS = --release --no-default-features --features python
# Set to 1 to allow builds for newer CPython versions than PyO3 officially supports.
PYO3_USE_ABI3_FORWARD_COMPATIBILITY ?= 1
PYTHON_INTERPRETERS=python3.12 python3.13

ifeq ($(OS),Windows_NT)
PYO3_FORWARD_ENV = set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=$(PYO3_USE_ABI3_FORWARD_COMPATIBILITY) &&
else
PYO3_FORWARD_ENV = PYO3_USE_ABI3_FORWARD_COMPATIBILITY=$(PYO3_USE_ABI3_FORWARD_COMPATIBILITY)
endif

python:
	$(PYO3_FORWARD_ENV) maturin build $(MATURIN_PYTHON_FLAGS) --interpreter $(PYTHON_INTERPRETERS)

clean:
	rm -f src/eyegestures.min.js

test:
	${PYTHON} -m unittest tests/test_*