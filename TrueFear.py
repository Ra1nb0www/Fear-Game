import pygame, random, time
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
    Loaded = False
    while Loaded == False:
        try:
            with open("currency.txt", "r") as file:
                currency = int(file.read())
        except:
            wipe_files()
def pytext(text, x, y, font_size, color1, color2):
    font = pygame.font.Font('freesansbold.ttf', font_size)
    text = font.render(text, True, color1, color2)
    textRect = text.get_rect()
    textRect.center = (x, y)
    screen.blit(text, textRect)
def main():
        load_files()
        menu_rect = [
                {"rect": pygame.Rect(300, 100, 200, 100), "color": darker_green, "action": "rect1_clicked"},
                {"rect": pygame.Rect(1000, 100, 200, 100), "color": darker_red, "action": "rect2_clicked"},
                {"rect": pygame.Rect(520, 100, 200, 100), "color": red, "action": "rect3_clicked"}
            ]
        for item in menu_rect:
            pygame.draw.rect(screen, item["color"], item["rect"])
        pygame.display.flip()
        clock.tick(60)