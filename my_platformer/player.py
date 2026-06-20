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
from .sprites import get_character_row


class Player:
    """Зелёный квадрат, которым управляет игрок."""

    JUMP_BUFFER_FRAMES = 6
    COYOTE_FRAMES = 6

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_x = 0
        self.velocity_y = 0.0
        self.on_ground = False
        self.lives = PLAYER_MAX_LIVES
        self.knockback_frames = 0
        self.knockback_direction = 0
        self.jump_buffer_frames = 0
        self.coyote_frames = 0
        self.sprite_frames = get_character_row(1, (64, 64))
        self.idle_frame = self.sprite_frames[0]
        self.walk_frames = self.sprite_frames[1:6] if len(self.sprite_frames) >= 6 else self.sprite_frames
        self.jump_frame = self.sprite_frames[6] if len(self.sprite_frames) > 6 else self.sprite_frames[-1]
        self.animation_tick = 0
        self.facing_right = True

    def jump(self) -> None:
        """Запоминает нажатие прыжка на несколько кадров."""
        self.jump_buffer_frames = self.JUMP_BUFFER_FRAMES

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

    def _try_jump(self) -> None:
        """Выполняет прыжок, если был буфер нажатия и игрок стоит на земле или в coyote time."""
        can_jump = (self.on_ground or self.coyote_frames > 0) and self.knockback_frames == 0
        if self.jump_buffer_frames > 0 and can_jump:
            self.velocity_y = JUMP_POWER
            self.on_ground = False
            self.jump_buffer_frames = 0
            self.coyote_frames = 0

    def update(self, platforms: list[pygame.sprite.Sprite], move_left: bool, move_right: bool) -> None:
        """Обновляет физику игрока и обрабатывает столкновения с платформами."""
        moving = False
        if self.knockback_frames > 0:
            self.velocity_x = self.knockback_direction * PLAYER_KNOCKBACK_SPEED
            self.knockback_frames -= 1
            moving = True
            self.facing_right = self.knockback_direction >= 0
        else:
            self.velocity_x = 0
            if move_left:
                self.velocity_x -= 1
            if move_right:
                self.velocity_x += 1
            self.velocity_x *= 0 if (move_left and move_right) else 1
            self.velocity_x *= 4
            moving = self.velocity_x != 0
            if move_left and not move_right:
                self.facing_right = False
            elif move_right and not move_left:
                self.facing_right = True

        self.rect.x += self.velocity_x
        self._apply_horizontal_collision(platforms)

        if self.on_ground:
            self.coyote_frames = self.COYOTE_FRAMES
        elif self.coyote_frames > 0:
            self.coyote_frames -= 1

        self._try_jump()

        self.velocity_y += GRAVITY
        self.rect.y += int(self.velocity_y)
        self._apply_vertical_collision(platforms)

        if moving or not self.on_ground:
            self.animation_tick += 1

        if self.jump_buffer_frames > 0:
            self.jump_buffer_frames -= 1

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует игрока с учётом камеры."""
        rect = camera.apply(self.rect)
        if not self.on_ground:
            frame = self.jump_frame
        else:
            # временно убираем ходовую анимацию, чтобы убрать дрожание спрайта
            frame = self.idle_frame

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        frame_rect = frame.get_rect(midbottom=(rect.centerx, rect.bottom))
        shadow = pygame.Surface((frame_rect.width, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
        surface.blit(shadow, (frame_rect.x, frame_rect.bottom - 8))
        surface.blit(frame, frame_rect)
