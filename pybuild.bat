@REM .\venv\Scripts\activate
@REM pyinstaller ./apps/app_win.spec
@REM deactivate;

uv run --no-sync --python 3.13 --with build python -m build --wheel
uv run --no-sync --python 3.14 --with build python -m build --wheel