"""Данные для всех уровней платформера."""

LEVELS = {
    1: {
        "platforms": [
            {"x": 0, "y": 550, "w": 800, "h": 50},
            {"x": 200, "y": 450, "w": 100, "h": 20},
            {"x": 500, "y": 350, "w": 100, "h": 20},
        ],
        "items": [
            {"x": 300, "y": 520, "type": "coin"},
            {"x": 550, "y": 420, "type": "coin"},
        ],
        "enemies": [
            {"x": 400, "y": 520, "patrol_left": 300, "patrol_right": 500},
        ],
        "door_spawn_platform": {"platform_index": 2, "offset_x": 610, "offset_y": 110},
        "items_to_collect": 2,
    },
    2: {
        "platforms": [
            {"x": 0, "y": 550, "w": 800, "h": 50},
            {"x": 150, "y": 450, "w": 120, "h": 20},
            {"x": 400, "y": 380, "w": 100, "h": 20},
            {"x": 600, "y": 300, "w": 100, "h": 20},
            {"x": 300, "y": 200, "w": 80, "h": 20},
            {"x": 550, "y": 120, "w": 80, "h": 20},
        ],
        "items": [
            {"x": 200, "y": 520, "type": "coin"},
            {"x": 450, "y": 360, "type": "coin"},
            {"x": 650, "y": 280, "type": "coin"},
            {"x": 340, "y": 180, "type": "coin"},
        ],
        "enemies": [
            {"x": 350, "y": 520, "patrol_left": 250, "patrol_right": 450},
            {"x": 500, "y": 360, "patrol_left": 450, "patrol_right": 650},
        ],
        "door_spawn_platform": {"platform_index": 5, "offset_x": 560, "offset_y": 80},
        "items_to_collect": 4,
    },
    3: {
        "platforms": [
            {"x": 0, "y": 550, "w": 800, "h": 50},
            {"x": 100, "y": 470, "w": 100, "h": 20},
            {"x": 350, "y": 400, "w": 100, "h": 20},
            {"x": 550, "y": 320, "w": 100, "h": 20},
            {"x": 200, "y": 250, "w": 80, "h": 20},
            {"x": 500, "y": 180, "w": 80, "h": 20},
            {"x": 650, "y": 100, "w": 80, "h": 20},
        ],
        "items": [
            {"x": 150, "y": 520, "type": "coin"},
            {"x": 400, "y": 380, "type": "coin"},
            {"x": 600, "y": 300, "type": "coin"},
            {"x": 240, "y": 230, "type": "coin"},
            {"x": 540, "y": 160, "type": "coin"},
            {"x": 680, "y": 80, "type": "coin"},
        ],
        "enemies": [
            {"x": 250, "y": 520, "patrol_left": 150, "patrol_right": 400},
            {"x": 450, "y": 380, "patrol_left": 350, "patrol_right": 550},
            {"x": 600, "y": 300, "patrol_left": 550, "patrol_right": 700},
        ],
        "door_spawn_platform": {"platform_index": 6, "offset_x": 660, "offset_y": 40},
        "items_to_collect": 6,
    },
}