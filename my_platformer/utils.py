"""Вспомогательные функции для отрисовки текста и HUD."""

from __future__ import annotations

from functools import lru_cache

import pygame

from .config import HEART_COLOR, HEART_OUTLINE_COLOR, TEXT_COLOR


@lru_cache(maxsize=16)
def _get_font(size: int) -> pygame.font.Font:
    """Возвращает кэшированный шрифт указанного размера."""
    return pygame.font.SysFont("arial", size, bold=True)


def draw_text(
    surface: pygame.Surface,
    text: str,
    x: int,
    y: int,
    size: int = 24,
    color: tuple[int, int, int] = TEXT_COLOR,
    *,
    center: bool = False,
) -> None:
    """Рисует текст на поверхности."""
    text_surface = _get_font(size).render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def draw_hearts(
    surface: pygame.Surface,
    lives: int,
    max_lives: int,
    x: int = 12,
    y: int = 12,
    radius: int = 10,
    spacing: int = 28,
) -> None:
    """Рисует здоровье игрока в виде красных кругов."""
    for index in range(max_lives):
        center_x = x + index * spacing + radius
        center_y = y + radius
        fill_color = HEART_COLOR if index < lives else (90, 30, 30)
        pygame.draw.circle(surface, fill_color, (center_x, center_y), radius)
        pygame.draw.circle(surface, HEART_OUTLINE_COLOR, (center_x, center_y), radius, 2)
        pygame.draw.circle(surface, (0, 0, 0), (center_x, center_y), radius - 2, 1)
