import pygame

from config import BACKGROUND_COLOR, TEXT_COLOR, WINDOW_SIZE
from engine.scenes.base import BaseScene


class TitleScene(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 32)
        self.small_font = pygame.font.SysFont("arial", 18)

    def draw(self, surface):
        surface.fill(BACKGROUND_COLOR)

        title = self.font.render("Platformer Prototype", True, TEXT_COLOR)
        hint = self.small_font.render("Structure is ready. Next: player, level, and camera.", True, TEXT_COLOR)

        surface.blit(title, title.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 20)))
        surface.blit(hint, hint.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 20)))
