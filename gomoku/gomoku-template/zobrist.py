import random
from constants import Piece
class Zobrist:
    """
    Diese Klasse ist zur Berechnung der Hash-Werte von Gomoku Stellungen zuständig.
    Die Klasse muss ausimplementiert werden, wie auf dem Projektblatt beschrieben.
    """

    def __init__(self) -> None:
        pass

    def update_hash(self, old_hash: int, row: int, col: int, player: int) -> int:
        """
        Die Methode bekommt den bisherigen Hash-Wert einer Stellung und den 
        gemachten Zug übergeben. Daraus berechnet die Methode den neuen Hashwert der Stellung
        und gibt diesen zurück.
        """
        pass