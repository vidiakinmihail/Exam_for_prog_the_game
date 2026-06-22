"""Собираемые предметы и анимированный портал финиша."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .config import PORTAL_SIZE
from .sprites import get_coin_frames, get_portal_frames

if TYPE_CHECKING:
    from .camera import Camera


class Item(pygame.sprite.Sprite):
    """Анимированная монета-собираемый предмет."""

    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.frames = get_coin_frames()
        self.center_x = x
        self.center_y = y
        self.radius = max(self.frames[0].get_width(), self.frames[0].get_height()) // 2
        self.rect = pygame.Rect(
            x - self.radius,
            y - self.radius,
            self.radius * 2,
            self.radius * 2,
        )
        self.animation_tick = 0

    def update(self) -> None:
        self.animation_tick += 1

    def collides_with(self, player_rect: pygame.Rect) -> bool:
        """Проверяет пересечение круга с прямоугольником игрока."""
        closest_x = max(player_rect.left, min(self.center_x, player_rect.right))
        closest_y = max(player_rect.top, min(self.center_y, player_rect.bottom))
        dx = self.center_x - closest_x
        dy = self.center_y - closest_y
        return dx * dx + dy * dy <= self.radius * self.radius

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Рисует монету с учётом камеры."""
        if not self.alive():
            return
        frame_index = (self.animation_tick // 6) % len(self.frames)
        frame = self.frames[frame_index]
        screen_x = self.center_x - camera.camera.x
        screen_y = self.center_y - camera.camera.y
        frame_rect = frame.get_rect(center=(screen_x, screen_y))
        surface.blit(frame, frame_rect)


class Portal(pygame.sprite.Sprite):
    """Анимированный портал, появляющийся после сбора всех предметов."""

    def __init__(self, x: int, y: int, level_num: int) -> None:
        super().__init__()
        self.level_num = level_num
        self.frames = get_portal_frames(level_num, PORTAL_SIZE)
        self.rect = pygame.Rect(x, y, PORTAL_SIZE[0], PORTAL_SIZE[1])
        self.animation_tick = 0

    def update(self) -> None:
        self.animation_tick += 1

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Рисует текущий кадр портала с учётом камеры."""
        rect = camera.apply(self.rect)
        frame_index = (self.animation_tick // 4) % len(self.frames)
        frame = self.frames[frame_index]
        frame_rect = frame.get_rect(midbottom=(rect.centerx, rect.bottom))
        surface.blit(frame, frame_rect)


Door = Portal
