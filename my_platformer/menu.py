"""Главное меню игры с анимированным фоном из игры."""

from __future__ import annotations

import pygame

from .config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TEXT_COLOR, WINDOW_TITLE
# Импортируем слои фона прямо из твоего менеджера спрайтов
from .sprites import get_parallax_layers, PARALLAX_FACTORS


class Menu:
    """Главное меню с динамичным параллакс-фоном и кнопками.

    Метод `show` блокирует выполнение и возвращает True, если игрок
    выбрал старт, или False при выходе/отмене.
    """

    @staticmethod
    def show(game) -> bool:
        screen = game.screen
        clock = game.clock

        pygame.font.init()
        # Используем встроенный или системный жирный шрифт для красивого заголовка
        title_font = pygame.font.SysFont("Impact", 64) or pygame.font.SysFont(None, 72)
        btn_font = pygame.font.SysFont("Arial", 28, bold=True) or pygame.font.SysFont(None, 36)

        title_surf = title_font.render(WINDOW_TITLE, True, TEXT_COLOR)
        btn_start_surf = btn_font.render("Начать игру", True, (255, 255, 255))
        btn_settings_surf = btn_font.render("Настройки", True, (255, 255, 255))
        btn_exit_surf = btn_font.render("Выход", True, (255, 255, 255))

        # Настройки геометрии кнопок
        btn_w, btn_h = 280, 55
        spacing = 16
        btn_x = (SCREEN_WIDTH - btn_w) // 2
        
        # Смещаем кнопки чуть ниже центра, чтобы заголовок смотрелся свободно
        start_y = int(SCREEN_HEIGHT * 0.45)
        btn_rect = pygame.Rect(btn_x, start_y, btn_w, btn_h)
        settings_rect = pygame.Rect(btn_x, start_y + btn_h + spacing, btn_w, btn_h)
        exit_rect = pygame.Rect(btn_x, start_y + (btn_h + spacing) * 2, btn_w, btn_h)

        # Загружаем слои фона
        bg_layers = get_parallax_layers()
        
        # Переменная для анимации движения фона (имитация движения камеры)
        scroll_x = 0.0

        while True:
            # Плавное движение фона влево со скоростью 0.5 пикселя за кадр
            scroll_x += 0.5 

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False
                    if event.key == pygame.K_s:
                        from .pause_menu import PauseMenu
                        PauseMenu().show_settings(game)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_rect.collidepoint(event.pos):
                        return True
                    if settings_rect.collidepoint(event.pos):
                        from .pause_menu import PauseMenu
                        PauseMenu().show_settings(game)
                    if exit_rect.collidepoint(event.pos):
                        return False

            # --- 1. ОТРИСОВКА ЖИВОГО ПАРАЛЛАКС-ФОНА ---
            for i, (layer, factor) in enumerate(zip(bg_layers, PARALLAX_FACTORS)):
                # Если у самого первого слоя (небо) фактор параллакса 0, 
                # искусственно дадим ему крошечное движение для глубины
                current_factor = factor if factor != 0 else 0.02
                
                layer_width = layer.get_width()
                offset = int(scroll_x * current_factor) % layer_width
                
                # Заполнение экрана по горизонтали
                x = -offset
                while x < SCREEN_WIDTH:
                    screen.blit(layer, (x, 0))
                    x += layer_width

            # --- 2. ОТРИСОВКА ЗАГОЛОВКА ИГРЫ С ТЕНЬЮ ---
            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
            
            # Эффект тени для текста (сдвиг на 3 пикселя вниз и вправо)
            shadow_surf = title_font.render(WINDOW_TITLE, True, (20, 20, 30))
            shadow_rect = shadow_surf.get_rect(center=(title_rect.centerx + 3, title_rect.centery + 3))
            screen.blit(shadow_surf, shadow_rect)
            screen.blit(title_surf, title_rect)

            # --- 3. ОТРИСОВКА СТИЛЬНЫХ ПОЛУПРОЗРАЧНЫХ КНОПОК ---
            mouse_pos = pygame.mouse.get_pos()

            for rect, text_surf in [
                (btn_rect, btn_start_surf),
                (settings_rect, btn_settings_surf),
                (exit_rect, btn_exit_surf)
            ]:
                # Проверяем, наведена ли мышь на кнопку (эффект Hover)
                is_hovered = rect.collidepoint(mouse_pos)
                
                # Создаем отдельную поверхность для реализации прозрачности (Alpha)
                button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                
                # Цвет кнопки: если наведены — делаем ярче, если нет — темнее и прозрачнее
                bg_color = (80, 50, 70, 220) if is_hovered else (40, 30, 40, 160)
                border_color = (200, 160, 120, 255) if is_hovered else (100, 80, 90, 200)

                # Рисуем саму кнопку и рамку на прозрачной поверхности
                pygame.draw.rect(button_surface, bg_color, (0, 0, rect.width, rect.height), border_radius=6)
                pygame.draw.rect(button_surface, border_color, (0, 0, rect.width, rect.height), width=2, border_radius=6)
                
                # Переносим кнопку на главный экран
                screen.blit(button_surface, (rect.x, rect.y))
                
                # Центрируем и рисуем текст поверх кнопки
                text_rect = text_surf.get_rect(center=rect.center)
                screen.blit(text_surf, text_rect)

            pygame.display.flip()
            clock.tick(FPS)