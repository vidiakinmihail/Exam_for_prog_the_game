"""Загрузка spritesheet-ов: персонажи, фон, тайлы, декорации, порталы, монеты."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pygame


ROOT_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT_DIR / "assets" / "raw"

CHARACTERS_SHEET_PATH = ASSETS_DIR / "characters.png"
TILES_DIR = ASSETS_DIR / "1 Tiles"
BACKGROUND_LAYERS_DIR = ASSETS_DIR / "2 Background" / "Layers"
OBJECTS_DIR = ASSETS_DIR / "3 Objects"
ANIMATED_DIR = ASSETS_DIR / "4 Animated objects"

PORTAL_SHEETS: dict[int, Path] = {
    1: ASSETS_DIR / "PORTAL BLUE-Sheet.png",
    2: ASSETS_DIR / "PORTAL ORANGE-Sheet.png",
    3: ASSETS_DIR / "Sprite-0003-Sheet (1).png",
}

DECORATION_DIRS = {
    "tree": OBJECTS_DIR / "Trees",
    "willow": OBJECTS_DIR / "Willows",
    "bush": OBJECTS_DIR / "Bushes",
    "grass": OBJECTS_DIR / "Grass",
}

FRAME_WIDTH = 32
FRAME_HEIGHT = 32
ROWS = 4
COLUMNS = 23

PORTAL_FRAME_WIDTH = 64
PORTAL_FRAME_HEIGHT = 64
PORTAL_FRAME_COUNT = 8

COIN_FRAME_WIDTH = 10
COIN_FRAME_HEIGHT = 10
COIN_FRAME_COUNT = 4
COIN_SCALE = 3

PARALLAX_TARGET_HEIGHT = 600
PARALLAX_LAYER_COUNT = 5
PARALLAX_FACTORS = (0.0, 0.06, 0.14, 0.24, 0.36)


@lru_cache(maxsize=1)
def _load_sheet() -> pygame.Surface:
    return pygame.image.load(str(CHARACTERS_SHEET_PATH)).convert_alpha()


@lru_cache(maxsize=16)
def get_character_row(row_index: int, scale: tuple[int, int] | None = None) -> tuple[pygame.Surface, ...]:
    """Возвращает все кадры указанной строки spritesheet."""
    if row_index < 0 or row_index >= ROWS:
        raise ValueError(f"row_index must be between 0 and {ROWS - 1}")

    sheet = _load_sheet()
    frames: list[pygame.Surface] = []
    target_size = scale or (FRAME_WIDTH, FRAME_HEIGHT)
    for column in range(COLUMNS):
        frame = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), pygame.Rect(column * FRAME_WIDTH, row_index * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT))
        if scale is not None:
            frame = pygame.transform.smoothscale(frame, scale)

        normalized = pygame.Surface(target_size, pygame.SRCALPHA)
        normalized.blit(frame, frame.get_rect(center=(target_size[0] // 2, target_size[1] // 2)))
        frames.append(normalized)
    return tuple(frames)


def _scale_to_height(image: pygame.Surface, target_height: int) -> pygame.Surface:
    width, height = image.get_size()
    if height == target_height:
        return image
    scale = target_height / height
    target_width = max(1, int(width * scale))
    return pygame.transform.smoothscale(image, (target_width, target_height))


@lru_cache(maxsize=64)
def get_tile(tile_id: int) -> pygame.Surface:
    """Загружает один тайл платформы."""
    path = TILES_DIR / f"Tile_{tile_id:02d}.png"
    return pygame.image.load(str(path)).convert_alpha()


@lru_cache(maxsize=1)
def get_parallax_layers() -> tuple[pygame.Surface, ...]:
    """Возвращает 5 слоёв параллакс-фона, масштабированных под экран."""
    layers: list[pygame.Surface] = []
    for index in range(1, PARALLAX_LAYER_COUNT + 1):
        path = BACKGROUND_LAYERS_DIR / f"{index}.png"
        image = pygame.image.load(str(path))
        if index == 1:
            image = image.convert()
        else:
            image = image.convert_alpha()
        layers.append(_scale_to_height(image, PARALLAX_TARGET_HEIGHT))
    return tuple(layers)


@lru_cache(maxsize=8)
def get_decoration_sprites(kind: str) -> tuple[pygame.Surface, ...]:
    """Загружает все варианты декорации указанного типа."""
    folder = DECORATION_DIRS[kind]
    sprites: list[pygame.Surface] = []
    for path in sorted(folder.glob("*.png")):
        sprites.append(pygame.image.load(str(path)).convert_alpha())
    return tuple(sprites)


@lru_cache(maxsize=1)
def get_coin_frames() -> tuple[pygame.Surface, ...]:
    """Нарезает и масштабирует кадры анимации монеты."""
    sheet = pygame.image.load(str(ANIMATED_DIR / "Coin.png")).convert_alpha()
    target_size = (COIN_FRAME_WIDTH * COIN_SCALE, COIN_FRAME_HEIGHT * COIN_SCALE)
    frames: list[pygame.Surface] = []
    for index in range(COIN_FRAME_COUNT):
        frame = pygame.Surface((COIN_FRAME_WIDTH, COIN_FRAME_HEIGHT), pygame.SRCALPHA)
        frame.blit(
            sheet,
            (0, 0),
            pygame.Rect(index * COIN_FRAME_WIDTH, 0, COIN_FRAME_WIDTH, COIN_FRAME_HEIGHT),
        )
        frames.append(pygame.transform.scale(frame, target_size))
    return tuple(frames)


@lru_cache(maxsize=4)
def get_portal_frames(level_num: int, scale: tuple[int, int] | None = None) -> tuple[pygame.Surface, ...]:
    """Нарезает и возвращает кадры анимации портала для указанного уровня."""
    sheet_path = PORTAL_SHEETS.get(level_num, PORTAL_SHEETS[1])
    sheet = pygame.image.load(str(sheet_path)).convert_alpha()
    target_size = scale or (PORTAL_FRAME_WIDTH, PORTAL_FRAME_HEIGHT)
    frames: list[pygame.Surface] = []
    for index in range(PORTAL_FRAME_COUNT):
        frame = pygame.Surface((PORTAL_FRAME_WIDTH, PORTAL_FRAME_HEIGHT), pygame.SRCALPHA)
        frame.blit(
            sheet,
            (0, 0),
            pygame.Rect(index * PORTAL_FRAME_WIDTH, 0, PORTAL_FRAME_WIDTH, PORTAL_FRAME_HEIGHT),
        )
        if scale is not None:
            frame = pygame.transform.smoothscale(frame, scale)
        frames.append(frame)
    return tuple(frames)
