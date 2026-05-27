import pygame


class Level:
    def __init__(self, name="level_01"):
        self.name = name
        self.platforms = [
            pygame.Rect(0, 432, 800, 48),
            pygame.Rect(180, 350, 120, 24),
            pygame.Rect(360, 290, 140, 24),
        ]
        self.spawn_point = (80, 200)

    def draw(self, surface, color=(80, 90, 120)):
        for platform in self.platforms:
            pygame.draw.rect(surface, color, platform)
