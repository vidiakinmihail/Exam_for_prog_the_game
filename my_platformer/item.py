"""Собираемые предметы и дверь финиша."""

from __future__ import annotations

import pygame

from .config import DOOR_COLOR, DOOR_SIZE, ITEM_COLOR, ITEM_RADIUS


class Item(pygame.sprite.Sprite):
    """Жёлтый круг-собираемый предмет."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.radius = ITEM_RADIUS
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)

    def collides_with(self, player_rect: pygame.Rect) -> bool:
        """Проверяет пересечение круга с прямоугольником игрока."""
        closest_x = max(player_rect.left, min(self.center_x, player_rect.right))
        closest_y = max(player_rect.top, min(self.center_y, player_rect.bottom))
        dx = self.center_x - closest_x
        dy = self.center_y - closest_y
        return dx * dx + dy * dy <= self.radius * self.radius

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует предмет с учётом камеры."""
        if not self.alive():
            return
        center = (self.center_x - camera.camera.x, self.center_y - camera.camera.y)
        glow = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 220, 80, 45), (glow.get_width() // 2, glow.get_height() // 2), self.radius + 4)
        surface.blit(glow, (center[0] - glow.get_width() // 2, center[1] - glow.get_height() // 2))
        pygame.draw.circle(surface, (255, 245, 180), center, self.radius)
        pygame.draw.circle(surface, ITEM_COLOR, center, self.radius - 2)
        pygame.draw.circle(surface, (120, 95, 20), center, self.radius, 2)
        pygame.draw.line(surface, (255, 255, 255), (center[0] - 4, center[1] - 5), (center[0], center[1] - 9), 2)
        pygame.draw.line(surface, (255, 255, 255), (center[0] + 2, center[1] - 2), (center[0] + 7, center[1] - 7), 2)


class Door(pygame.sprite.Sprite):
    """Синяя дверь финиша, которая появляется после сбора всех предметов."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, DOOR_SIZE[0], DOOR_SIZE[1])

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует дверь с учётом камеры."""
        rect = camera.apply(self.rect)
        glow = pygame.Surface((rect.width + 30, rect.height + 30), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (110, 160, 255, 50), (8, 8, rect.width + 12, rect.height + 12))
        surface.blit(glow, (rect.x - 15, rect.y - 15))

        body = rect.inflate(-2, -2)
        pygame.draw.rect(surface, (195, 225, 255), body, border_radius=6)
        inner = body.inflate(-8, -10)
        pygame.draw.rect(surface, DOOR_COLOR, inner, border_radius=5)
        pygame.draw.rect(surface, (20, 35, 110), body, 3, border_radius=6)
        pygame.draw.rect(surface, (250, 250, 255), (inner.x + 5, inner.y + 5, 5, inner.height - 10), border_radius=3)
