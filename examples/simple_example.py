import pygame
import cv2 
import numpy as np
from eyeGestures.utils import VideoCapture
from eyeGestures.eyegestures import EyeGestures

gestures = EyeGestures(500,500,250,250,285,115)

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

clock = pygame.time.Clock()

# Main game loop
running = True
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

    cursor_x, cursor_y = 0, 0
    try:
        event = gestures.estimate(
            frame,
            "main",
            True, # set calibration - switch to False to stop calibration
            screen_width,
            screen_height,
            0, 0, 0.8,10)
    
        cursor_x, cursor_y = event.point_screen[0],event.point_screen[1]
        # frame = pygame.transform.scale(frame, (400, 400))
    
        
    except Exception as e:
        print(f"exception: {e}")

    screen.fill((0, 0, 0))
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (400, 400))
    
    # Display frame on Pygame screen
    screen.blit(frame, (0, 0))
    pygame.draw.circle(screen, RED, (cursor_x, cursor_y), 100)
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
cap.release()
