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
        pygame.draw.circle(surface, ITEM_COLOR, center, self.radius)
        pygame.draw.circle(surface, (120, 95, 20), center, self.radius, 2)


class Door(pygame.sprite.Sprite):
    """Синяя дверь финиша, которая появляется после сбора всех предметов."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, DOOR_SIZE[0], DOOR_SIZE[1])

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует дверь с учётом камеры."""
        rect = camera.apply(self.rect)
        pygame.draw.rect(surface, DOOR_COLOR, rect)
        pygame.draw.rect(surface, (20, 35, 110), rect, 3)
