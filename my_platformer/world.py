"""Мир игры: платформы, предметы, враг, дверь и проверки победы/поражения."""

from __future__ import annotations

import pygame

from .config import (
    BACKGROUND_COLOR,
    DOOR_SPAWN,
    ENEMY_SPAWN,
    ITEMS_LIST,
    PLAYER_MAX_LIVES,
    PLAYER_START_POS,
    PLATFORM_COLOR,
    PLATFORMS_LIST,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WORLD_WIDTH,
)
from .enemy import Enemy
from .item import Door, Item
from .player import Player
from .utils import draw_hearts, draw_text


class Platform(pygame.sprite.Sprite):
    """Прямоугольная платформа уровня."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        rect = camera.apply(self.rect)
        pygame.draw.rect(surface, PLATFORM_COLOR, rect)
        pygame.draw.rect(surface, (70, 45, 20), rect, 2)


class World:
    """Содержит все игровые объекты и управляет правилами уровня."""

    def __init__(self) -> None:
        self.platforms = pygame.sprite.Group(
            *[Platform(x, y, width, height) for x, y, width, height in PLATFORMS_LIST]
        )
        self.items = pygame.sprite.Group(*[Item(x, y) for x, y in ITEMS_LIST])
        self.enemies = pygame.sprite.Group()
        self.enemy = Enemy(*ENEMY_SPAWN)
        self.enemies.add(self.enemy)
        self.doors = pygame.sprite.Group()
        self.door: Door | None = None

        self.player = Player(*PLAYER_START_POS)
        self.score = 0
        self.total_items = len(ITEMS_LIST)
        self.game_over = False
        self.win = False
        self.world_width = WORLD_WIDTH
        self.world_height = SCREEN_HEIGHT

    def _spawn_door_if_needed(self) -> None:
        """Создаёт дверь после сбора всех предметов."""
        if self.score == self.total_items and self.door is None:
            self.door = Door(*DOOR_SPAWN)
            self.doors.add(self.door)

    def _collect_items(self) -> None:
        """Проверяет подбор предметов игроком."""
        for item in list(self.items):
            if item.collides_with(self.player.rect):
                item.kill()
                self.score += 1

    def _check_door_collision(self) -> None:
        """Проверяет условие победы при касании двери."""
        if self.door is not None and self.door.rect.colliderect(self.player.rect):
            self.win = True

    def update(self, move_left: bool, move_right: bool) -> None:
        """Обновляет все игровые сущности и проверяет состояние игры."""
        if self.game_over or self.win:
            return

        self.player.update(self.platforms.sprites(), move_left, move_right)
        self.enemy.update(self.player, self.platforms.sprites())
        self._collect_items()
        self._spawn_door_if_needed()
        self._check_door_collision()

        if self.player.lives <= 0:
            self.game_over = True

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует весь уровень и HUD."""
        surface.fill(BACKGROUND_COLOR)

        for platform in self.platforms:
            platform.draw(surface, camera)

        for item in self.items:
            item.draw(surface, camera)

        for door in self.doors:
            door.draw(surface, camera)

        for enemy in self.enemies:
            enemy.draw(surface, camera)

        self.player.draw(surface, camera)

        draw_hearts(surface, self.player.lives, PLAYER_MAX_LIVES)
        draw_text(surface, f"Score: {self.score}/{self.total_items}", 12, 42, 24)

        if self.game_over:
            draw_text(surface, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 64, center=True)
        elif self.win:
            draw_text(surface, "YOU WIN!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 64, center=True)
