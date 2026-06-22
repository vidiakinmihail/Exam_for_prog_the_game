"""Вспомогательные функции для отрисовки текста и HUD."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import pygame

from .config import TEXT_COLOR


HUD_PANEL_SIZE = (280, 135)  # Немного увеличили панель для лучшего распределения элементов
HUD_PANEL_MARGIN = 10

HUD_BG = (28, 22, 36, 215)
HUD_BORDER_OUTER = (138, 150, 31)
HUD_BORDER_INNER = (74, 52, 68)
HUD_ACCENT = (118, 168, 72)
HUD_LABEL = (186, 198, 152)
HUD_VALUE = (255, 246, 214)
HUD_DIVIDER = (90, 110, 62, 120)

# Путь к текстуре сердечка
ROOT_DIR = Path(__file__).resolve().parents[1]
HEART_IMAGE_PATH = ROOT_DIR / "assets" / "raw" / "image.png"


@lru_cache(maxsize=1)
def _load_heart_sprites() -> tuple[pygame.Surface, pygame.Surface]:
    """Загружает картинку сердца и возвращает кортеж (целое_сердце, пустое_сердце)."""
    try:
        full_sheet = pygame.image.load(str(HEART_IMAGE_PATH)).convert_alpha()
        w, h = full_sheet.get_size()
        
        # Проверяем: если картинка вытянута в ширину (спрайтшит), режем её пополам
        if w >= h * 2:
            single_w = w // 2
            full_heart = pygame.Surface((single_w, h), pygame.SRCALPHA)
            full_heart.blit(full_sheet, (0, 0), pygame.Rect(0, 0, single_w, h))
            
            empty_heart = pygame.Surface((single_w, h), pygame.SRCALPHA)
            empty_heart.blit(full_sheet, (0, 0), pygame.Rect(single_w, 0, single_w, h))
        else:
            # Если картинка квадратная — это одно целое сердце. 
            # Делаем пустую версию программно (применяем полупрозрачность)
            full_heart = full_sheet
            empty_heart = full_sheet.copy()
            empty_heart.fill((100, 100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
            
        # Масштабируем до аккуратного игрового размера (24x24 пикселя)
        target_size = (24, 24)
        return (
            pygame.transform.smoothscale(full_heart, target_size),
            pygame.transform.smoothscale(empty_heart, target_size)
        )
    except Exception:
        # Если файл не нашелся, создаем временные цветные квадраты, чтобы игра не вылетала
        fallback_full = pygame.Surface((24, 24))
        fallback_full.fill((220, 40, 40))
        fallback_empty = pygame.Surface((24, 24))
        fallback_empty.fill((60, 40, 40))
        return fallback_full, fallback_empty


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


def draw_hearts(
    surface: pygame.Surface,
    lives: int,
    max_lives: int,
    x: int,
    y: int,
    spacing: int = 28,
) -> None:
    """Рисует здоровье игрока с использованием загруженных картинок-сердечек."""
    full_heart, empty_heart = _load_heart_sprites()
    for index in range(max_lives):
        heart_surf = full_heart if index < lives else empty_heart
        # Отрисовка текстуры по указанным координатам со сдвигом вправо
        surface.blit(heart_surf, (x + index * spacing, y))


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
    """Рисует обновленную геометрически выверенную панель статуса."""
    panel_w, panel_h = HUD_PANEL_SIZE
    outer = pygame.Rect(x, y, panel_w, panel_h)
    inner = outer.inflate(-6, -6)
    
    # Слой внутренней рабочей области
    content_x = inner.x + 8
    content_y = inner.y + 6
    content_w = inner.width - 16

    # 1. Тень панели
    shadow = outer.move(3, 4)
    shadow_surface = pygame.Surface(shadow.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 80), shadow_surface.get_rect(), border_radius=16)
    surface.blit(shadow_surface, shadow.topleft)

    # 2. Основа подложки и рамки
    panel = pygame.Surface(outer.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, HUD_BORDER_OUTER, panel.get_rect(), border_radius=16)
    pygame.draw.rect(panel, HUD_BG, inner.move(-x, -y), border_radius=13)
    pygame.draw.rect(panel, HUD_BORDER_INNER, inner.move(-x, -y), 2, border_radius=13)
    
    # Световой блик вверху панели
    highlight = pygame.Rect(inner.x - x + 6, inner.y - y + 4, inner.width - 12, 22)
    pygame.draw.rect(panel, (255, 255, 255, 14), highlight, border_radius=8)
    surface.blit(panel, outer.topleft)

    # Шрифты
    label_font = _get_font(18, bold=False)
    value_font = _get_font(20, bold=True)
    title_font = _get_font(22, bold=True)

    # 3. Заголовок "Статус" (Теперь отрисовывается строго по сетке блика)
    title = title_font.render("Статус", True, HUD_ACCENT)
    surface.blit(title, (content_x + 2, content_y - 8))

    # 4. Блок здоровья (Сердечки + Надпись "Жизни")
    # Отодвинули Y вниз на +32, чтобы надписи не пересекались
    hearts_x = content_x + 2
    hearts_y = content_y + 32
    draw_hearts(surface, lives, max_lives, hearts_x, hearts_y, spacing=30)

    # Надпись "Жизни" теперь стоит справа от сердечек с фиксированным отступом
    lives_label = label_font.render("Жизни", True, HUD_LABEL)
    surface.blit(lives_label, (hearts_x + max_lives * 30 + 10, hearts_y + 2))

    # 5. Разделительная линия
    divider_y = content_y + 66
    divider = pygame.Surface((content_w, 2), pygame.SRCALPHA)
    divider.fill(HUD_DIVIDER)
    surface.blit(divider, (content_x, divider_y))

    # 6. Статистика уровней и монет
    rows = (
        ("Уровень", f"{level} / {max_level}"),
        ("Монеты", f"{score} / {total_items}"),
    )
    row_y = divider_y + 8
    for label_text, value_text in rows:
        label = label_font.render(f"{label_text}:", True, HUD_LABEL)
        value = value_font.render(value_text, True, HUD_VALUE)
        
        surface.blit(label, (content_x + 2, row_y))
        # Прижимаем числовые значения ровно к правому внутреннему краю панели
        surface.blit(value, (content_x + content_w - value.get_width() - 4, row_y - 1))
        row_y += 24