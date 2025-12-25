import pygame, random, time
import sys
import os
import ctypes
import traceback

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
file_names = []

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
            num = 0
            with open((file) + ".txt", "w") as file:
                values = []
                for i in range(3):
                    values.append(0)
                for line in values:
                    file.write(f"{str(line)}\n")

def load_files():
    global currency, level, era, upgrade_1, upgrade_2, orbs
    orbs = []
    Loaded = True
    while Loaded == False:
        try:
            with open("currency.txt", "r") as file:
                currency = int(file.read())
            with open("level.txt", "r") as file:
                level = int(file.read())
            with open("era.txt", "r") as file:
                era = int(file.read())
            with open("upgrade_1.txt", "r") as file:
                upgrade_1 = int(file.read())
            with open("upgrade_2.txt", "r") as file:
                upgrade_2 = int(file.read())
            with open("orbs.txt", "r") as file:
                pre_orbs = (file.readlines())
                for line in pre_orbs:
                    orbs.append(int(line))
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
    pygame.display.set_caption(f"Fear")
    load_files()
    running = True
    while running:
        screen.fill(background_color)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        menu_rect = [
                {"rect": pygame.Rect(300, 100, 200, 100), "color": darker_green, "action": "rect1_clicked"},
                {"rect": pygame.Rect(1000, 100, 200, 100), "color": darker_red, "action": "rect2_clicked"},
                {"rect": pygame.Rect(520, 100, 200, 100), "color": red, "action": "rect3_clicked"}
            ]
        for item in menu_rect:
            pygame.draw.rect(screen, item["color"], item["rect"])
        pygame.display.flip()
        clock.tick(60)


main()
