import pygame
from engine import assets


class Level:
    def __init__(self, name="level_01"):
        self.name = name
        self.platforms = [
            pygame.Rect(0, 432, 800, 48),
            pygame.Rect(180, 350, 120, 24),
            pygame.Rect(360, 290, 140, 24),
        ]
        self.spawn_point = (80, 200)

        # try to load tiles for background drawing
        self.tiles = assets.load_tiles()
        manifest = assets.load_manifest() or {}
        self.tile_size = manifest.get("tile_size", 16)

    def draw(self, surface, color=(80, 90, 120)):
        # draw tiled background if tiles available
        if self.tiles:
            ts = self.tile_size
            cols = surface.get_width() // ts + 1
            rows = surface.get_height() // ts + 1
            # pick a simple grass/tile index (first tile) to fill
            tile_img = self.tiles[0]
            for y in range(rows):
                for x in range(cols):
                    surface.blit(tile_img, (x * ts, y * ts))
        else:
            surface.fill((40, 44, 56))

        # draw platforms on top
        for platform in self.platforms:
            pygame.draw.rect(surface, color, platform)
