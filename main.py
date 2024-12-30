from perlin_noise import PerlinNoise
import pygame
from math import floor

WIDTH = 640
HEIGHT = 360
DOT_SPACING = 20

MARCHING_SQUARES_LINES: list[list[float]] = [
    [],
    [[0, 0.5], [0.5, 1]],
    [[0.5, 1], [1, 0.5]],
    [[0, 0.5], [1, 0.5]],
    [[0.5, 0], [1, 0.5]],
    [[0, 0.5], [0.5, 0], [0.5, 1], [1, 0.5]],
    [[0.5, 0], [0.5, 1]],
    [[0, 0.5], [0.5, 0]],
    [[0, 0.5], [0.5, 0]],
    [[0.5, 0], [0.5, 1]],
    [[0, 0.5], [0.5, 1], [0.5, 0], [1, 0.5]],
    [[0.5, 0], [1, 0.5]],
    [[0, 0.5], [1, 0.5]],
    [[0.5, 1], [1, 0.5]],
    [[0, 0.5], [0.5, 1]],
    [],
]

# pygame setup
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

noise = PerlinNoise(octaves=3.5, seed=777)

sampled_noise = []

for x in range(0, WIDTH + DOT_SPACING, DOT_SPACING):
    sampled_noise_row = []
    for y in range(0, HEIGHT + DOT_SPACING, DOT_SPACING):
        n = noise([x / WIDTH, y / HEIGHT])
        sampled_noise_row.append(floor(n + 1))
    sampled_noise.append(sampled_noise_row)

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

    for x in range(WIDTH // DOT_SPACING + 1):
        for y in range(HEIGHT // DOT_SPACING + 1):
            noise_at_point = sampled_noise[x][y]
            brightness = noise_at_point * 255
            pygame.draw.circle(
                screen,
                (brightness, brightness, brightness),
                (x * DOT_SPACING, y * DOT_SPACING),
                5,
            )

    for x in range(WIDTH // DOT_SPACING):
        for y in range(HEIGHT // DOT_SPACING):
            noise_top_left = sampled_noise[x][y]
            noise_top_right = sampled_noise[x + 1][y]
            noise_bottom_left = sampled_noise[x][y + 1]
            noise_bottom_right = sampled_noise[x + 1][y + 1]

            lines_index = (
                noise_top_left * 8
                + noise_top_right * 4
                + noise_bottom_right * 2
                + noise_bottom_left
            )

            lines_points: list[float] = MARCHING_SQUARES_LINES[lines_index]
            for i in range(0, len(lines_points), 2):
                start = lines_points[i]
                end = lines_points[i + 1]
                start_x = (x + start[0]) * DOT_SPACING
                start_y = (y + start[1]) * DOT_SPACING
                end_x = (x + end[0]) * DOT_SPACING
                end_y = (y + end[1]) * DOT_SPACING
                pygame.draw.line(screen, "black", (start_x, start_y), (end_x, end_y))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
