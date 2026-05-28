"""Камера, которая следует за игроком и ограничивается размерами уровня."""

from __future__ import annotations

import pygame


class Camera:
    """Хранит смещение экрана относительно мира."""

    def __init__(self, width: int, height: int, world_width: int, world_height: int) -> None:
        self.camera = pygame.Rect(0, 0, width, height)
        self.world_width = world_width
        self.world_height = world_height

    def update(self, target_rect: pygame.Rect) -> None:
        """Центрирует камеру на цели и не выходит за границы уровня."""
        self.camera.center = target_rect.center
        self.camera.left = max(0, min(self.camera.left, self.world_width - self.camera.width))
        self.camera.top = max(0, min(self.camera.top, self.world_height - self.camera.height))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Возвращает прямоугольник, сдвинутый на текущее смещение камеры."""
        return rect.move(-self.camera.x, -self.camera.y)
