import pygame
from settings import SCREEN_W, SCREEN_H, FPS
from systems.scenes import SceneManager
from systems.save import SaveManager


def main():
    pygame.init()
    pygame.display.set_caption('Tower Defense Game')
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock = pygame.time.Clock()
    manager = SceneManager(screen, SaveManager())
    manager.replace('title')
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                manager.handle_event(event)
        manager.update(dt)
        manager.draw()
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()