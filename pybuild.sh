rm -rf ./dist/
python3 -m build
pyinstaller --onefile --add-data "/home/wallace/.local/lib/python3.10/site-packages/cv2/data/haarcascade_frontalface_default.xml:." app.py
