from collections import deque
import pygame
from settings import GRID_SIZE, TILE_SIZE, MAP_SIZE, EMPTY, WALL, PATH, START, END, GRID, STAGES

EMPTY_CELL = 0
WALL_CELL = 1
TOWER_CELL = 2
START_CELL = 3
END_CELL = 4

class MapManager:
    def __init__(self, stage_id=1):
        self.stage_id = stage_id
        self.stage = STAGES[stage_id]
        self.start = self.stage["start"]
        self.end = self.stage["end"]
        self.grid = [[EMPTY_CELL for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.path = []
        self.generate_stage()
        self.path = self.find_path()

    def generate_stage(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid[r][c] = EMPTY_CELL
        if self.stage_id == 1:
            for r in range(4, 27, 4):
                gap = 2 if (r // 4) % 2 else 26
                for c in range(1, 29):
                    if abs(c - gap) > 1:
                        self.grid[r][c] = WALL_CELL
            for c in range(6, 25, 6):
                for r in range(6, 26):
                    if r % 8 not in (1, 2):
                        self.grid[r][c] = WALL_CELL
        else:
            for c in range(4, 27, 5):
                gap = 15 if c % 2 == 0 else 7
                for r in range(2, 28):
                    if abs(r - gap) > 2:
                        self.grid[r][c] = WALL_CELL
            for r in (5, 24):
                for c in range(5, 25):
                    if c not in (14, 15):
                        self.grid[r][c] = WALL_CELL
        sr, sc = self.start
        er, ec = self.end
        self.grid[sr][sc] = START_CELL
        self.grid[er][ec] = END_CELL
        # Make sure direct neighborhoods are open.
        for rr, cc in [self.start, self.end]:
            for dr, dc in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
                r, c = rr+dr, cc+dc
                if self.in_bounds(r,c) and self.grid[r][c] == WALL_CELL:
                    self.grid[r][c] = EMPTY_CELL

    def in_bounds(self, r, c):
        return 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE

    def is_walkable(self, r, c, ignore_tower=None):
        if not self.in_bounds(r, c):
            return False
        if ignore_tower == (r, c):
            return True
        return self.grid[r][c] in (EMPTY_CELL, START_CELL, END_CELL)

    def is_placeable(self, r, c):
        return self.in_bounds(r, c) and self.grid[r][c] == EMPTY_CELL

    def find_path(self, start=None, end=None):
        start = start or self.start
        end = end or self.end
        q = deque([start])
        came = {start: None}
        while q:
            cur = q.popleft()
            if cur == end:
                break
            r, c = cur
            for nr, nc in [(r+1,c),(r-1,c),(r,c+1),(r,c-1)]:
                if self.is_walkable(nr, nc) and (nr, nc) not in came:
                    came[(nr, nc)] = cur
                    q.append((nr, nc))
        if end not in came:
            return []
        path = []
        cur = end
        while cur is not None:
            path.append(cur)
            cur = came[cur]
        path.reverse()
        return path

    def place_tower_cell(self, r, c):
        if not self.is_placeable(r, c):
            return False
        self.grid[r][c] = TOWER_CELL
        new_path = self.find_path()
        if not new_path:
            self.grid[r][c] = EMPTY_CELL
            return False
        self.path = new_path
        return True

    def remove_tower_cell(self, r, c):
        if self.in_bounds(r, c) and self.grid[r][c] == TOWER_CELL:
            self.grid[r][c] = EMPTY_CELL
            self.path = self.find_path()

    def pixel_to_cell(self, x, y):
        if x < 0 or y < 0 or x >= MAP_SIZE or y >= MAP_SIZE:
            return None
        return y // TILE_SIZE, x // TILE_SIZE

    def cell_to_pixel(self, r, c):
        return c * TILE_SIZE, r * TILE_SIZE

    def draw(self, screen):
        path_set = set(self.path)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                cell = self.grid[r][c]
                color = EMPTY
                if (r, c) in path_set:
                    color = PATH
                if cell == WALL_CELL:
                    color = WALL
                elif cell == START_CELL:
                    color = START
                elif cell == END_CELL:
                    color = END
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRID, rect, 1)
