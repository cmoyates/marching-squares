from perlin_noise import PerlinNoise
import pygame
from math import floor, ceil
from PIL import Image
from time import time

WIDTH = 640
HEIGHT = 360

DOT_SPACING = 20
DOT_RADIUS = 5

NOISE_STEPS = 3

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
    global sampled_noise, dots, holding_left_mouse

    if not holding_left_mouse:
        return

    for x in range(WIDTH // DOT_SPACING + 1):
        for y in range(HEIGHT // DOT_SPACING + 1):
            if dots[x][y]:
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
            brightness = min(max(brightness, 0), 255)
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

dots = []

holding_cmd = False
holding_left_mouse = False
mouse_positon = None


def main():
    # PyGame Setup
    pygame.init()
    pygame.display.set_caption("Marching Squares Heightmap Generator")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    noise = PerlinNoise(octaves=3.5, seed=time())

    global sampled_noise, holding_left_mouse, holding_cmd, mouse_positon

    # Generate and sample the noise

    min_sample = None
    max_sample = None

    for x in range(0, WIDTH + DOT_SPACING, DOT_SPACING):
        sampled_noise_row = []
        for y in range(0, HEIGHT + DOT_SPACING, DOT_SPACING):
            sample = noise([x / WIDTH, y / HEIGHT])
            sample_0_to_1 = (sample + 1) / 2

            if min_sample is None or sample_0_to_1 < min_sample:
                min_sample = sample_0_to_1
            if max_sample is None or sample_0_to_1 > max_sample:
                max_sample = sample_0_to_1

            sampled_noise_row.append(sample_0_to_1)
        sampled_noise.append(sampled_noise_row)

    # Normalize the sampled noise
    for x in range(WIDTH // DOT_SPACING + 1):
        for y in range(HEIGHT // DOT_SPACING + 1):
            sampled_noise[x][y] = floor(
                (sampled_noise[x][y] - min_sample)
                * (NOISE_STEPS)
                / (max_sample - min_sample)
            )

    # Populate the dots
    for x in range(WIDTH // DOT_SPACING + 1):
        dots_row = []
        for y in range(HEIGHT // DOT_SPACING + 1):
            dots_row.append(False)
        dots.append(dots_row)

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
                    holding_left_mouse = True
                    mouse_positon = pygame.mouse.get_pos()
                elif event.button == 4:
                    if holding_left_mouse:
                        increment_selected_noise(True)
                elif event.button == 5:
                    if holding_left_mouse:
                        increment_selected_noise(False)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and holding_left_mouse:
                    holding_left_mouse = False
                    mouse_positon = None
                    for x in range(WIDTH // DOT_SPACING + 1):
                        for y in range(HEIGHT // DOT_SPACING + 1):
                            dots[x][y] = False
            elif event.type == pygame.MOUSEMOTION:
                if holding_left_mouse:
                    mouse_positon = pygame.mouse.get_pos()

        # Reset the screen
        screen.fill("grey")

        for x in range(WIDTH // DOT_SPACING + 1):
            for y in range(HEIGHT // DOT_SPACING + 1):
                noise_at_point = sampled_noise[x][y]
                brightness = int(noise_at_point * 255 / (NOISE_STEPS - 1))
                brightness = min(max(brightness, 0), 255) / 2
                color = (brightness, brightness, brightness)

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        (x - 0.5) * DOT_SPACING,
                        (y - 0.5) * DOT_SPACING,
                        DOT_SPACING,
                        DOT_SPACING,
                    ),
                )

        # Draw the lines
        for noise_step in range(NOISE_STEPS - 1):
            for x in range(WIDTH // DOT_SPACING):
                for y in range(HEIGHT // DOT_SPACING):
                    noise_top_left = ceil(
                        (sampled_noise[x][y] - noise_step) / (NOISE_STEPS)
                    )
                    noise_top_right = ceil(
                        (sampled_noise[x + 1][y] - noise_step) / (NOISE_STEPS)
                    )
                    noise_bottom_right = ceil(
                        (sampled_noise[x + 1][y + 1] - noise_step) / (NOISE_STEPS)
                    )
                    noise_bottom_left = ceil(
                        (sampled_noise[x][y + 1] - noise_step) / (NOISE_STEPS)
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
                            screen, "white", (start_x, start_y), (end_x, end_y)
                        )

        # Select dots that are close enough to the mouse
        if holding_left_mouse:
            for x in range(WIDTH // DOT_SPACING + 1):
                for y in range(HEIGHT // DOT_SPACING + 1):
                    dot_position = (x * DOT_SPACING, y * DOT_SPACING)
                    dot_to_mouse_distance = (
                        mouse_positon[0] - dot_position[0]
                    ) ** 2 + (mouse_positon[1] - dot_position[1]) ** 2

                    if dot_to_mouse_distance < (DOT_SPACING + DOT_RADIUS) ** 2:
                        dots[x][y] = True

        min_dot_x = None
        max_dot_x = None
        min_dot_y = None
        max_dot_y = None

        # Draw the dots
        for x in range(WIDTH // DOT_SPACING + 1):
            for y in range(HEIGHT // DOT_SPACING + 1):
                if dots[x][y]:
                    if min_dot_x is None or x < min_dot_x:
                        min_dot_x = x
                    if max_dot_x is None or x > max_dot_x:
                        max_dot_x = x
                    if min_dot_y is None or y < min_dot_y:
                        min_dot_y = y
                    if max_dot_y is None or y > max_dot_y:
                        max_dot_y = y

                    pygame.draw.circle(
                        screen,
                        GREEN_RGB,
                        (x * DOT_SPACING, y * DOT_SPACING),
                        DOT_RADIUS,
                    )

        # Draw the selection box
        if (
            min_dot_x is not None
            and max_dot_x is not None
            and min_dot_y is not None
            and max_dot_y is not None
        ):
            pygame.draw.rect(
                screen,
                GREEN_RGB,
                (
                    min_dot_x * DOT_SPACING - DOT_RADIUS,
                    min_dot_y * DOT_SPACING - DOT_RADIUS,
                    (max_dot_x - min_dot_x) * DOT_SPACING + 2 * DOT_RADIUS,
                    (max_dot_y - min_dot_y) * DOT_SPACING + 2 * DOT_RADIUS,
                ),
                1,
            )

        # Flip() the display to put your work on screen
        pygame.display.flip()

        # Limit FPS to 60
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
