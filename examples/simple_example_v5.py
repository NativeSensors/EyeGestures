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
pygame.display.set_caption("EyeGestures v5 (Reservoir Computing) Example")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)  # Set the font to bold

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v5

# Initialize EyeGestures V5 with reservoir parameters
gestures = EyeGestures_v5(reservoir_size=20, leak_rate=0.3)
cap = VideoCapture(0)

# Set up colors
RED = (255, 0, 100)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
BLANK = (0, 0, 0)
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
            # Adjust reservoir parameters dynamically
            elif event.key == pygame.K_1:
                gestures.setReservoirParams(reservoir_size=50, leak_rate=0.3)
                print("Reservoir size set to 50")
            elif event.key == pygame.K_2:
                gestures.setReservoirParams(reservoir_size=100, leak_rate=0.3)
                print("Reservoir size set to 100")
            elif event.key == pygame.K_3:
                gestures.setReservoirParams(reservoir_size=200, leak_rate=0.3)
                print("Reservoir size set to 200")
            elif event.key == pygame.K_4:
                gestures.setReservoirParams(reservoir_size=100, leak_rate=0.1)
                print("Leak rate set to 0.1")
            elif event.key == pygame.K_5:
                gestures.setReservoirParams(reservoir_size=100, leak_rate=0.5)
                print("Leak rate set to 0.5")

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
        pygame.draw.circle(screen, BLUE, calib_point, 50)
    else:
        pass

    pygame.draw.circle(screen, RED, point, 50)
    
    # Display reservoir parameters
    reservoir_text = f"Reservoir: {gestures.reservoir_size} neurons, Leak Rate: {gestures.leak_rate}"
    text_surface = bold_font.render(reservoir_text, True, WHITE)
    screen.blit(text_surface, (20, 20))
    
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()