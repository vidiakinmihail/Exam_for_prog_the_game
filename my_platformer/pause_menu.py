"""Пауза: меню с кнопками `Resume`, `Main Menu`, `Settings`."""

from __future__ import annotations

import pygame

from .config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TEXT_COLOR, BACKGROUND_COLOR


class PauseMenu:
    def __init__(self) -> None:
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 64)
        self.btn_font = pygame.font.SysFont(None, 28)

        self.btn_w, self.btn_h = 220, 56
        spacing = 12
        total_h = self.btn_h * 3 + spacing * 2
        start_y = (SCREEN_HEIGHT - total_h) // 2
        x = (SCREEN_WIDTH - self.btn_w) // 2

        self.resume_rect = pygame.Rect(x, start_y, self.btn_w, self.btn_h)
        self.settings_rect = pygame.Rect(x, start_y + self.btn_h + spacing, self.btn_w, self.btn_h)
        self.main_menu_rect = pygame.Rect(x, start_y + (self.btn_h + spacing) * 2, self.btn_w, self.btn_h)

    def render(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("Пауза", True, TEXT_COLOR)
        # place title above the first button to avoid overlap
        title_y = self.resume_rect.top - 40
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        screen.blit(title, title_rect)

        # buttons
        for rect, text in (
            (self.resume_rect, "Продолжить"),
            (self.settings_rect, "Настройки"),
            (self.main_menu_rect, "В главное меню"),
        ):
            pygame.draw.rect(screen, (200, 200, 200), rect)
            pygame.draw.rect(screen, (100, 100, 100), rect, 3)
            surf = self.btn_font.render(text, True, (10, 10, 10))
            screen.blit(surf, surf.get_rect(center=rect.center))

    def handle_mouse(self, pos: tuple[int, int]) -> str | None:
        if self.resume_rect.collidepoint(pos):
            return "resume"
        if self.settings_rect.collidepoint(pos):
            return "settings"
        if self.main_menu_rect.collidepoint(pos):
            return "main_menu"
        return None

    def show_settings(self, game) -> None:
        screen = game.screen
        clock = game.clock
        font = pygame.font.SysFont(None, 48)
        back_font = pygame.font.SysFont(None, 28)

        back_rect = pygame.Rect((SCREEN_WIDTH - 140) // 2, SCREEN_HEIGHT - 120, 140, 48)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if back_rect.collidepoint(event.pos):
                        return

            screen.fill(BACKGROUND_COLOR)
            title = font.render("Настройки", True, TEXT_COLOR)
            screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)))

            pygame.draw.rect(screen, (200, 200, 200), back_rect)
            pygame.draw.rect(screen, (100, 100, 100), back_rect, 3)
            back_s = back_font.render("Назад", True, (10, 10, 10))
            screen.blit(back_s, back_s.get_rect(center=back_rect.center))

            pygame.display.flip()
            clock.tick(FPS)


class GameOverMenu:
    """Экран Game Over с кнопкой возврата в главное меню."""

    def __init__(self) -> None:
        pygame.font.init()
        self.title_font = pygame.font.SysFont(None, 64)
        self.btn_font = pygame.font.SysFont(None, 28)

        self.btn_w, self.btn_h = 220, 56
        self.main_menu_rect = pygame.Rect(
            (SCREEN_WIDTH - self.btn_w) // 2,
            SCREEN_HEIGHT // 2 + 20,
            self.btn_w,
            self.btn_h,
        )

    def render(self, screen: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        title = self.title_font.render("Игра окончена", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(title, title_rect)

        pygame.draw.rect(screen, (200, 200, 200), self.main_menu_rect)
        pygame.draw.rect(screen, (100, 100, 100), self.main_menu_rect, 3)
        label = self.btn_font.render("В главное меню", True, (10, 10, 10))
        screen.blit(label, label.get_rect(center=self.main_menu_rect.center))

    def handle_mouse(self, pos: tuple[int, int]) -> str | None:
        if self.main_menu_rect.collidepoint(pos):
            return "main_menu"
        return None
