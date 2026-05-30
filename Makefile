# Python build
FORMAT_TOOLS = uv run --with isort --with black
CHECK_TOOLS = uv run --with pylint --with flake8 --with mypy --with isort --with black
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

MINIFY = npx terser
MINIFY_FLAGS = --compress --mangle
JS_SRC = web/src/eyegestures.js
MIN = $(JS_SRC:.js=.min.js)

min:
	$(MINIFY) $(JS_SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

wasm:
	cd ./engine && wasm-pack build --target web
	$(MINIFY) $(JS_SRC) $(MINIFY_FLAGS) -o engine/pkg/eyegestures.min.js

# Python build
PYTHON = uv run
MATURIN_PYTHON_FLAGS = --release --no-default-features --features python
# Space-separated interpreters used by `make python`.
# Example single: `make python PYTHON_INTERPRETERS="python3.13"`
# Example multi:  `make python PYTHON_INTERPRETERS="python3.12 python3.13"`
# Default: use whichever `python` is in PATH.
PYTHON_INTERPRETERS ?= python
# Set to 1 to allow builds for newer CPython versions than PyO3 officially supports.
PYO3_USE_ABI3_FORWARD_COMPATIBILITY ?= 1

ifeq ($(OS),Windows_NT)
PYO3_FORWARD_ENV = set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=$(PYO3_USE_ABI3_FORWARD_COMPATIBILITY) &&
else
PYO3_FORWARD_ENV = PYO3_USE_ABI3_FORWARD_COMPATIBILITY=$(PYO3_USE_ABI3_FORWARD_COMPATIBILITY)
endif

python:
	cd ./engine && $(PYO3_FORWARD_ENV) maturin build $(MATURIN_PYTHON_FLAGS) --interpreter $(PYTHON_INTERPRETERS)

python-help:
	@echo "make python"
	@echo "  - builds wheel using default interpreter: python"
	@echo "make python PYTHON_INTERPRETERS=\"python3.13\""
	@echo "  - builds wheel for one interpreter"
	@echo "make python PYTHON_INTERPRETERS=\"python3.12 python3.13\""
	@echo "  - builds wheel files in engine/target/wheels"
	@echo "make python PYO3_USE_ABI3_FORWARD_COMPATIBILITY=0"
	@echo "  - enforces PyO3 max supported Python version"
	@echo "Tip (Windows): prefer explicit paths if discovery fails, e.g."
	@echo "  make python PYTHON_INTERPRETERS=\"C:/Python313/python.exe C:/Python314/python.exe\""

clean:
	rm -f src/eyegestures.min.js

test:
	${PYTHON} -m unittest tests/test_*