"""Мир игры: платформы, предметы, враги, портал и переходы между уровнями."""

from __future__ import annotations

import random

import pygame

from .config import PLAYER_MAX_LIVES, PLAYER_START_POS, SCREEN_HEIGHT, SCREEN_WIDTH, START_LEVEL, WORLD_WIDTH
from .enemy import Enemy
from .item import Portal, Item
from .levels import LEVELS
from .player import Player
from .sprites import PARALLAX_FACTORS, get_decoration_sprites, get_parallax_layers
from .tiles import draw_tiled_platform
from .utils import draw_hud_panel, draw_text


class Platform(pygame.sprite.Sprite):
    """Прямоугольная платформа уровня."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        draw_tiled_platform(surface, camera.apply(self.rect))


class World:
    """Хранит все игровые объекты и данные текущего уровня."""

    GROUND_Y = 550

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
        self.door: Portal | None = None
        self.enemy: Enemy | None = None

        self.level_num = level_num
        self.score = 0
        self.total_items = 0
        self.game_over = False
        self.level_complete = False
        self.game_completed = False
        self.win = False
        self.door_spawn_position = (0, 0)
        self._parallax_layers = get_parallax_layers()
        self._decorations: list[tuple[int, int, str, int, float]] = []

        self._load_level(level_num, keep_lives=player_lives)

    def _build_background(self) -> None:
        """Расставляет деревья, ивы, кусты и траву на уровне."""
        rng = random.Random(self.level_num * 173)
        self._decorations = []

        for _ in range(6):
            kind = rng.choice(("tree", "tree", "willow"))
            variants = get_decoration_sprites(kind)
            self._decorations.append(
                (
                    rng.randrange(80, self.world_width - 80),
                    self.GROUND_Y,
                    kind,
                    rng.randrange(len(variants)),
                    rng.uniform(0.10, 0.18),
                )
            )

        for _ in range(10):
            kind = rng.choice(("bush", "grass", "grass"))
            variants = get_decoration_sprites(kind)
            self._decorations.append(
                (
                    rng.randrange(0, self.world_width),
                    self.GROUND_Y,
                    kind,
                    rng.randrange(len(variants)),
                    rng.uniform(0.22, 0.34),
                )
            )

        for platform in self.platforms:
            if platform.rect.height > 24:
                continue
            for _ in range(rng.randint(1, 2)):
                variants = get_decoration_sprites("grass")
                self._decorations.append(
                    (
                        rng.randrange(platform.rect.left + 8, max(platform.rect.left + 12, platform.rect.right - 8)),
                        platform.rect.top,
                        "grass",
                        rng.randrange(len(variants)),
                        1.0,
                    )
                )

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
        """Создаёт портал после сбора всех предметов."""
        if self.score == self.total_items and self.door is None:
            self.door = Portal(*self.door_spawn_position, self.level_num)
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

        for item in self.items:
            item.update()

        for door in self.doors:
            door.update()

        self._collect_items()
        self._spawn_door_if_needed()
        self._check_door_collision()

        if self.player.lives <= 0:
            self.game_over = True

    def draw(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует уровень и HUD."""
        self._draw_background(surface, camera)
        self._draw_decorations(surface, camera, kinds=("tree", "willow"))

        for platform in self.platforms:
            platform.draw(surface, camera)

        self._draw_decorations(surface, camera, kinds=("bush", "grass"))

        for item in self.items:
            item.draw(surface, camera)

        for door in self.doors:
            door.draw(surface, camera)

        for enemy in self.enemies:
            enemy.draw(surface, camera)

        self.player.draw(surface, camera)

        draw_hud_panel(
            surface,
            lives=self.player.lives,
            max_lives=PLAYER_MAX_LIVES,
            level=self.level_num,
            max_level=self.max_level,
            score=self.score,
            total_items=self.total_items,
        )

        if self.game_completed:
            draw_text(surface, "Игра пройдена!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 64, center=True)
        elif self.level_complete:
            draw_text(surface, "Уровень пройден!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 56, center=True)

    def _draw_parallax_layer(
        self,
        surface: pygame.Surface,
        layer: pygame.Surface,
        cam_x: float,
        factor: float,
    ) -> None:
        """Рисует один слой параллакса с горизонтальным тайлингом."""
        width = surface.get_width()
        layer_width = layer.get_width()
        offset = int(cam_x * factor) % layer_width
        x = -offset
        while x < width:
            surface.blit(layer, (x, 0))
            x += layer_width

    def _draw_background(self, surface: pygame.Surface, camera: "Camera") -> None:
        """Рисует многослойный лесной параллакс-фон."""
        cam_x = camera.camera.x
        for layer, factor in zip(self._parallax_layers, PARALLAX_FACTORS):
            self._draw_parallax_layer(surface, layer, cam_x, factor)

    def _draw_decorations(self, surface: pygame.Surface, camera: "Camera", kinds: tuple[str, ...]) -> None:
        """Рисует деревья, кусты и траву с параллаксом."""
        width = surface.get_width()
        cam_x = camera.camera.x
        cam_y = camera.camera.y

        for world_x, anchor_y, kind, variant_index, factor in sorted(self._decorations, key=lambda entry: entry[4]):
            if kind not in kinds:
                continue
            sprite = get_decoration_sprites(kind)[variant_index]
            screen_x = int(world_x - cam_x * factor)
            if screen_x + sprite.get_width() < -120 or screen_x > width + 120:
                continue

            if kind in ("tree", "willow"):
                sprite_rect = sprite.get_rect(midbottom=(screen_x, anchor_y - cam_y))
            elif kind == "bush":
                sprite_rect = sprite.get_rect(midbottom=(screen_x, anchor_y - cam_y + 4))
            else:
                sprite_rect = sprite.get_rect(midbottom=(screen_x, anchor_y - cam_y - 2))

            surface.blit(sprite, sprite_rect)
