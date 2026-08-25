import os
import sys
import cv2
import pygame
import numpy as np

pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeGestures v4 example")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)  # Set the font to bold

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eye_gestures.utils import VideoCapture
from eye_gestures import EyeGestures_v4

gestures = EyeGestures_v4()
cap = VideoCapture(0)

# Initialize Pygame
# Set up colors
RED = (255, 0, 100)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
BLANK = (0,0,0)
WHITE = (255, 255, 255)

clock = pygame.time.Clock()

# Main game loop
running = True
iterator = 0
prev_x = 0
prev_y = 0
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False


    # Generate new random position for the cursor
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    point, calibrate, calib_point = gestures.step(frame, screen_width, screen_height - 100)
    
    screen.fill((0, 0, 0))
    # Display frame on Pygame 
    if calibrate:
        if calib_point[0] != prev_x or calib_point[1] != prev_y:
            iterator += 1
            prev_x = calib_point[0]
            prev_y = calib_point[1]
        # pygame.draw.circle(screen, GREEN, fit_point, calibration_radius)
        pygame.draw.circle(screen, BLUE, calib_point, 50)
    else:
        pass

    pygame.draw.circle(screen, RED, point, 50)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
