import os
import sys
import cv2
import pygame
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures_v2

gestures = EyeGestures_v2()
gestures.uploadCalibrationMap([[0,0],[0,1],[1,0],[1,1]])
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
YELLOW = (255,255,0)

clock = pygame.time.Clock()

# Main game loop
running = True
iterator = 0
first = [0,0]
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False

    calibration = gestures.calibrationMat.getNextPoint(screen_width,screen_height)
    
    if calibration[0] == first[0] and calibration[1] == first[1]:
        screen.fill((0, 0, 0))

    if first[0] == 0 and first[1] == 0:
        first = calibration
    # Display frame on Pygame screen
    pygame.draw.circle(screen, YELLOW, calibration, 200)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(10)

# Quit Pygame
pygame.quit()
cap.release()
