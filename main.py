import pygame
from systems.map import Grid, Pathfinder, StageLoader
from settings import GRID_SIZE, CELL_SIZE, COLOR_GRID, COLOR_PATH

pygame.init()

grid = Grid()
pathfinder = Pathfinder()

loader = StageLoader()
stage = loader.load(1)

grid.load_layout(stage["layout"], stage["start"], stage["end"])
grid.path = pathfinder.find_path(grid)

screen = pygame.display.set_mode(
    (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)
)

clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    grid.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()