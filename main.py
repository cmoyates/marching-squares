# Example file showing a basic pygame "game loop"
from perlin_noise import PerlinNoise
import pygame
from math import ceil

WIDTH = 640
HEIGHT = 360
DOT_SPACING = 20

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

noise = PerlinNoise(octaves=3.5, seed=777)

while running:
    # poll for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("grey")

    for x in range(0, WIDTH + DOT_SPACING, DOT_SPACING):
        for y in range(0, HEIGHT + DOT_SPACING, DOT_SPACING):
            n = noise([x / WIDTH, y / HEIGHT])
            brightness = ceil(n) * 255
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 5)

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
