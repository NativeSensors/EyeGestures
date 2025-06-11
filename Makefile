format:
	isort eyeGestures
	black eyeGestures

format_check:
	isort eyeGestures --check
	black eyeGestures --check