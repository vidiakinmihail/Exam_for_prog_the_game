import pygame

from config import BACKGROUND_COLOR
from engine.entities.player import Player
from engine.levels.level import Level
from engine.scenes.base import BaseScene


class GameScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.level = Level()
        self.player = Player(*self.level.spawn_point)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.player.jump()

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.level.platforms)

    def draw(self, surface):
        surface.fill(BACKGROUND_COLOR)
        self.level.draw(surface)
        self.player.draw(surface)