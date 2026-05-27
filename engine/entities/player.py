import pygame


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 220
        self.jump_power = 420
        self.on_ground = False

    def update(self, dt, keys):
        movement = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement += 1

        self.rect.x += int(movement * self.speed * dt)

    def draw(self, surface, offset=(0, 0)):
        pygame.draw.rect(surface, (220, 220, 255), self.rect.move(-offset[0], -offset[1]))
