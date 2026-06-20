"""Враг с конечным автоматом состояний."""

from __future__ import annotations

import pygame

from .config import (
    ENEMY_ATTACK_COOLDOWN_FRAMES,
    ENEMY_CHASE_RANGE,
    ENEMY_CHASE_SPEED,
    ENEMY_COLOR,
    ENEMY_PATROL_SPEED,
    ENEMY_RETREAT_SPEED,
    ENEMY_SIZE,
    ENEMY_VERTICAL_TOLERANCE,
    GRAVITY,
)
from .sprites import get_character_row

PATROL = "patrol"
CHASE = "chase"
ATTACK_COOLDOWN = "attack_cooldown"


class Enemy(pygame.sprite.Sprite):
    """Красный квадрат, который патрулирует, преследует и атакует игрока."""

    def __init__(self, x: int, y: int, patrol_left: int = 300, patrol_right: int = 500, skin_row: int = 0) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, ENEMY_SIZE, ENEMY_SIZE)
        self.state = PATROL
        self.direction = 1
        self.velocity_y = 0.0
        self.on_ground = False
        self.cooldown_frames = 0
        self.retreat_direction = -1
        self.patrol_left = patrol_left
        self.patrol_right = patrol_right
        self.sprite_frames = get_character_row(skin_row, (52, 52))
        if skin_row == 3:
            self.sprite_frames = self.sprite_frames[:4]
        self.animation_tick = 0
        self.facing_right = True

    def _should_chase(self, player_rect: pygame.Rect) -> bool:
        horizontal_distance = abs(player_rect.centerx - self.rect.centerx)
        vertical_distance = abs(player_rect.centery - self.rect.centery)
        return horizontal_distance <= ENEMY_CHASE_RANGE and vertical_distance <= ENEMY_VERTICAL_TOLERANCE

    def _move_horizontally(self, delta_x: int, platforms: list[pygame.sprite.Sprite]) -> None:
        self.rect.x += delta_x
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if delta_x > 0:
                    self.rect.right = platform.rect.left
                elif delta_x < 0:
                    self.rect.left = platform.rect.right

    def _apply_gravity(self, platforms: list[pygame.sprite.Sprite]) -> None:
        self.velocity_y += GRAVITY
        self.rect.y += int(self.velocity_y)
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

    def update(self, player: "Player", platforms: list[pygame.sprite.Sprite]) -> None:
        """Обновляет состояние врага и его физику."""
        moving = False
        if self.cooldown_frames > 0:
            self.state = ATTACK_COOLDOWN
            self._move_horizontally(self.retreat_direction * ENEMY_RETREAT_SPEED, platforms)
            self.facing_right = self.retreat_direction >= 0
            moving = True
            self.cooldown_frames -= 1
            self._apply_gravity(platforms)
            if self.cooldown_frames == 0:
                self.state = CHASE if self._should_chase(player.rect) else PATROL
            return

        if self.rect.colliderect(player.rect):
            self.state = ATTACK_COOLDOWN
            self.cooldown_frames = ENEMY_ATTACK_COOLDOWN_FRAMES
            self.retreat_direction = -1 if player.rect.centerx > self.rect.centerx else 1
            player.take_damage(1 if player.rect.centerx > self.rect.centerx else -1)
            self._move_horizontally(self.retreat_direction * ENEMY_RETREAT_SPEED, platforms)
            self.facing_right = self.retreat_direction >= 0
            moving = True
            self._apply_gravity(platforms)
            return

        if self._should_chase(player.rect):
            self.state = CHASE
            chase_direction = 1 if player.rect.centerx > self.rect.centerx else -1
            self._move_horizontally(chase_direction * ENEMY_CHASE_SPEED, platforms)
            self.facing_right = chase_direction >= 0
            moving = True
        else:
            self.state = PATROL
            if self.rect.left <= self.patrol_left:
                self.direction = 1
            elif self.rect.left >= self.patrol_right:
                self.direction = -1
            self._move_horizontally(self.direction * ENEMY_PATROL_SPEED, platforms)
            self.facing_right = self.direction >= 0
            moving = True

        self._apply_gravity(platforms)

        if moving:
            self.animation_tick += 1

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует врага с учётом камеры."""
        rect = camera.apply(self.rect)
        frame_index = 0
        if self.state == ATTACK_COOLDOWN:
            frame_index = min(3, len(self.sprite_frames) - 1)
        elif self.state == CHASE or self.state == PATROL:
            frame_index = (self.animation_tick // 5) % len(self.sprite_frames)

        frame = self.sprite_frames[frame_index]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        frame_rect = frame.get_rect(midbottom=(rect.centerx, rect.bottom + 8))
        shadow = pygame.Surface((frame_rect.width, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
        surface.blit(shadow, (frame_rect.x, frame_rect.bottom - 8))
        surface.blit(frame, frame_rect)
