import win32api
from win32api import GetSystemMetrics
import win32con
import pygame
import win32gui
import pyautogui

pygame.init()
screen = pygame.display.set_mode((GetSystemMetrics(0), GetSystemMetrics(1)), pygame.FULLSCREEN, pygame.NOFRAME)  # For borderless, use pygame.NOFRAME
done = False
fuchsia = (255, 0, 128)  # Transparency color
dark_red = (139, 0, 0)

# Set window transparency color
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                       win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*fuchsia), 0, win32con.LWA_COLORKEY)

# Make the window always on top
win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

# Some controls
block = 0
block1 = 0

# You can render some text
white = (255, 255, 255)
blue = (0, 0, 255)
font = pygame.font.Font('freesansbold.ttf', 32) 
texto = font.render('press "z" to define one corner and again to define the rectangle, it will take a screenshot', True, white, blue)

while not done:
    keys = pygame.key.get_pressed()
    pygame.time.delay(50)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    # This controls the actions at starting and end point
    if block1 == 0:
        if keys[pygame.K_z]:
            if block == 0:
                block = 1
                n = win32gui.GetCursorPos()
            else:
                done = True
                break
            # this prevents double checks, can be handled also by using events
            block1 = 10
        else:
            m = win32gui.GetCursorPos()
    else:
        block1 -= 1        

    screen.fill(fuchsia)  # Transparent background
    # this will render some text
    screen.blit(texto, (0, 0))
    # This will draw your rectangle
    if block == 1:
        pygame.draw.line(screen, dark_red, (n[0], n[1]), (m[0], n[1]), 1)
        pygame.draw.line(screen, dark_red, (n[0], m[1]), (m[0], m[1]), 1)
        pygame.draw.line(screen, dark_red, (n[0], n[1]), (n[0], m[1]), 1)
        pygame.draw.line(screen, dark_red, (m[0], n[1]), (m[0], m[1]), 1)
        pygame.draw.rect(screen, dark_red, (min(n[0], m[0]), min(n[1], m[1]), abs(m[0] - n[0]), abs(m[1] - n[1])), 1)

        # Check for mouse clicks
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:  # Left mouse button is clicked
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Check if the click is within the region of the rectangle
            if min(n[0], m[0]) <= mouse_x <= max(n[0], m[0]) and min(n[1], m[1]) <= mouse_y <= max(n[1], m[1]):
                # Forward the click to the underlying applications
                pyautogui.click(x=mouse_x, y=mouse_y)

    pygame.display.update()

pygame.display.quit()
pyautogui.screenshot(region=(min(n[0], m[0]), min(n[1], m[1]), abs(m[0] - n[0]), abs(m[1] - n[1])))
