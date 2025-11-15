.PHONY: format format_check test

# Detect OS and set PYTHON command accordingly
ifeq ($(OS),Windows_NT)
    PYTHON := $(shell where python3)
else
    PYTHON := $(shell which python3)
endif

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

test:
	${PYTHON} -m unittest tests/test_*