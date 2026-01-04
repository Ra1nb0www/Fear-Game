import pygame, random, time
import sys
import os
import ctypes
import traceback
import math
def is_admin():
    """
    Check if the script is running with administrative privileges.
    Returns True if admin, False otherwise.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """
    Relaunch the current script with admin privileges.
    """
    try:
        # ShellExecuteW parameters:
        # hwnd, lpOperation, lpFile, lpParameters, lpDirectory, nShowCmd
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
    except Exception as e:
        print(f"Failed to elevate privileges: {e}")

#if __name__ == "__main__":
#    if is_admin():
#        pass
#    else:
#        print("⚠️ Not running as admin. Requesting elevation...")
#        run_as_admin()
#        sys.exit()
pygame.init()
info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
background_color = (0, 0, 0) 
clock = pygame.time.Clock()
white = (255, 255, 255)
green = (0, 255, 0)
darker_green = (0, 200, 0)
blue = (0, 0, 128)
black = (0, 0, 0)
greyish = (170, 170, 170)
light_blue = (0, 200, 250)
darker_red = (150, 0, 0)
red = (200, 0, 0)
file_names = ["currency"]
center = [0.0, 0.0]
speed = 500
def save(file):
    x = globals()[file]
    with open((file) + ".txt", "w") as file:
        file.write(str(x))


def wipe_files():
    for file in file_names:
        if file != "orbs":
            with open((file) + ".txt", "w") as file:
                file.write(str(0))
        else:
            with open((file) + ".txt", "w") as file:
                values = []
                for i in range(3):
                    values.append(0)
                for line in values:
                    file.write(f"{str(line)}\n")

def load_files():
    global currency
    Loaded = False
    while Loaded == False:
        try:
            with open("currency.txt", "r") as file:
                currency = int(file.read())
            Loaded = True
        except:
            wipe_files()

def pytext(text, x, y, font_size, color1, color2):
    font = pygame.font.Font('freesansbold.ttf', font_size)
    text = font.render(text, True, color1, color2)
    textRect = text.get_rect()
    textRect.center = (x, y)
    screen.blit(text, textRect)

def main():
    global direction_list, angle
    direction_list = []
    pygame.display.set_caption(f"Fear")
    load_files()
    angle = 0
    running = True
    while running:
        # Handle OS / pygame events so the window stays responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        get_input()
        #print(input_list)
        angle = process_direction()
        movement()
        playerr = playerv(angle)
        walls = process_objects()
        visuals(playerr, walls)
        clock.tick(60)
    pygame.quit()
    sys.exit()

def movement():
    global angle, center
    dt = clock.tick(60) / 1000.0
    move = False
    for item in direction_list:
        if item == 'space':
            move = True
    if move:
        rad = math.radians(angle)
        dx = -math.sin(rad)
        dy = -math.cos(rad)
        center[0] += dx * speed * dt
        center[1] += dy * speed * dt
    

def process_objects():
    relative_posx = screen_width // 2 - center[0]
    relative_posy = screen_height // 2 - center[1]
    walls = [
        {"rect": pygame.Rect(relative_posx, relative_posy, 50, 200), "color": darker_green, "type": "wall", "true_posx": 1000,  "true_posy": 1000}
        ]
    return walls

def get_input():
    global direction_list, input_lis
    # Use pygame's key state to avoid global hooks and keep window responsive
    keys = pygame.key.get_pressed()
    desired = []
    if keys[pygame.K_a]:
        desired.append('a')
    if keys[pygame.K_d]:
        desired.append('d')
    if keys[pygame.K_s]:
        desired.append('s')
    if keys[pygame.K_w]:
        desired.append('w')

    if keys[pygame.K_SPACE]:
        desired.append('space')
    # Sync direction_list to desired state
    # Remove keys not currently pressed
    for item in list(direction_list):
        if item not in desired:
            direction_list.remove(item)
    # Add newly pressed keys in order
    for item in desired:
        if item not in direction_list:
            direction_list.append(item)

def process_direction():
    global angle
    up = False
    down = False
    left = False
    right = False
    for item in direction_list:
        if item == 'a':
            right = False
            left = True
        if item == 'd':
            right = True
            left = False
        if item == 's':
            down = True
            up = False
        if item == 'w':
            down = False
            up = True
    if up and right:
        return 315
    if up and left:
        return 45
    if down and right:
        return 225
    if down and left:
        return 135
    if up:
        return 0
    if down:
        return 180
    if right:
        return 270
    if left:
        return 90
    return angle

def playerv(angle):
    center_pos = (screen_width // 2, screen_height // 2)
    rect_size = (75, 100)
    rect_color = (0, 200, 250)
    rect_surface = pygame.Surface(rect_size, pygame.SRCALPHA)
    rect_surface.fill(rect_color)
    indicator_size = (40, 20)
    indicator_color = (200, 50, 50)
    ind_w, ind_h = indicator_size
    rect_w, rect_h = rect_size
    pygame.draw.rect(rect_surface, indicator_color, (rect_w // 2 - ind_w // 2, 0, ind_w, ind_h))
    # Optional: draw a thin center line to emphasize forward direction
    pygame.draw.line(rect_surface, (255, 255, 255), (rect_w // 2, rect_h // 2), (rect_w // 2, 0), 2)
    rotated_surface = pygame.transform.rotate(rect_surface, angle)
    rotated_rect = rotated_surface.get_rect(center=center_pos)
    return (rotated_surface, rotated_rect)

def visuals(player, walls):
    screen.fill(background_color)
    screen.blit(player[0], player[1])
    for item in walls:
        pygame.draw.rect(screen, item["color"], item["rect"])
    pygame.display.flip()
main()
