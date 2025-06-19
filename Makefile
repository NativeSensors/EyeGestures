format:
	isort eyeGestures
	black eyeGestures

format_check:
	isort eyeGestures --check
	black eyeGestures --check

check: format_check
	pylint eyeGestures
	flake8 eyeGestures
