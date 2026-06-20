"""Точка входа в игру и главный цикл."""

from __future__ import annotations

import pygame

from .camera import Camera
from .config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, START_LEVEL, WINDOW_TITLE, TEXT_COLOR
from .world import World
from .pause_menu import PauseMenu


class Game:
    """Управляет окнами, событиями и игровым циклом."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.current_level = START_LEVEL
        self.world = World(self.current_level)
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.world.world_width, self.world.world_height)
        self.running = True
        self.completion_timer = 0
        self.paused = False
        self.pause_menu = PauseMenu()
        self.return_to_menu = False

    def handle_events(self) -> None:
        """Обрабатывает события окна и клавиатуры."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    # Toggle pause
                    self.paused = not self.paused
                elif event.key == pygame.K_SPACE:
                    if not self.paused:
                        self.world.player.jump()
            elif self.paused and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self.pause_menu.handle_mouse(event.pos)
                if action == "resume":
                    self.paused = False
                elif action == "main_menu":
                    # request return to main menu
                    self.return_to_menu = True
                    self.running = False
                elif action == "settings":
                    # open settings (blocking) and stay paused afterwards
                    self.pause_menu.show_settings(self)

    def update(self) -> None:
        """Обновляет модель мира, если игра ещё не завершена."""
        if self.completion_timer > 0:
            self.completion_timer -= 1
            if self.completion_timer == 0:
                self.return_to_menu = True
                self.running = False
            return
        if self.paused:
            return

        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        self.world.update(move_left, move_right)

        if self.world.level_complete and not self.world.game_completed:
            self.current_level += 1
            self.world.next_level()
            self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.world.world_width, self.world.world_height)
        elif self.world.game_completed:
            self.return_to_menu = True
            self.completion_timer = FPS * 2

        self.camera.update(self.world.player.rect)

    def draw(self) -> None:
        """Рисует текущий кадр."""
        self.world.draw(self.screen, self.camera)
        if self.paused:
            self.pause_menu.render(self.screen)
        pygame.display.flip()

    def run(self) -> str:
        """Запускает главный цикл игры."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        # Не завершаем Pygame здесь — main() решит, что делать дальше
        if self.return_to_menu:
            return "to_menu"
        return "quit"


def main() -> None:
    """Стартует игру и поддерживает возврат в главное меню."""
    from .menu import Menu

    while True:
        game = Game()
        start = Menu.show(game)
        if not start:
            break
        result = game.run()
        if result != "to_menu":
            break

    pygame.quit()


if __name__ == "__main__":
    main()
