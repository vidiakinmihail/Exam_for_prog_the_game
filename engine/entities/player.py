import pygame


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.velocity = pygame.Vector2(0, 0)
        self.speed = 220
        self.jump_power = 420
        self.gravity = 1200
        self.on_ground = False

    def jump(self):
        if self.on_ground:
            self.velocity.y = -self.jump_power
            self.on_ground = False

    def update(self, dt, keys, platforms):
        movement = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement += 1

        self.rect.x += int(movement * self.speed * dt)

        self.velocity.y += self.gravity * dt
        self.rect.y += int(self.velocity.y * dt)

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform) and self.velocity.y >= 0:
                self.rect.bottom = platform.top
                self.velocity.y = 0
                self.on_ground = True

    def draw(self, surface, offset=(0, 0)):
        pygame.draw.rect(surface, (220, 220, 255), self.rect.move(-offset[0], -offset[1]))
