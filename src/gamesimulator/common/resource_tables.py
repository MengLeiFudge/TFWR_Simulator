from __future__ import annotations


ENTITY_GROWTH_RANGES = {
    "Grass": (0.5, 0.5),
    "Bush": (3.2, 4.8),
    "Tree": (5.6, 8.4),
    "Carrot": (4.8, 7.2),
    "Sunflower": (5.6, 8.4),
    "Cactus": (1.0, 1.0),
    "Pumpkin": (0.2, 3.8),
    "Dinosaur": (0.18, 0.22),
    "Dead_Pumpkin": (0.0, 0.0),
    "Treasure": (0.0, 0.0),
    "Hedge": (0.0, 0.0),
}

ENTITY_ALLOWED_GROUNDS = {
    "Grass": {"Grounds.Grassland", "Grounds.Soil"},
    "Bush": {"Grounds.Grassland", "Grounds.Soil"},
    "Tree": {"Grounds.Grassland", "Grounds.Soil"},
    "Carrot": {"Grounds.Soil"},
    "Sunflower": {"Grounds.Soil"},
    "Cactus": {"Grounds.Soil"},
    "Pumpkin": {"Grounds.Soil"},
    "Dinosaur": {"Grounds.Grassland", "Grounds.Soil"},
}

COMPANION_ENTITIES = {"Grass", "Bush", "Tree", "Carrot"}

COMPANION_OFFSETS = [
    (-3, 0), (-2, -1), (-2, 0), (-2, 1),
    (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2),
    (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3),
    (1, -2), (1, -1), (1, 0), (1, 1), (1, 2),
    (2, -1), (2, 0), (2, 1), (3, 0),
]
