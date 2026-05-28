"""Игрок платформера: движение, прыжок, здоровье и отталкивание."""

from __future__ import annotations

import pygame

from .config import (
    GRAVITY,
    JUMP_POWER,
    PLAYER_COLOR,
    PLAYER_KNOCKBACK_FRAMES,
    PLAYER_KNOCKBACK_SPEED,
    PLAYER_MAX_LIVES,
    PLAYER_SIZE,
)


class Player:
    """Зелёный квадрат, которым управляет игрок."""

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_x = 0
        self.velocity_y = 0.0
        self.on_ground = False
        self.lives = PLAYER_MAX_LIVES
        self.knockback_frames = 0
        self.knockback_direction = 0

    def jump(self) -> None:
        """Запускает прыжок, если игрок стоит на земле."""
        if self.on_ground and self.knockback_frames == 0:
            self.velocity_y = JUMP_POWER
            self.on_ground = False

    def take_damage(self, knockback_direction: int) -> None:
        """Снимает одну жизнь и отбрасывает игрока от врага."""
        if self.lives <= 0:
            return
        self.lives -= 1
        self.knockback_frames = PLAYER_KNOCKBACK_FRAMES
        self.knockback_direction = 1 if knockback_direction >= 0 else -1
        self.velocity_y = min(self.velocity_y, 0)
        self.on_ground = False

    def _apply_horizontal_collision(self, platforms: list[pygame.sprite.Sprite]) -> None:
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

    def _apply_vertical_collision(self, platforms: list[pygame.sprite.Sprite]) -> None:
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

    def update(self, platforms: list[pygame.sprite.Sprite], move_left: bool, move_right: bool) -> None:
        """Обновляет физику игрока и обрабатывает столкновения с платформами."""
        if self.knockback_frames > 0:
            self.velocity_x = self.knockback_direction * PLAYER_KNOCKBACK_SPEED
            self.knockback_frames -= 1
        else:
            self.velocity_x = 0
            if move_left:
                self.velocity_x -= 1
            if move_right:
                self.velocity_x += 1
            self.velocity_x *= 0 if (move_left and move_right) else 1
            self.velocity_x *= 4

        self.rect.x += self.velocity_x
        self._apply_horizontal_collision(platforms)

        self.velocity_y += GRAVITY
        self.rect.y += int(self.velocity_y)
        self._apply_vertical_collision(platforms)

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует игрока с учётом камеры."""
        rect = camera.apply(self.rect)
        pygame.draw.rect(surface, PLAYER_COLOR, rect)
        pygame.draw.rect(surface, (20, 90, 35), rect, 2)
