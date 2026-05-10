import pygame
import sys

class Game:
    def __init__(self): 
        """Инициализация игры"""
        pygame.init()
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("project")
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 60
        self.player_pos = [self.screen_width // 4, self.screen_height // 2]
        self.player_speed = 5

    def run(self):
        """Запуск игрового цикла"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        self.quit()

    def quit(self):
        """Корректное завершение"""
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()  
