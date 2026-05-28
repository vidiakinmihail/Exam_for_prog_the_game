"""Точка входа в игру и главный цикл."""

from __future__ import annotations

import pygame

from .camera import Camera
from .config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, WINDOW_TITLE
from .world import World


class Game:
    """Управляет окнами, событиями и игровым циклом."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.world = World()
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, self.world.world_width, self.world.world_height)
        self.running = True

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
        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        self.world.update(move_left, move_right)
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
    Game().run()


if __name__ == "__main__":
    main()
