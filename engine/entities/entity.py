import pygame


class Entity:
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = pygame.Vector2(0, 0)
        self.color = color
        self.alive = True

    def move_x(self, amount):
        self.rect.x += int(amount)

    def move_y(self, amount):
        self.rect.y += int(amount)

    def update(self, dt):
        raise NotImplementedError

    def draw(self, surface, offset=(0, 0)):
        pygame.draw.rect(surface, self.color, self.rect.move(-offset[0], -offset[1]))