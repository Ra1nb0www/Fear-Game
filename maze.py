import random
import os
import pygame
from collections import deque


def generate_maze(cols,
                  rows,
                  cell_size=50,
                  wall_thickness=10,
                  origin_x=0,
                  origin_y=0,
                  relative_posx=0,
                  relative_posy=0,
                  color=(0,200,0),
                  seed=None,
                  entrance_cell=None,
                  exit_cell=None,
                  num_doors=0,
                  door_color=(200,0,0)):

    # use a local RNG; if seed is None, seed from os.urandom to ensure variability
    seed_val = seed if seed is not None else int.from_bytes(os.urandom(8), "big")
    rng = random.Random(seed_val)

    # cell walls: rows x cols
    # each cell has dict with top/right/bottom/left boolean
    walls = [[{"top": True, "right": True, "bottom": True, "left": True} for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]

    # DFS backtracker
    stack = [(0, 0)]
    visited[0][0] = True
    while stack:
        r, c = stack[-1]
        neighbors = []
        # (dr, dc, this_side, neighbor_side)
        for dr, dc, side, nside in [(-1, 0, "top", "bottom"), (1, 0, "bottom", "top"), (0, -1, "left", "right"), (0, 1, "right", "left")]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                neighbors.append((nr, nc, side, nside))
        if neighbors:
            nr, nc, side, nside = rng.choice(neighbors)
            walls[r][c][side] = False
            walls[nr][nc][nside] = False
            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

    # prepare lists; actual wall rects will be built after doors/entrance are applied
    wall_list = []
    doors_list = []
    t = int(wall_thickness)
    half_t = t // 2

    # handle entrance/exit defaults (top random and bottom random) and internal doors
    if entrance_cell is None:
        entrance_col = rng.randrange(cols)
        entrance_cell = (0, entrance_col)
    if exit_cell is None:
        exit_col = rng.randrange(cols)
        exit_cell = (rows - 1, exit_col)

    # create entrance door by clearing the relevant outer wall and adding to doors_list
    er, ec = entrance_cell
    if er == 0 and walls[er][ec].get("top", True):
        walls[er][ec]["top"] = False
        true_x = origin_x + ec * cell_size
        true_y = origin_y + er * cell_size - half_t
        rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, cell_size, t)
        doors_list.append({"rect": rect, "color": door_color, "type": "door", "true_posx": true_x, "true_posy": true_y})

    er, ec = exit_cell
    if er == rows - 1 and walls[er][ec].get("bottom", True):
        walls[er][ec]["bottom"] = False
        true_x = origin_x + ec * cell_size
        true_y = origin_y + rows * cell_size - half_t
        rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, cell_size, t)
        doors_list.append({"rect": rect, "color": door_color, "type": "door", "true_posx": true_x, "true_posy": true_y})

    # add some internal doors (openings that are not considered walls)
    tries = 0
    added = 0
    max_tries = num_doors * 10 + 50
    while added < num_doors and tries < max_tries:
        tries += 1
        r = rng.randrange(rows)
        c = rng.randrange(cols)
        # choose a random neighbor side that currently has a wall
        sides = [s for s, val in walls[r][c].items() if val and s in ("top", "right", "bottom", "left")]
        if not sides:
            continue
        side = rng.choice(sides)
        if side == "top":
            nr, nc, nside = r - 1, c, "bottom"
            render_cell = (r, c)
            true_x = origin_x + c * cell_size
            true_y = origin_y + r * cell_size - half_t
            rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, cell_size, t)
        elif side == "left":
            nr, nc, nside = r, c - 1, "right"
            true_x = origin_x + c * cell_size - half_t
            true_y = origin_y + r * cell_size
            rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, t, cell_size)
        elif side == "right":
            nr, nc, nside = r, c + 1, "left"
            # represented by neighbor's left wall
            true_x = origin_x + (c + 1) * cell_size - half_t
            true_y = origin_y + r * cell_size
            rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, t, cell_size)
        else:  # bottom
            nr, nc, nside = r + 1, c, "top"
            true_x = origin_x + c * cell_size
            true_y = origin_y + (r + 1) * cell_size - half_t
            rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, cell_size, t)

        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        # remove both sides and add to doors_list
        if walls[r][c].get(side, True):
            walls[r][c][side] = False
            walls[nr][nc][nside] = False
            doors_list.append({"rect": rect, "color": door_color, "type": "door", "true_posx": true_x, "true_posy": true_y})
            added += 1

    # Now build wall_list from the final `walls` matrix (after doors/entrance modifications)
    for r in range(rows):
        for c in range(cols):
            cell_x = origin_x + c * cell_size
            cell_y = origin_y + r * cell_size
            # top
            if walls[r][c]["top"]:
                true_x = cell_x
                true_y = cell_y - half_t
                rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, cell_size, t)
                wall_list.append({"rect": rect, "color": color, "type": "wall", "true_posx": true_x, "true_posy": true_y})
            # left
            if walls[r][c]["left"]:
                true_x = cell_x - half_t
                true_y = cell_y
                rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, t, cell_size)
                wall_list.append({"rect": rect, "color": color, "type": "wall", "true_posx": true_x, "true_posy": true_y})

    # outer right and bottom walls
    for r in range(rows):
        if walls[r][cols-1].get("right", True):
            true_x = origin_x + cols * cell_size - half_t
            true_y = origin_y + r * cell_size
            rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, t, cell_size)
            wall_list.append({"rect": rect, "color": color, "type": "wall", "true_posx": true_x, "true_posy": true_y})

    for c in range(cols):
        if walls[rows-1][c].get("bottom", True):
            true_x = origin_x + c * cell_size
            true_y = origin_y + rows * cell_size - half_t
            rect = pygame.Rect(relative_posx + true_x, relative_posy + true_y, cell_size, t)
            wall_list.append({"rect": rect, "color": color, "type": "wall", "true_posx": true_x, "true_posy": true_y})

    return wall_list, doors_list, entrance_cell, exit_cell


def is_solvable(cols, rows, wall_list, doors_list, cell_size=50, wall_thickness=10, origin_x=0, origin_y=0, entrance_cell=None, exit_cell=None):
    """Check if maze is solvable from entrance_cell to exit_cell ignoring doors.

    Treat any door in `doors_list` as an opening (i.e., not a wall) even if a matching wall exists in wall_list.
    Returns True if a path exists between entrance and exit cells using 4-way movement.
    """
    if entrance_cell is None:
        entrance_cell = (0, random.randrange(cols))
    if exit_cell is None:
        exit_cell = (rows - 1, random.randrange(cols))

    t = int(wall_thickness)
    half_t = t // 2

    def wall_blocking_between(r, c, nr, nc):
        # compute expected wall true coords and size between (r,c) and (nr,nc)
        if nr == r and nc == c + 1:
            # right wall of (r,c)
            true_x = origin_x + (c + 1) * cell_size - half_t
            true_y = origin_y + r * cell_size
            w, h = t, cell_size
        elif nr == r and nc == c - 1:
            true_x = origin_x + c * cell_size - half_t
            true_y = origin_y + r * cell_size
            w, h = t, cell_size
        elif nr == r - 1 and nc == c:
            true_x = origin_x + c * cell_size
            true_y = origin_y + r * cell_size - half_t
            w, h = cell_size, t
        elif nr == r + 1 and nc == c:
            true_x = origin_x + c * cell_size
            true_y = origin_y + (r + 1) * cell_size - half_t
            w, h = cell_size, t
        else:
            return True

        # if a door exists at that true position, it's not blocking
        for d in doors_list:
            if int(d.get("true_posx", d["rect"].x)) == int(true_x) and int(d.get("true_posy", d["rect"].y)) == int(true_y):
                return False

        # if a wall exists at that position, it's blocking
        for wobj in wall_list:
            if int(wobj.get("true_posx", wobj["rect"].x)) == int(true_x) and int(wobj.get("true_posy", wobj["rect"].y)) == int(true_y):
                return True
        return False

    # BFS
    q = deque()
    q.append(entrance_cell)
    seen = set([entrance_cell])
    while q:
        r, c = q.popleft()
        if (r, c) == exit_cell:
            return True
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            if (nr, nc) in seen:
                continue
            if wall_blocking_between(r, c, nr, nc):
                continue
            seen.add((nr, nc))
            q.append((nr, nc))
    return False


if __name__ == "__main__":
    # quick visual test (requires pygame display)
    pygame.init()
    # editable parameters (change these)
    cols = 20
    rows = 20
    cell_size = 50
    wall_thickness = 8
    origin_x = 50
    origin_y = 50
    num_doors = 3
    # make screen large enough to view the maze (clamped to a sensible max)
    screen_w = min(1600, origin_x * 2 + cols * cell_size + 100)
    screen_h = min(1200, origin_y * 2 + rows * cell_size + 100)
    screen = pygame.display.set_mode((screen_w, screen_h))
    clock = pygame.time.Clock()
    walls, doors, ent, ex = generate_maze(cols, rows, cell_size=cell_size, wall_thickness=wall_thickness, origin_x=origin_x, origin_y=origin_y, relative_posx=0, relative_posy=0, seed=None, num_doors=num_doors)
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
        screen.fill((0,0,0))
        for w in walls:
            pygame.draw.rect(screen, w["color"], w["rect"])
        for d in doors:
            pygame.draw.rect(screen, d["color"], d["rect"])
        print("solvable:", end=" ")
        print(is_solvable(cols, rows, walls, doors, cell_size=cell_size, wall_thickness=wall_thickness, origin_x=origin_x, origin_y=origin_y, entrance_cell=ent, exit_cell=ex))
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
