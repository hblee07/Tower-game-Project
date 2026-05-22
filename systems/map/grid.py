import pygame
from collections import deque
from settings import *
EMPTY = 0
OBSTACLE = 1
TOWER = 2
START = 3
END = 4


class Grid:
    def __init__(self):
        self.cells = [[EMPTY] * GRID_SIZE for _ in range(GRID_SIZE)]

        self.start = (0, 0)
        self.end = (GRID_SIZE - 1, GRID_SIZE - 1)

        self.path = []

    def is_valid(self, col, row):
        return 0 <= col < GRID_SIZE and 0 <= row < GRID_SIZE

    def load_layout(self, layout, start, end):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.cells[r][c] = layout[r][c]

        self.start = start
        self.end = end

        self.cells[start[1]][start[0]] = START
        self.cells[end[1]][end[0]] = END

    def draw(self, surface):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):

                rect = pygame.Rect(
                    col * CELL_SIZE,
                    row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                color = COLOR_GRID

                if (col, row) in self.path:
                    color = COLOR_PATH

                if self.cells[row][col] == OBSTACLE:
                    color = (100,100,100)

                elif self.cells[row][col] == START:
                    color = (255,0,0)

                elif self.cells[row][col] == END:
                    color = (0,255,0)

                pygame.draw.rect(surface, color, rect)

                pygame.draw.rect(
                    surface,
                    (50,50,50),
                    rect,
                    1
                )


class Pathfinder: # bfs
    def find_path(self, grid):

        start = grid.start
        end = grid.end

        queue = deque([start])

        parent = {start: None}

        while queue:

            node = queue.popleft()

            if node == end:
                return self.reconstruct(parent, end)

            col, row = node

            for dc, dr in [(0,1), (0,-1), (1,0), (-1,0)]:

                nc = col + dc
                nr = row + dr

                if not grid.is_valid(nc, nr):
                    continue

                if grid.cells[nr][nc] == OBSTACLE:
                    continue

                if (nc, nr) not in parent:

                    parent[(nc, nr)] = node

                    queue.append((nc, nr))

        return []

    def reconstruct(self, parent, end):

        path = []

        node = end

        while node is not None:

            path.append(node)

            node = parent[node]

        path.reverse()

        return path


class StageLoader:
    def load(self, stage_id):

        import json
        import os

        path = os.path.join(
            "systems",
            "map",
            "stages",
            f"stage{stage_id}.json"
        )

        with open(path, "r") as f:
            data = json.load(f)

        data["start"] = tuple(data["start"])
        data["end"] = tuple(data["end"])

        return data