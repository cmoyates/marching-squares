from perlin_noise import PerlinNoise
import pygame
from math import floor, ceil
from PIL import Image
from time import time

WIDTH = 640
HEIGHT = 360
DOT_SPACING = 20

NOISE_STEPS = 2

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

GREEN_RGB = (0, 255, 0)


def mix_colors(color1, color2, ratio=0.5):
    return (
        color1[0] * ratio + color2[0] * (1 - ratio),
        color1[1] * ratio + color2[1] * (1 - ratio),
        color1[2] * ratio + color2[2] * (1 - ratio),
    )


def increment_selected_noise(increase: bool = True):
    global sampled_noise

    if not min_drag_x or not max_drag_x or not min_drag_y or not max_drag_y:
        return

    for x in range(ceil(min_drag_x / DOT_SPACING), ceil(max_drag_x / DOT_SPACING)):
        for y in range(ceil(min_drag_y / DOT_SPACING), ceil(max_drag_y / DOT_SPACING)):
            if increase:
                sampled_noise[x][y] += 1.0
            else:
                sampled_noise[x][y] -= 1.0
            sampled_noise[x][y] = min(max(sampled_noise[x][y], 0), NOISE_STEPS - 1)


def save_image():
    image = Image.new("RGB", (WIDTH, HEIGHT))

    for x in range(WIDTH // DOT_SPACING + 1):
        for y in range(HEIGHT // DOT_SPACING + 1):
            noise_at_point = sampled_noise[x][y]
            brightness = int(noise_at_point * 255 / (NOISE_STEPS - 1))
            color = (brightness, brightness, brightness)

            image.paste(
                color,
                (
                    x * DOT_SPACING,
                    y * DOT_SPACING,
                    (x + 1) * DOT_SPACING,
                    (y + 1) * DOT_SPACING,
                ),
            )

    image.save("output.png")


sampled_noise = []

mouse_drag_start_positon = None
mouse_drag_current_position = None
min_drag_x = None
max_drag_x = None
min_drag_y = None
max_drag_y = None

holding_cmd = False


def main():
    # PyGame Setup
    pygame.init()
    pygame.display.set_caption("Marching Squares Heightmap Generator")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    noise = PerlinNoise(octaves=3.5, seed=time())

    global sampled_noise, mouse_drag_start_positon, mouse_drag_current_position, min_drag_x, max_drag_x, min_drag_y, max_drag_y, holding_cmd

    # Generate the noise
    for x in range(0, WIDTH + DOT_SPACING, DOT_SPACING):
        sampled_noise_row = []
        for y in range(0, HEIGHT + DOT_SPACING, DOT_SPACING):
            n = noise([x / WIDTH, y / HEIGHT])
            sampled_noise_row.append(floor((NOISE_STEPS) * ((n + 1) / 2)))
        sampled_noise.append(sampled_noise_row)

    # Game loop
    while running:
        # Poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_LMETA or event.key == pygame.K_RMETA:
                    holding_cmd = True
                elif event.key == pygame.K_s and holding_cmd:
                    save_image()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LMETA or event.key == pygame.K_RMETA:
                    holding_cmd = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_drag_start_positon = event.pos
                elif event.button == 4:
                    if mouse_drag_start_positon:
                        increment_selected_noise(True)
                elif event.button == 5:
                    if mouse_drag_start_positon:
                        increment_selected_noise(False)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and mouse_drag_start_positon:
                    mouse_drag_start_positon = None
                    mouse_drag_current_position = None
                    min_drag_x = None
                    max_drag_x = None
                    min_drag_y = None
                    max_drag_y = None
            elif event.type == pygame.MOUSEMOTION:
                if mouse_drag_start_positon:
                    mouse_drag_current_position = event.pos

        # Reset the screen
        screen.fill("grey")

        # Draw the lines
        for noise_step in range(NOISE_STEPS - 1):
            for x in range(WIDTH // DOT_SPACING):
                for y in range(HEIGHT // DOT_SPACING):
                    noise_top_left = ceil(
                        (sampled_noise[x][y] - noise_step) / (NOISE_STEPS - 1)
                    )
                    noise_top_right = ceil(
                        (sampled_noise[x + 1][y] - noise_step) / (NOISE_STEPS - 1)
                    )
                    noise_bottom_right = ceil(
                        (sampled_noise[x + 1][y + 1] - noise_step) / (NOISE_STEPS - 1)
                    )
                    noise_bottom_left = ceil(
                        (sampled_noise[x][y + 1] - noise_step) / (NOISE_STEPS - 1)
                    )

                    lines_index = (
                        noise_top_left * 8
                        + noise_top_right * 4
                        + noise_bottom_right * 2
                        + noise_bottom_left
                    )

                    lines_points: list[float] = MARCHING_SQUARES_LINES[int(lines_index)]
                    for i in range(0, len(lines_points), 2):
                        start = lines_points[i]
                        end = lines_points[i + 1]
                        start_x = (x + start[0]) * DOT_SPACING
                        start_y = (y + start[1]) * DOT_SPACING
                        end_x = (x + end[0]) * DOT_SPACING
                        end_y = (y + end[1]) * DOT_SPACING
                        pygame.draw.line(
                            screen, "black", (start_x, start_y), (end_x, end_y)
                        )

        # Draw the selection rectangle
        if mouse_drag_start_positon and mouse_drag_current_position:
            min_drag_x = min(
                mouse_drag_start_positon[0], mouse_drag_current_position[0]
            )
            max_drag_x = max(
                mouse_drag_start_positon[0], mouse_drag_current_position[0]
            )
            min_drag_y = min(
                mouse_drag_start_positon[1], mouse_drag_current_position[1]
            )
            max_drag_y = max(
                mouse_drag_start_positon[1], mouse_drag_current_position[1]
            )

            pygame.draw.rect(
                screen,
                "green",
                (
                    min_drag_x,
                    min_drag_y,
                    max_drag_x - min_drag_x,
                    max_drag_y - min_drag_y,
                ),
                2,
            )

        # Draw the dots
        for x in range(WIDTH // DOT_SPACING + 1):
            for y in range(HEIGHT // DOT_SPACING + 1):
                noise_at_point = sampled_noise[x][y]
                brightness = noise_at_point * 255 / (NOISE_STEPS - 1)
                color = (brightness, brightness, brightness)

                if mouse_drag_start_positon and mouse_drag_current_position:
                    if (
                        x * DOT_SPACING >= min_drag_x
                        and x * DOT_SPACING <= max_drag_x
                        and y * DOT_SPACING >= min_drag_y
                        and y * DOT_SPACING <= max_drag_y
                    ):
                        color = mix_colors(color, GREEN_RGB)

                pygame.draw.circle(
                    screen,
                    color,
                    (x * DOT_SPACING, y * DOT_SPACING),
                    5,
                )

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Limit FPS to 60
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
