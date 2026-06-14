"""Точка входа в игру и главный цикл."""

from __future__ import annotations

import pygame

from .camera import Camera
from .config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, START_LEVEL, WINDOW_TITLE
from .world import World


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

    def handle_events(self) -> None:
        """Обрабатывает события окна и клавиатуры."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.world.player.jump()

    def update(self) -> None:
        """Обновляет модель мира, если игра ещё не завершена."""
        if self.completion_timer > 0:
            self.completion_timer -= 1
            if self.completion_timer == 0:
                self.running = False
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
            self.completion_timer = FPS * 2

        self.camera.update(self.world.player.rect)

    def draw(self) -> None:
        """Рисует текущий кадр."""
        self.world.draw(self.screen, self.camera)
        pygame.display.flip()

    def run(self) -> None:
        """Запускает главный цикл игры."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


def main() -> None:
    """Стартует игру."""
    game = Game()
    from .menu import Menu

    start = Menu.show(game)
    if start:
        game.run()
    else:
        # Пользователь закрыл меню — корректно завершить Pygame
        pygame.quit()


if __name__ == "__main__":
    main()
