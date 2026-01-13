import pyautogui
import time
import keyboard
import random
def hold_key_down(key, duration):
    """
    Holds a specified key down for a given duration in seconds.
    """
    print(f"Holding down the '{key}' key for {duration} seconds...")
    pyautogui.keyDown(key)
    time.sleep(duration)  # The key is held during this sleep period
    pyautogui.keyUp(key)
    print(f"Released the '{key}' key.")

keyLoop = ['w', 'a', 's', 'd']
timing = []
def main():
    timing = []
    running = True
    while running:
        time1 = random.uniform(4.1, 4.9)
        time2 = random.uniform(0.5, 1.0)
        timing.append(time1)
        timing.append(time2)
        timing.append(time1)
        timing.append(time2)
        for i in range(len(keyLoop)):
            looptime = time.perf_counter()
            run = True
            while run:
                passed = time.perf_counter()-looptime
                pyautogui.keyDown(keyLoop[i])
                if passed > timing[i]:
                    pyautogui.keyUp(keyLoop[i])
                    run = False
                print(passed)
                if keyboard.is_pressed('esc'):
                    running = False
                    run = False
                    break
        timing = []
main()