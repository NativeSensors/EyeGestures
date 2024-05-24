import os
import sys
import cv2 
import pygame
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures_v1

gestures = EyeGestures_v1(285,115,80,15)

cap = VideoCapture(0)  

# Initialize Pygame
pygame.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Fullscreen Red Cursor")

# Set up colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()

# Main game loop
running = True
iterator = 0
calibrate = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Generate new random position for the cursor
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame,1)
    # frame = cv2.resize(frame, (360, 640))

    iterator += 1

    cursor_x, cursor_y = 0, 0
    event, calibration = gestures.step(
        frame,
        "main",
        calibrate, # set calibration - switch to False to stop calibration
        screen_width,
        screen_height,
        0, 0, 0.8,10)
    calibrate = calibration.calibration

    cursor_x, cursor_y = event.point[0],event.point[1]
    # frame = pygame.transform.scale(frame, (400, 400))

    screen.fill((0, 0, 0))
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (400, 400))

    # Display frame on Pygame screen
    screen.blit(frame, (0, 0))
    if calibration.point != (0,0):
        pygame.draw.circle(screen, BLUE, calibration.point, 100)
    pygame.draw.circle(screen, RED, (cursor_x, cursor_y), 100)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()