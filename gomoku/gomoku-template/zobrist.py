import random
import numpy as np
from constants import Piece


class Zobrist:
    """
    Diese Klasse ist zur Berechnung der Hash-Werte von Gomoku Stellungen zuständig.
    Die Klasse muss ausimplementiert werden, wie auf dem Projektblatt beschrieben.
    """

    def __init__(self) -> None:
        self.white = np.random.randint(2**15 - 1, 2**31 - 1, size=(15, 15))
        self.black = np.random.randint(2**15 - 1, 2**31 - 1, size=(15, 15))

    def update_hash(self, old_hash: int, row: int, col: int, player: int) -> int:
        """
        Die Methode bekommt den bisherigen Hash-Wert einer Stellung und den 
        gemachten Zug übergeben. Daraus berechnet die Methode den neuen Hashwert der Stellung
        und gibt diesen zurück.
        """
        return old_hash ^ self.white[row, col] if player == Piece.WHITE.value else old_hash ^ self.black[row, col]
