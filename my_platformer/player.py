"""Игрок платформера: движение, прыжок, здоровье и отталкивание."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .config import (
    GRAVITY,
    JUMP_POWER,
    PLAYER_COLOR,
    PLAYER_KNOCKBACK_FRAMES,
    PLAYER_KNOCKBACK_SPEED,
    PLAYER_MAX_LIVES,
    PLAYER_SIZE,
)
from .sprites import get_character_row

if TYPE_CHECKING:
    from .camera import Camera


class Player:
    """Зелёный квадрат, которым управляет игрок."""

    JUMP_BUFFER_FRAMES = 6
    COYOTE_FRAMES = 6

    def __init__(self, x: int, y: int) -> None:
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.velocity_x = 0
        self.velocity_y = 0.0
        self.on_ground = False
        self.lives = PLAYER_MAX_LIVES
        self.knockback_frames = 0
        self.knockback_direction = 0
        self.jump_buffer_frames = 0
        self.coyote_frames = 0
        self.sprite_frames = get_character_row(1, (64, 64))
        self.idle_frame = self.sprite_frames[0]
        self.walk_frames = self.sprite_frames[1:6] if len(self.sprite_frames) >= 6 else self.sprite_frames
        self.jump_frame = self.sprite_frames[6] if len(self.sprite_frames) > 6 else self.sprite_frames[-1]
        self.animation_tick = 0
        self.facing_right = True

    def jump(self) -> None:
        """Запоминает нажатие прыжка на несколько кадров."""
        self.jump_buffer_frames = self.JUMP_BUFFER_FRAMES

    def take_damage(self, knockback_direction: int) -> None:
        """Снимает одну жизнь и отбрасывает игрока от врага."""
        if self.lives <= 0:
            return
        self.lives -= 1
        self.knockback_frames = PLAYER_KNOCKBACK_FRAMES
        self.knockback_direction = 1 if knockback_direction >= 0 else -1
        self.velocity_y = min(self.velocity_y, 0)
        self.on_ground = False

    def _apply_horizontal_collision(self, platforms: list[pygame.sprite.Sprite]) -> None:
        """Разрешение горизонтальных коллизий между игроком и платформами.

        Алгоритм: пробегает по списку платформ и при пересечении прямоугольников
        перемещает игрока в край платформы в зависимости от направления движения.

        Сложность: O(N) по числу платформ за обновление.
        """
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.velocity_x > 0:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0:
                    self.rect.left = platform.rect.right

    def _is_standing_on(self, platforms: list[pygame.sprite.Sprite]) -> bool:
        """Проверяет, стоит ли игрок на платформе (даже без пересечения hitbox).

        Алгоритм: сравнивает координату стопы игрока с вершиной каждой платформы
        с небольшой допуском, учитывает горизонтальное перекрытие.

        Сложность: O(N) по числу платформ.
        """
        feet = self.rect.bottom
        for platform in platforms:
            if (
                abs(feet - platform.rect.top) <= 1
                and self.rect.right > platform.rect.left
                and self.rect.left < platform.rect.right
            ):
                return True
        return False

    def _apply_vertical_collision(self, platforms: list[pygame.sprite.Sprite]) -> None:
        """Разрешение вертикальных коллизий и детекция касания земли.

        Алгоритм: проходит по списку платформ; если игрок падает и пересекает
        платформу, ставит нижнюю границу игрока на верхнюю грань платформы и обнуляет
        вертикальную скорость. Также обрабатывает столкновение головой.

        Сложность: O(N) по числу платформ за обновление.
        """
        self.on_ground = False
        for platform in platforms:
            if self.velocity_y >= 0 and (
                self.rect.colliderect(platform.rect)
                or (
                    self.rect.bottom >= platform.rect.top - 1
                    and self.rect.bottom <= platform.rect.top + 8
                    and self.rect.right > platform.rect.left
                    and self.rect.left < platform.rect.right
                )
            ):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.on_ground = True
            elif self.rect.colliderect(platform.rect) and self.velocity_y < 0:
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

    def _try_jump(self) -> None:
        """Выполняет прыжок при наличии буфера нажатия или coyote time.

        Алгоритм: проверяет флаги `jump_buffer_frames` и `coyote_frames` и при
        выполнении условий устанавливает вертикальную скорость в `JUMP_POWER`.

        Сложность: O(1).
        """
        can_jump = (self.on_ground or self.coyote_frames > 0) and self.knockback_frames == 0
        if self.jump_buffer_frames > 0 and can_jump:
            self.velocity_y = JUMP_POWER
            self.on_ground = False
            self.jump_buffer_frames = 0
            self.coyote_frames = 0

    def update(self, platforms: list[pygame.sprite.Sprite], move_left: bool, move_right: bool) -> None:
        """Обновляет физику игрока, состояние анимации и обрабатывает столкновения.

        Алгоритм: рассчитывает горизонтальную скорость, применяет горизонтальные
        и вертикальные коллизии, обновляет гравитацию, coyote/jump-buffer
        и инкремент таймеров анимации.

        Сложность: O(N) по числу платформ (коллизии) + O(1) остальные операции.
        """
        moving = False
        if self.knockback_frames > 0:
            self.velocity_x = self.knockback_direction * PLAYER_KNOCKBACK_SPEED
            self.knockback_frames -= 1
            moving = True
            self.facing_right = self.knockback_direction >= 0
        else:
            self.velocity_x = 0
            if move_left:
                self.velocity_x -= 1
            if move_right:
                self.velocity_x += 1
            self.velocity_x *= 0 if (move_left and move_right) else 1
            self.velocity_x *= 4
            moving = self.velocity_x != 0
            if move_left and not move_right:
                self.facing_right = False
            elif move_right and not move_left:
                self.facing_right = True

        self.rect.x += self.velocity_x
        self._apply_horizontal_collision(platforms)

        if self.on_ground:
            self.coyote_frames = self.COYOTE_FRAMES
        elif self.coyote_frames > 0:
            self.coyote_frames -= 1

        self._try_jump()

        if self.on_ground and not self._is_standing_on(platforms):
            self.on_ground = False

        if not self.on_ground:
            self.velocity_y += GRAVITY
            self.rect.y += int(self.velocity_y)
        else:
            self.velocity_y = 0

        self._apply_vertical_collision(platforms)

        if moving or not self.on_ground:
            self.animation_tick += 1

        if self.jump_buffer_frames > 0:
            self.jump_buffer_frames -= 1

    def draw(self, surface: pygame.Surface, camera: Camera) -> None:
        """Рисует игрока с учётом камеры и тени.

        Описание: выбирает текущий кадр анимации в зависимости от состояния
        (прыжок / ходьба / простое стояние), выполняет отражение спрайта и
        рисует тень под персонажем.

        Сложность: O(1) за вызов (рисование — зависит от размера поверхности).
        """
        rect = camera.apply(self.rect)
        if not self.on_ground:
            frame = self.jump_frame
        elif abs(self.velocity_x) > 0:
            frame = self.walk_frames[(self.animation_tick // 6) % len(self.walk_frames)]
        else:
            frame = self.idle_frame

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        frame_rect = frame.get_rect(midbottom=(int(rect.centerx), int(rect.bottom)))
        shadow = pygame.Surface((frame_rect.width, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
        surface.blit(shadow, (frame_rect.x, frame_rect.bottom - 8))
        surface.blit(frame, frame_rect)
