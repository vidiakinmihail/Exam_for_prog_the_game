"""Отрисовка платформ тайлами из набора Craftpix."""

from __future__ import annotations

import pygame

from .sprites import get_tile

TILE_SIZE = 32

# Стандартная 3×3 сетка: верх / середина / низ × лево / центр / право.
SOLID_TILES = {
    (True, True, True, True): 5,
    (True, True, True, False): 2,
    (True, True, False, True): 2,
    (True, True, False, False): 2,
    (True, False, True, True): 4,
    (True, False, True, False): 4,
    (True, False, False, True): 5,
    (True, False, False, False): 5,
    (False, True, True, True): 8,
    (False, True, True, False): 8,
    (False, True, False, True): 8,
    (False, True, False, False): 8,
    (False, False, True, True): 6,
    (False, False, True, False): 6,
    (False, False, False, True): 6,
    (False, False, False, False): 6,
}

THIN_TILES = {
    (True, True): 1,
    (True, False): 2,
    (False, True): 3,
    (False, False): 2,
}


def _solid_tile_id(top: bool, bottom: bool, left: bool, right: bool) -> int:
    return SOLID_TILES[(top, bottom, left, right)]


def _thin_tile_id(left: bool, right: bool) -> int:
    return THIN_TILES[(left, right)]


def draw_tiled_platform(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Рисует прямоугольную платформу тайлами с мхом и камнями."""
    if rect.width <= 0 or rect.height <= 0:
        return

    thin = rect.height <= 24
    cols = max(1, (rect.width + TILE_SIZE - 1) // TILE_SIZE)
    rows = 1 if thin else max(1, (rect.height + TILE_SIZE - 1) // TILE_SIZE)

    for row in range(rows):
        for col in range(cols):
            if thin:
                tile_id = _thin_tile_id(col == 0, col == cols - 1)
            else:
                tile_id = _solid_tile_id(
                    row == 0,
                    row == rows - 1,
                    col == 0,
                    col == cols - 1,
                )
            tile = get_tile(tile_id)
            x = rect.x + col * TILE_SIZE
            y = rect.y + row * TILE_SIZE
            surface.blit(tile, (x, y))
