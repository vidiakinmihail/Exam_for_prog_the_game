"""Мир игры: платформы, предметы, враги, дверь и переходы между уровнями."""

from __future__ import annotations

import pygame

from .config import BACKGROUND_COLOR, PLAYER_MAX_LIVES, PLAYER_START_POS, PLATFORM_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH, START_LEVEL, WORLD_WIDTH
from .enemy import Enemy
from .item import Door, Item
from .levels import LEVELS
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
    """Хранит все игровые объекты и данные текущего уровня."""

    def __init__(self, level_num: int = START_LEVEL, player_lives: int = PLAYER_MAX_LIVES) -> None:
        self.player = Player(*PLAYER_START_POS)
        self.player.lives = player_lives
        self.world_width = WORLD_WIDTH
        self.world_height = SCREEN_HEIGHT
        self.max_level = max(LEVELS)

        self.platforms = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.door: Door | None = None
        self.enemy: Enemy | None = None

        self.level_num = level_num
        self.score = 0
        self.total_items = 0
        self.game_over = False
        self.level_complete = False
        self.game_completed = False
        self.win = False
        self.door_spawn_position = (0, 0)

        self._load_level(level_num, keep_lives=player_lives)

    def _reset_player_for_level(self, keep_lives: int | None = None) -> None:
        self.player.rect.topleft = PLAYER_START_POS
        self.player.velocity_x = 0
        self.player.velocity_y = 0.0
        self.player.on_ground = False
        self.player.knockback_frames = 0
        self.player.knockback_direction = 0
        if keep_lives is not None:
            self.player.lives = keep_lives

    def _load_level(self, level_num: int, keep_lives: int | None = None) -> None:
        level_data = LEVELS[level_num]
        self.level_num = level_num
        self.score = 0
        self.total_items = level_data["items_to_collect"]
        self.game_over = False
        self.level_complete = False
        self.game_completed = False
        self.win = False

        self.platforms = pygame.sprite.Group(
            *[Platform(platform["x"], platform["y"], platform["w"], platform["h"]) for platform in level_data["platforms"]]
        )
        self.items = pygame.sprite.Group(*[Item(item["x"], item["y"]) for item in level_data["items"]])
        self.enemies = pygame.sprite.Group(
            *[
                Enemy(
                    enemy_data["x"],
                    enemy_data["y"],
                    enemy_data.get("patrol_left", 300),
                    enemy_data.get("patrol_right", 500),
                )
                for enemy_data in level_data["enemies"]
            ]
        )
        self.enemy = self.enemies.sprites()[0] if self.enemies else None
        self.doors = pygame.sprite.Group()
        self.door = None
        door_spawn = level_data["door_spawn_platform"]
        self.door_spawn_position = (door_spawn["offset_x"], door_spawn["offset_y"])

        self._reset_player_for_level(keep_lives)

    def _spawn_door_if_needed(self) -> None:
        """Создаёт дверь после сбора всех предметов."""
        if self.score == self.total_items and self.door is None:
            self.door = Door(*self.door_spawn_position)
            self.doors.add(self.door)

    def _collect_items(self) -> None:
        """Проверяет подбор предметов игроком."""
        for item in list(self.items):
            if item.collides_with(self.player.rect):
                item.kill()
                self.score += 1

    def _check_door_collision(self) -> None:
        """Проверяет условие завершения уровня."""
        if self.door is not None and self.door.rect.colliderect(self.player.rect):
            self.level_complete = True
            self.win = True
            if self.level_num == self.max_level:
                self.game_completed = True

    def next_level(self) -> bool:
        """Переходит на следующий уровень, сохраняя жизни игрока."""
        if self.level_num >= self.max_level:
            self.game_completed = True
            return False

        current_lives = self.player.lives
        self._load_level(self.level_num + 1, keep_lives=current_lives)
        return True

    def update(self, move_left: bool, move_right: bool) -> None:
        """Обновляет игровые сущности и проверяет состояние уровня."""
        if self.game_over or self.level_complete or self.game_completed:
            return

        platforms = self.platforms.sprites()
        self.player.update(platforms, move_left, move_right)
        for enemy in self.enemies:
            enemy.update(self.player, platforms)

        self._collect_items()
        self._spawn_door_if_needed()
        self._check_door_collision()

        if self.player.lives <= 0:
            self.game_over = True

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует уровень и HUD."""
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
        draw_text(surface, f"Level: {self.level_num}/{self.max_level}", 12, 42, 24)
        draw_text(surface, f"Score: {self.score}/{self.total_items}", 12, 72, 24)

        if self.game_over:
            draw_text(surface, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 64, center=True)
        elif self.game_completed:
            draw_text(surface, "GAME COMPLETED!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 64, center=True)
        elif self.level_complete:
            draw_text(surface, "LEVEL COMPLETE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 56, center=True)
