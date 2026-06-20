"""Мир игры: платформы, предметы, враги, дверь и переходы между уровнями."""

from __future__ import annotations

import random

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
        shadow_rect = rect.move(4, 5)
        pygame.draw.rect(surface, (18, 16, 24), shadow_rect, border_radius=6)
        pygame.draw.rect(surface, PLATFORM_COLOR, rect, border_radius=6)
        top_band = pygame.Rect(rect.x, rect.y, rect.width, max(4, rect.height // 4))
        pygame.draw.rect(surface, (166, 112, 62), top_band, border_radius=6)
        pygame.draw.rect(surface, (68, 43, 23), rect, 2, border_radius=6)


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
        self._sky_stars: list[tuple[int, int, int]] = []
        self._clouds: list[tuple[int, int, int, int]] = []
        self._hills_far: list[tuple[int, int, int]] = []
        self._hills_near: list[tuple[int, int, int]] = []

        self._load_level(level_num, keep_lives=player_lives)

    def _build_background(self) -> None:
        """Создаёт простой процедурный фон для текущего уровня."""
        rng = random.Random(self.level_num * 173)
        self._sky_stars = [
            (rng.randrange(0, self.world_width), rng.randrange(10, 220), rng.randrange(1, 3))
            for _ in range(30)
        ]
        self._clouds = [
            (rng.randrange(0, self.world_width), rng.randrange(20, 180), rng.randrange(80, 180), rng.randrange(24, 46))
            for _ in range(8)
        ]
        self._hills_far = [
            (rng.randrange(0, self.world_width), rng.randrange(380, 470), rng.randrange(100, 180))
            for _ in range(10)
        ]
        self._hills_near = [
            (rng.randrange(0, self.world_width), rng.randrange(430, 520), rng.randrange(120, 220))
            for _ in range(10)
        ]

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
                    skin_row=0 if index % 2 == 0 else 3,
                )
                for index, enemy_data in enumerate(level_data["enemies"])
            ]
        )
        self.enemy = self.enemies.sprites()[0] if self.enemies else None
        self.doors = pygame.sprite.Group()
        self.door = None
        door_spawn = level_data["door_spawn_platform"]
        self.door_spawn_position = (door_spawn["offset_x"], door_spawn["offset_y"])
        self._build_background()

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
        surface.fill((16, 20, 34))
        self._draw_background(surface, camera)

        for platform in self.platforms:
            platform.draw(surface, camera)

        for item in self.items:
            item.draw(surface, camera)

        for door in self.doors:
            door.draw(surface, camera)

        for enemy in self.enemies:
            enemy.draw(surface, camera)

        self.player.draw(surface, camera)

        hud = pygame.Surface((240, 110), pygame.SRCALPHA)
        pygame.draw.rect(hud, (10, 14, 24, 170), hud.get_rect(), border_radius=14)
        pygame.draw.rect(hud, (120, 150, 210, 90), hud.get_rect(), 2, border_radius=14)
        surface.blit(hud, (6, 6))

        draw_hearts(surface, self.player.lives, PLAYER_MAX_LIVES)
        draw_text(surface, f"Level: {self.level_num}/{self.max_level}", 12, 42, 24)
        draw_text(surface, f"Score: {self.score}/{self.total_items}", 12, 72, 24)

        if self.game_over:
            draw_text(surface, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 64, center=True)
        elif self.game_completed:
            draw_text(surface, "GAME COMPLETED!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 64, center=True)
        elif self.level_complete:
            draw_text(surface, "LEVEL COMPLETE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 56, center=True)

    def _draw_background(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует небо, облака, звёзды и дальние холмы с параллаксом."""
        width = surface.get_width()
        height = surface.get_height()

        for y in range(height):
            t = y / max(1, height - 1)
            color = (
                int(20 + 12 * t),
                int(26 + 18 * t),
                int(44 + 28 * t),
            )
            pygame.draw.line(surface, color, (0, y), (width, y))

        horizon = int(height * 0.68)
        pygame.draw.rect(surface, (27, 33, 52), (0, horizon, width, height - horizon))

        cam_x = camera.camera.x

        for star_x, star_y, star_size in self._sky_stars:
            x = int(star_x - cam_x * 0.15) % (self.world_width + 200) - 100
            if -10 <= x <= width + 10:
                pygame.draw.circle(surface, (255, 245, 220), (x, star_y), star_size)

        sun_center = (width - 140, 110)
        for radius, alpha in ((74, 20), (50, 35), (26, 75)):
            glow = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 220, 150, alpha), (glow.get_width() // 2, glow.get_height() // 2), radius)
            surface.blit(glow, (sun_center[0] - glow.get_width() // 2, sun_center[1] - glow.get_height() // 2))

        for cloud_x, cloud_y, cloud_w, cloud_h in self._clouds:
            x = int(cloud_x - cam_x * 0.25) % (self.world_width + 280) - 140
            if -220 <= x <= width + 220:
                cloud = pygame.Surface((cloud_w + 60, cloud_h + 20), pygame.SRCALPHA)
                pygame.draw.ellipse(cloud, (230, 238, 255, 150), (0, 8, cloud_w, cloud_h))
                pygame.draw.ellipse(cloud, (255, 255, 255, 90), (12, 0, cloud_w * 0.55, cloud_h * 0.8))
                pygame.draw.ellipse(cloud, (255, 255, 255, 90), (cloud_w * 0.35, 2, cloud_w * 0.65, cloud_h * 0.75))
                surface.blit(cloud, (x, cloud_y))

        def draw_hills(hills: list[tuple[int, int, int]], base_color: tuple[int, int, int], factor: float, shadow_color: tuple[int, int, int]) -> None:
            for hill_x, hill_y, hill_w in hills:
                x = int(hill_x - cam_x * factor) % (self.world_width + hill_w * 2) - hill_w
                points = [
                    (x, height),
                    (x + hill_w // 2, hill_y - hill_w // 2),
                    (x + hill_w, height),
                ]
                pygame.draw.polygon(surface, shadow_color, [(px + 8, py + 10) for px, py in points])
                pygame.draw.polygon(surface, base_color, points)

        draw_hills(self._hills_far, (40, 65, 92), 0.20, (26, 38, 58))
        draw_hills(self._hills_near, (58, 88, 114), 0.38, (30, 46, 68))

        ground_glow = pygame.Surface((width, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(ground_glow, (90, 110, 150, 38), (width * 0.1, 24, width * 0.8, 54))
        surface.blit(ground_glow, (0, horizon - 20))
