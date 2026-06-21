"""Вспомогательные функции для отрисовки текста и HUD."""

from __future__ import annotations

from functools import lru_cache

import pygame

from .config import HEART_COLOR, HEART_OUTLINE_COLOR, TEXT_COLOR


HUD_PANEL_SIZE = (268, 128)
HUD_PANEL_MARGIN = 10

HUD_BG = (28, 22, 36, 215)
HUD_BORDER_OUTER = (138, 150, 31)
HUD_BORDER_INNER = (74, 52, 68)
HUD_ACCENT = (118, 168, 72)
HUD_LABEL = (186, 198, 152)
HUD_VALUE = (255, 246, 214)
HUD_DIVIDER = (90, 110, 62, 120)
HEART_EMPTY = (58, 32, 42)
HEART_SHINE = (255, 170, 170)


@lru_cache(maxsize=16)
def _get_font(size: int, *, bold: bool = True) -> pygame.font.Font:
    """Возвращает шрифт с поддержкой кириллицы."""
    for name in ("segoeui", "arial", "tahoma", None):
        font = pygame.font.SysFont(name, size, bold=bold)
        if font:
            return font
    return pygame.font.Font(None, size)


def draw_text(
    surface: pygame.Surface,
    text: str,
    x: int,
    y: int,
    size: int = 24,
    color: tuple[int, int, int] = TEXT_COLOR,
    *,
    center: bool = False,
    bold: bool = True,
) -> None:
    """Рисует текст на поверхности."""
    text_surface = _get_font(size, bold=bold).render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def _draw_heart(
    surface: pygame.Surface,
    center_x: int,
    center_y: int,
    size: int,
    *,
    filled: bool,
) -> None:
    """Рисует пиксельное сердечко."""
    s = size
    left = (center_x - s // 2, center_y - s // 4)
    right = (center_x + s // 2, center_y - s // 4)
    bottom = (center_x, center_y + s // 2)
    top_left = (center_x - s // 2, center_y - s // 3)
    top_right = (center_x + s // 2, center_y - s // 3)

    fill_color = HEART_COLOR if filled else HEART_EMPTY
    outline = HEART_OUTLINE_COLOR if filled else (40, 20, 24)

    pygame.draw.circle(surface, fill_color, left, s // 3)
    pygame.draw.circle(surface, fill_color, right, s // 3)
    pygame.draw.polygon(surface, fill_color, [top_left, top_right, bottom])

    pygame.draw.circle(surface, outline, left, s // 3, 2)
    pygame.draw.circle(surface, outline, right, s // 3, 2)
    pygame.draw.polygon(surface, outline, [top_left, top_right, bottom], 2)

    if filled:
        shine = (center_x - s // 5, center_y - s // 5)
        pygame.draw.circle(surface, HEART_SHINE, shine, max(2, s // 7))


def draw_hearts(
    surface: pygame.Surface,
    lives: int,
    max_lives: int,
    x: int = 12,
    y: int = 12,
    radius: int = 10,
    spacing: int = 28,
) -> None:
    """Рисует здоровье игрока в виде сердечек."""
    heart_size = radius * 2 + 2
    for index in range(max_lives):
        center_x = x + index * spacing + heart_size // 2
        center_y = y + heart_size // 2
        _draw_heart(surface, center_x, center_y, heart_size, filled=index < lives)


def draw_hud_panel(
    surface: pygame.Surface,
    *,
    lives: int,
    max_lives: int,
    level: int,
    max_level: int,
    score: int,
    total_items: int,
    x: int = HUD_PANEL_MARGIN,
    y: int = HUD_PANEL_MARGIN,
) -> None:
    """Рисует декоративную панель статуса игрока."""
    panel_w, panel_h = HUD_PANEL_SIZE
    outer = pygame.Rect(x, y, panel_w, panel_h)
    inner = outer.inflate(-6, -6)
    content = inner.inflate(-10, -10)

    shadow = outer.move(3, 4)
    shadow_surface = pygame.Surface(shadow.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 70), shadow_surface.get_rect(), border_radius=16)
    surface.blit(shadow_surface, shadow.topleft)

    panel = pygame.Surface(outer.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, HUD_BORDER_OUTER, panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, HUD_BG, inner.move(-x, -y), border_radius=13)
    pygame.draw.rect(panel, HUD_BORDER_INNER, inner.move(-x, -y), 2, border_radius=13)
    highlight = pygame.Rect(inner.x - x + 8, inner.y - y + 6, inner.width - 16, 18)
    pygame.draw.rect(panel, (255, 255, 255, 18), highlight, border_radius=8)
    surface.blit(panel, outer.topleft)

    label_font = _get_font(18, bold=False)
    value_font = _get_font(22, bold=True)
    title_font = _get_font(20, bold=True)

    title = title_font.render("Статус", True, HUD_ACCENT)
    surface.blit(title, (content.x + 4, content.y + 2))

    hearts_x = content.x + 4
    hearts_y = content.y + 30
    draw_hearts(surface, lives, max_lives, hearts_x, hearts_y, radius=9, spacing=26)

    lives_label = label_font.render("Жизни", True, HUD_LABEL)
    surface.blit(lives_label, (content.x + 92, content.y + 34))

    divider_y = content.y + 58
    divider = pygame.Surface((content.width, 2), pygame.SRCALPHA)
    divider.fill(HUD_DIVIDER)
    surface.blit(divider, (content.x, divider_y))

    rows = (
        ("Уровень", f"{level} / {max_level}"),
        ("Монеты", f"{score} / {total_items}"),
    )
    row_y = divider_y + 10
    for label_text, value_text in rows:
        label = label_font.render(f"{label_text}:", True, HUD_LABEL)
        value = value_font.render(value_text, True, HUD_VALUE)
        surface.blit(label, (content.x + 4, row_y))
        surface.blit(value, (content.right - value.get_width(), row_y - 1))
        row_y += 24
