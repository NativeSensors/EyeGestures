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
gestures.uploadCalibrationMap([[1,0],[1,1],[0,1],[0.01,0.01],[0.5,0.5],[0.5,1],[0.5,0],[0,0.5],[1,0.5]])
gestures.enableCNCalib()
gestures.setClassicalImpact(2)
gestures.setFixation(1.0)
cap = VideoCapture(0)

# Initialize Pygame
pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen
screen = pygame.display.set_mode((screen_width, screen_height))
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

    calibrate = (iterator <= 600)
    iterator += 1

    event, calibration = gestures.step(frame, calibrate, screen_width, screen_height, context="my_context")
    
    screen.fill((0, 0, 0))
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (400, 400))

    if event is not None or calibration is not None:
        # Display frame on Pygame screen
        screen.blit(frame, (0, 0))
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render(f'{event.fixation}', False, (0, 0, 0))
        screen.blit(text_surface, (0,0))
        if calibrate:
            # pygame.draw.circle(screen, GREEN, fit_point, calibration_radius)
            pygame.draw.circle(screen, BLUE, calibration.point, calibration.acceptance_radius)
        else:
            pygame.draw.circle(screen, YELLOW, calibration.point, calibration.acceptance_radius)
        pygame.draw.circle(screen, RED, event.point, 50)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
