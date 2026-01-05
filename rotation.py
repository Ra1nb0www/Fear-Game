import pygame
import math

pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
background_color = (0, 0, 0)
clock = pygame.time.Clock()

# Rectangle surface (width, height) — this is the player and stays fixed on screen
rect_size = (200, 100)
rect_color = (0, 200, 250)
rect_surface = pygame.Surface(rect_size, pygame.SRCALPHA)
rect_surface.fill(rect_color)

# Direction indicator (drawn on top of the rectangle surface so it rotates together)
indicator_size = (40, 20)
indicator_color = (200, 50, 50)
ind_w, ind_h = indicator_size
rect_w, rect_h = rect_size
pygame.draw.rect(rect_surface, indicator_color, (rect_w // 2 - ind_w // 2, 0, ind_w, ind_h))
pygame.draw.line(rect_surface, (255, 255, 255), (rect_w // 2, rect_h // 2), (rect_w // 2, 0), 2)

# Player angle and fixed screen center
angle = 0
player_screen_center = (screen_width // 2, screen_height // 2)

# Player position in world coordinates (the player stays at screen center; world moves around them)
player_world_pos = [0.0, 0.0]

# Some example world objects at fixed world positions
world_objects = [
    {"pos": [0.0, -400.0], "color": (255, 200, 0), "radius": 24},
    {"pos": [300.0, 100.0], "color": (0, 200, 100), "radius": 18},
    {"pos": [-250.0, 200.0], "color": (200, 50, 200), "radius": 14},
]

speed = 240.0  # pixels per second (player movement in world space)

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # rotate player (still rotates on-screen)
    angle = (angle + 120 * dt) % 360

    # movement controls: move player in world space; player stays visually centered
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        rad = math.radians(angle)
        dx = -math.sin(rad)
        dy = -math.cos(rad)
        player_world_pos[0] += dx * speed * dt
        player_world_pos[1] += dy * speed * dt
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        rad = math.radians(angle)
        dx = -math.sin(rad)
        dy = -math.cos(rad)
        player_world_pos[0] -= dx * speed * dt
        player_world_pos[1] -= dy * speed * dt

    # compute world offset so objects are drawn relative to the player's world position
    world_offset_x = player_screen_center[0] - player_world_pos[0]
    world_offset_y = player_screen_center[1] - player_world_pos[1]

    screen.fill(background_color)

    # draw world objects shifted by world offset
    for obj in world_objects:
        screen_x = int(obj["pos"][0] + world_offset_x)
        screen_y = int(obj["pos"][1] + world_offset_y)
        pygame.draw.circle(screen, obj["color"], (screen_x, screen_y), obj["radius"])

    # draw player at fixed screen center (rotated)
    rotated_surface = pygame.transform.rotate(rect_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=player_screen_center)
    screen.blit(rotated_surface, rotated_rect)

    pygame.display.flip()

pygame.quit()