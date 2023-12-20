rm -rf ./dist/
python3 -m build
pyinstaller --onefile app.py
