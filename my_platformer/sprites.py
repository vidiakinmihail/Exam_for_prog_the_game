"""Загрузка и нарезка персонажного spritesheet."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pygame


ROOT_DIR = Path(__file__).resolve().parents[1]
CHARACTERS_SHEET_PATH = ROOT_DIR / "assets" / "raw" / "characters.png"

FRAME_WIDTH = 32
FRAME_HEIGHT = 32
ROWS = 4
COLUMNS = 23


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
