.PHONY: format format_check test min wasm python python-help

# Python build
FORMAT_TOOLS = uv run --with isort --with black
CHECK_TOOLS = uv run --with pylint --with flake8 --with mypy --with isort --with black

MINIFY = npx terser
MINIFY_FLAGS = --compress --mangle
JS_SRC = web/src/eyegestures.js
MIN = $(JS_SRC:.js=.min.js)

format:
	$(FORMAT_TOOLS) python -m isort eye_gestures eyeGestures
	$(FORMAT_TOOLS) python -m black eye_gestures eyeGestures

format_check:
	$(CHECK_TOOLS) python -m isort eye_gestures eyeGestures --check
	$(CHECK_TOOLS) python -m black eye_gestures eyeGestures --check

check: format_check
	$(CHECK_TOOLS) python -m pylint eye_gestures eyeGestures
	$(CHECK_TOOLS) python -m flake8 eye_gestures eyeGestures
	$(CHECK_TOOLS) python -m mypy eye_gestures eyeGestures

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

ifeq ($(OS),Windows_NT)
python:
	$(PYO3_FORWARD_ENV) maturin build $(MATURIN_PYTHON_FLAGS) --target i686-pc-windows-msvc --interpreter $(PYTHON_INTERPRETERS)
	$(PYO3_FORWARD_ENV) maturin build $(MATURIN_PYTHON_FLAGS) --target x86_64-pc-windows-msvc --interpreter $(PYTHON_INTERPRETERS)
else
python:
	$(PYO3_FORWARD_ENV) maturin build $(MATURIN_PYTHON_FLAGS) --interpreter $(PYTHON_INTERPRETERS)
endif

clean:
	rm -f src/eyegestures.min.js

test:
	@if [ -d tests ] && find tests -maxdepth 1 -type f -name 'test_*.py' -print -quit | grep -q .; then \
		${PYTHON} -m unittest discover -s tests -p 'test_*.py'; \
	else \
		echo "No test files found in tests/; skipping test execution."; \
	fi
