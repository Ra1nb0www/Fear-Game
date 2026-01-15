import pygame, random, time
import sys
import os
import ctypes
import traceback
import math
from maze import generate_maze
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
dx = 0.0
dy = 0.0
old_x = 0.0
old_y = 0.0
currency = 0

# --- Minimal maze integration: generate walls/doors and spawn player at entrance ---
# Only change: generate MAZE_WALLS/MAZE_DOORS here (editable) and set initial center to entrance

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
        get_input()
        #print(input_list)
        angle = process_direction()
        movement()
        playerr = playerv(angle)
        process_objects(playerr[1])  # Pass player's bounding rect for collision
        visuals(playerr)
        # `movement()` advances the clock/timing; avoid double tick here.
    pygame.quit()
    sys.exit()

def movement():
    global angle, center, old_x, old_y
    dt = clock.tick(60) / 1000.0
    forward = False
    backward = False
    for item in direction_list:
        if item == 'space':
            forward = True
            backward = False
        if item == 'shift':
            forward = False
            backward = True
    if forward:
        old_x, old_y = center[0], center[1]
        rad = math.radians(angle)
        dx = -math.sin(rad)
        dy = -math.cos(rad)
        center[0] += dx * speed * dt
        center[1] += dy * speed * dt
    if backward:
        old_x, old_y = center[0], center[1]
        rad = math.radians(angle)
        dx = -math.sin(rad)
        dy = -math.cos(rad)
        center[0] -= dx * speed * dt
        center[1] -= dy * speed * dt

    

def process_objects(player_rect):
    global PCList, center, old_x, old_y, MAZE_WALLS, MAZE_DOORS
    relative_posx = screen_width // 2 - center[0]
    relative_posy = screen_height // 2 - center[1]
    PCList = []
    # build screen-space wall rects each frame from MAZE_WALLS / MAZE_DOORS true positions
    walls_list = []
    for item in MAZE_WALLS:
        w = item["rect"].width
        h = item["rect"].height
        sx = int(relative_posx + item["true_posx"])
        sy = int(relative_posy + item["true_posy"])
        walls_list.append({"rect": pygame.Rect(sx, sy, w, h), "color": item.get("color", darker_green), "type": item.get("type", "wall"), "true_posx": item["true_posx"], "true_posy": item["true_posy"]})
    doors_list = []
    for item in MAZE_DOORS:
        w = item["rect"].width
        h = item["rect"].height
        sx = int(relative_posx + item["true_posx"])
        sy = int(relative_posy + item["true_posy"])
        # ensure doors are visible and marked as doors
        doors_list.append({"rect": pygame.Rect(sx, sy, w, h), "color": item.get("color", red), "type": "door", "true_posx": item["true_posx"], "true_posy": item["true_posy"]})
    # Use the walls generated by the maze directly (maze.generate_maze already removes walls replaced by doors)
    PCList.append(walls_list)
    # append doors last so they draw on top
    PCList.append(doors_list)
    for list in PCList:
        for item in list:
            # skip doors for collision checks
            if item.get("type") == "door":
                continue
            if is_colliding(player_rect.x, player_rect.y, player_rect.width, player_rect.height, item["rect"].x, item["rect"].y, item["rect"].width, item["rect"].height):
                # Try resolving collision by reverting only X or only Y (fix diagonal tunneling)
                sx_if_x_revert = int(screen_width // 2 - old_x + item["true_posx"])
                sy_if_x_revert = int(screen_height // 2 - center[1] + item["true_posy"])
                coll_if_x = is_colliding(player_rect.x, player_rect.y, player_rect.width, player_rect.height, sx_if_x_revert, sy_if_x_revert, item["rect"].width, item["rect"].height)
                sx_if_y_revert = int(screen_width // 2 - center[0] + item["true_posx"])
                sy_if_y_revert = int(screen_height // 2 - old_y + item["true_posy"])
                coll_if_y = is_colliding(player_rect.x, player_rect.y, player_rect.width, player_rect.height, sx_if_y_revert, sy_if_y_revert, item["rect"].width, item["rect"].height)
                if not coll_if_x:
                    center[0] = old_x
                elif not coll_if_y:
                    center[1] = old_y
                else:
                    center[0], center[1] = old_x, old_y
                return
    


def get_input():
    # Pump events so key state updates even without an event loop
    pygame.event.pump()
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
    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
        desired.append('shift')
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

def visuals(player):
    global PCList
    screen.fill(background_color)
    screen.blit(player[0], player[1])
    for list in PCList:
        for item in list:
            pygame.draw.rect(screen, item["color"], item["rect"])
        
    pygame.display.flip()

def is_colliding(px, py, pw, ph, ox, oy, ow, oh):
    return (
        px < ox + ow and
        px + pw > ox and
        py < oy + oh and
        py + ph > oy
    )
try:
    # editable maze parameters
    _maze_cols = 20
    _maze_rows = 20
    _maze_cell_size = 600
    _maze_wall_thickness = 40
    _maze_origin_x = -10
    _maze_origin_y = -10
    _maze_num_doors = 1
    MAZE_WALLS, MAZE_DOORS, MAZE_ENT, MAZE_EXIT = generate_maze(_maze_cols, _maze_rows, cell_size=_maze_cell_size, wall_thickness=_maze_wall_thickness, origin_x=_maze_origin_x, origin_y=_maze_origin_y, relative_posx=0, relative_posy=0, seed=None, num_doors=_maze_num_doors)
    # spawn the player at the entrance cell (world coordinates) — place in cell center
    _er, _ec = MAZE_ENT
    center[0] = _maze_origin_x + _ec * _maze_cell_size + _maze_cell_size / 2
    center[1] = _maze_origin_y + _er * _maze_cell_size + _maze_cell_size / 2
    # spawn safety: if the player's screen-centered rect overlaps any wall, nudge the spawn
    try:
        # player bounding box used in playerv()
        preg_w, preg_h = 75, 100
        attempts = 8
        for i in range(attempts):
            relative_posx = screen_width // 2 - center[0]
            relative_posy = screen_height // 2 - center[1]
            px = screen_width // 2 - preg_w // 2
            py = screen_height // 2 - preg_h // 2
            collision = False
            for w in MAZE_WALLS:
                sx = int(relative_posx + w["true_posx"])
                sy = int(relative_posy + w["true_posy"])
                if is_colliding(px, py, preg_w, preg_h, sx, sy, w["rect"].width, w["rect"].height):
                    collision = True
                    break
            if not collision:
                break
            # nudge down/up alternating a fraction of a cell to escape walls
            shift = (_maze_cell_size // 4) * (1 if (i % 2 == 0) else -1)
            center[1] += shift
    except Exception:
        pass
except Exception:
    MAZE_WALLS = []
    MAZE_DOORS = []
    MAZE_ENT = (0, 0)
    MAZE_EXIT = (0, 0)
main()
