from pygame import Rect


class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.offset = [0, 0]

    def follow(self, target_rect):
        self.offset[0] = max(0, target_rect.centerx - self.width // 2)
        self.offset[1] = max(0, target_rect.centery - self.height // 2)

    def apply(self, rect):
        return Rect(rect.x - self.offset[0], rect.y - self.offset[1], rect.width, rect.height)
