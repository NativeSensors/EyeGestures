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
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Generate new random position for the cursor
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    calibrate = (iterator <= 1000)
    iterator += 1

    point, fit_point, blink, fixation, acceptance_radius, calibration_radius = gestures.step(frame, calibrate, screen_width, screen_height)


    screen.fill((0, 0, 0))
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (400, 400))

    # Display frame on Pygame screen
    screen.blit(frame, (0, 0))
    if calibrate:
        # pygame.draw.circle(screen, GREEN, fit_point, calibration_radius)
        pygame.draw.circle(screen, BLUE, fit_point, acceptance_radius)
    pygame.draw.circle(screen, RED, point, 50)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
cap.release()