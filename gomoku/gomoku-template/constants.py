from enum import Enum

"""
In dieser Datei sind die Konstanten und Threat-Typen mit zugehöriger Gewichtung deklariert.
"""

class Piece(Enum):
    BLACK = 1
    WHITE = -1

class  Threats(Enum):
    FIVE = 1e15

    OPEN_FOUR = 1e5
    BLOCKED_FOUR = 1e4
    OPEN_POKED_FOUR = 1e4
    BLOCKED_POKED_FOUR = 4

    OPEN_THREE = 5e3
    BLOCKED_THREE = 1670
    OPEN_POKED_THREE = 5e3
    BLOCKED_POKED_THREE = 1670

    OPEN_TWO = 1500
    BLOCKED_TWO = 500
    OPEN_POKED_TWO = 1500
    BLOCKED_POKED_TWO = 300

    NONE = 0