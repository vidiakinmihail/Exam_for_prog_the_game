"""Главное меню игры с кнопкой "Начать игру"."""

from __future__ import annotations

import pygame

from .config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BACKGROUND_COLOR, TEXT_COLOR


class Menu:
    """Простейшее меню с одной кнопкой "Начать игру".

    Метод `show` блокирует выполнение и возвращает True, если игрок
    выбрал старт, или False при выходе/отмене.
    """

    @staticmethod
    def show(game) -> bool:
        screen = game.screen
        clock = game.clock

        pygame.font.init()
        title_font = pygame.font.SysFont(None, 72)
        btn_font = pygame.font.SysFont(None, 36)

        title_surf = title_font.render("Platformer", True, TEXT_COLOR)
        btn_start_surf = btn_font.render("Начать игру", True, (10, 10, 10))
        btn_settings_surf = btn_font.render("Настройки", True, (10, 10, 10))
        btn_exit_surf = btn_font.render("Выход", True, (10, 10, 10))

        btn_w, btn_h = 260, 64
        spacing = 16
        btn_x = (SCREEN_WIDTH - btn_w) // 2
        btn_y = (SCREEN_HEIGHT) // 2
        btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        settings_rect = pygame.Rect(btn_x, btn_y + btn_h + spacing, btn_w, btn_h)
        exit_rect = pygame.Rect(btn_x, btn_y + (btn_h + spacing) * 2, btn_w, btn_h)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return True
                    if event.key == pygame.K_ESCAPE:
                        return False
                    if event.key == pygame.K_s:
                        # open settings via PauseMenu's settings view
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

            screen.fill(BACKGROUND_COLOR)

            title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            screen.blit(title_surf, title_rect)

            # Start button
            # Start button
            pygame.draw.rect(screen, (200, 200, 200), btn_rect)
            pygame.draw.rect(screen, (160, 160, 160), btn_rect, 3)
            btn_text_rect = btn_start_surf.get_rect(center=btn_rect.center)
            screen.blit(btn_start_surf, btn_text_rect)

            # Settings button
            pygame.draw.rect(screen, (200, 200, 200), settings_rect)
            pygame.draw.rect(screen, (160, 160, 160), settings_rect, 3)
            settings_text_rect = btn_settings_surf.get_rect(center=settings_rect.center)
            screen.blit(btn_settings_surf, settings_text_rect)

            # Exit button
            pygame.draw.rect(screen, (200, 200, 200), exit_rect)
            pygame.draw.rect(screen, (160, 160, 160), exit_rect, 3)
            exit_text_rect = btn_exit_surf.get_rect(center=exit_rect.center)
            screen.blit(btn_exit_surf, exit_text_rect)

            pygame.display.flip()
            clock.tick(FPS)
