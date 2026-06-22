"""Модульные тесты для проверки игровой логики платформера."""

import unittest
import os
import sys

# Добавляем текущую директорию в пути, чтобы тесты видели пакет my_platformer
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Импортируем данные уровней для проверки
from my_platformer.levels import LEVELS


class TestPlatformerLogic(unittest.TestCase):
    """Тесты для проверки структуры данных и логики игры."""

    def test_levels_structure(self):
        """Проверяем, что все уровни содержат обязательные ключи."""
        for level_num, level_data in LEVELS.items():
            with self.subTest(level=level_num):
                # Проверяем, что в уровне есть платформы, монеты и враги
                self.assertIn("platforms", level_data)
                self.assertIn("items", level_data)
                self.assertIn("enemies", level_data)
                self.assertIn("items_to_collect", level_data)

    def test_first_level_items_count(self):
        """Проверяем, что на 1 уровне количество монет совпадает с целью сборки."""
        level_1 = LEVELS[1]
        actual_coins = len(level_1["items"])
        required_coins = level_1["items_to_collect"]
        
        # Тест пройдет, если физически созданных монет столько же, сколько нужно собрать
        self.assertEqual(actual_coins, required_coins, "Количество монет на Лвл 1 не совпадает с целью!")

    def test_platforms_bounds(self):
        """Проверяем, что координаты платформ не улетают в минус."""
        for level_num, level_data in LEVELS.items():
            for i, plat in enumerate(level_data["platforms"]):
                with self.subTest(level=level_num, platform=i):
                    # Проверяем, что координаты X и Y больше или равны 0
                    self.assertGreaterEqual(plat["x"], 0, f"Платформа {i} вышла за левую границу")
                    self.assertGreaterEqual(plat["y"], 0, f"Платформа {i} улетела выше экрана")


if __name__ == "__main__":
    unittest.main()