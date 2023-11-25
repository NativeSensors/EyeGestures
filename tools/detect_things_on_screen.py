import pyautogui
import easyocr
import time 

# Capture a screenshot
screenshot = pyautogui.screenshot()

# Convert the screenshot to an image file format used by pytesseract
image_file = 'screenshot.png'
screenshot.save(image_file )
reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
now = time.time()
result = reader.readtext(image_file )
# print(f"processing took: {time.time() - now}")
# print(result)