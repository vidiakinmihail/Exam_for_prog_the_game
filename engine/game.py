import sys

import pygame

from config import FPS, WINDOW_SIZE, WINDOW_TITLE
from engine.scenes.title_scene import TitleScene


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_scene = TitleScene(self)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    self.quit()

            self.current_scene.handle_events(events)
            self.current_scene.update(dt)
            self.current_scene.draw(self.screen)

            pygame.display.flip()

        self.quit()

    def switch_scene(self, scene):
        self.current_scene = scene

    def quit(self):
        self.running = False
        pygame.quit()
        sys.exit()
