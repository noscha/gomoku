from constants import Piece
from evaluator import Evaluator
from zobrist import Zobrist
from copy import deepcopy

class GameState:

    def __init__(self, board: list[list[int]] = None, player=Piece.BLACK.value) -> None:
        self.evaluator = Evaluator()
        self.zobrist = Zobrist()

        self.active_map: list[list[bool]] = [[False for _ in range(15)] for _ in range(15)]

        # Spieler, der aktuell am Zug ist
        self.player = player
        # Speichert den bisherigen Spielverlauf als Stack. Jedes Element ist vom Typ (row, col, active_map_changes, player, zobrist_hash)
        self.move_history = []
        # Zobrist-Hash Wert des aktuellen Spielzustandes
        self.zobrist_hash = 0

        # Hashmaps um bereits berechnete Werte wiederzuverwenden um neuen Wert nach einem Zug zu berechnen.
        self.heurstic_values = {}
        self.sorted_moves = {}
        self.score_maps = {}

        # Wenn GameState von einem bestehenden Spielzustand erzeugt wird, initialisiere die active_map und den Zobrist-Hash entsprechend
        if board is None:
            self.board: list[list[int]] = [[0 for col in range(15)] for row in range(15)]
        else:
            self.board = board
            for row in range(15):
                for col in range(15):
                    if self.board[row][col] != 0:
                        self.update_active_map(row, col)
                        self.zobrist.update_hash(self.zobrist_hash, row, col, self.board[row][col])
        
    
    def make_move(self, row, col):
        """
        Aktualisiert GameState um den Zug (row, col)
        """
        self.board[row][col] = self.player
        changes = self.update_active_map(row, col)
        self.move_history.append((row, col, changes, self.player, self.zobrist_hash))
        self.zobrist_hash = self.zobrist.update_hash(self.zobrist_hash, row, col, self.player)
        self.player = self.player * (-1)

    def undo_move(self):
        """
        Mache letzten Zug rückgängig
        """
        row, col, changes, last_player, last_zobrist_hash = self.move_history.pop()
        self.undo_active_map_changes(changes)
        self.board[row][col] = 0
        self.player = last_player
        self.zobrist_hash = last_zobrist_hash

    def update_active_map(self, row, col):
        """
        Wenn neuer Zug ausgeführt wird, muss die active_map aktualisiert werden.
        Das Feld auf dem der Zug gemacht wird ist danach natürlich nicht mehr "active".
        Außerdem werden im Abstand 2 vom entsprechendem Feld, alle Felder, die bisher noch nicht "active"
        waren nun active. Die gemachten Änderungen werden gespeichert um sie wieder rückgängig machen
        zu können.
        """
        dirs = [(0, 1), (1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1), (-1, 0), (0, -1)]
        changes = []

        if self.active_map[row][col] == True:
            self.active_map[row][col] = False
            changes.append((row, col))

        for d_x, d_y in dirs:
            for i in range(1, 3):
                new_row = row + i * d_y
                new_col = col + i * d_x

                if 0 <= new_row < 15 and 0 <= new_col < 15 and self.board[new_row][new_col] == 0:
                    if self.active_map[new_row][new_col] == False:
                        changes.append((new_row, new_col))
                        self.active_map[new_row][new_col] = True

        return changes
        
    def undo_active_map_changes(self, changes: list[tuple[int, int]]):
        """
        Macht die Änderungen an der active_map wieder rückgängig.
        """
        for row, col in changes:
            self.active_map[row][col] = not self.active_map[row][col]

    def invalidate(self, board, row, col):
        """
        Setzt die bereits berechneten Werte für diejenigen Felder zurückt, die durch den neuen Zug
        eventuell verändert worden sind.
        """
        dirs = [(0, 1), (1, 0), (1, 1), (-1, -1), (-1, 1), (1, -1), (-1, 0), (0, -1)]
        for dir_x, dir_y in dirs:
            cur_row, cur_col = row, col
            k = 0
            while k <= 5 and 0 <= cur_row < 15 and 0 <= cur_col < 15:
                board[cur_row][cur_col] = None
                cur_col += dir_x
                cur_row += dir_y
                k += 1

    def get_heuristic_value(self):
        """
        Evaluiert den aktuellen Spielzustand in Abhängigkeit von den Bedrohungen (insbesondere werden keine leeren Felder berücksichtigt)
        Für jedes besetzte Feld werden die Bedrohungen des jeweiligen Spielers bewertet und aufsummiert.
        Die Evaluierung geschieht immer aus Sicht des schwarzen Spielers, daher werden schwarze Bedrohungen positiv
        und weiße Bedrohungen negativ summiert.

        Der Wert wird inkrementell berechnet. Falls die aktuelle Position nicht im Cache gespeichert ist,
        versuche die letzte Position aus dem Cache zu bekommen und berechne darauf basierend inkrementell
        den neuen Wert nach dem letzten Zug.
        """
        if self.zobrist_hash in self.heurstic_values:
            score = self.heurstic_values[self.zobrist_hash]
        else:
            prev_scores = None
            if len(self.move_history) > 0:
                last_row, last_col, _, old_player, last_hash = self.move_history[-1]
                if last_hash in self.score_maps:
                    prev_scores = deepcopy(self.score_maps[last_hash])
                    self.invalidate(prev_scores, last_row, last_col)
            
            score_map = [[0 for _ in range(15)] for _ in range(15)]
            eval_value = 0
            for row in range(15):
                for col in range(15):
                    if self.board[row][col] == 0:
                        continue
                    if prev_scores is not None and prev_scores[row][col] is not None:
                        score_map[row][col] = prev_scores[row][col]
                    else:
                        score = self.evaluator.evaluate(self.board, row, col, self.board[row][col])
                        score *= 1 if self.board[row][col] == Piece.BLACK.value else -1
                        score_map[row][col] = score
                        eval_value += score
                
            self.score_maps[self.zobrist_hash] = score_map
        return eval_value

    
    def get_sorted_moves(self) -> list:
        """
        Gibt die Nachfolgerzüge der aktuellen Spielstellung austeigend geordnet nach ihrem
        "Threat-Potenzial" zurück. Dabei werden nun aktive (bezüglich der active_map) Züge berücksichtigt.
        """
        if self.zobrist_hash in self.sorted_moves:
            return self.sorted_moves[self.zobrist_hash]
        
        sorted_moves = []
        score_map = [[None for _ in range(15)] for _ in range(15)]
        if len(self.move_history) > 0:
            last_row, last_col, _, old_player, last_hash = self.move_history[-1]

            if last_hash in self.sorted_moves: 
                for row, col, score in self.sorted_moves[last_hash]:
                    score_map[row][col] = score
                self.invalidate(score_map, last_row, last_col)

        no_active_squares = True
        for row in range(15):
            for col in range(15):
                if self.active_map[row][col]:
                    no_active_squares = False
                    if score_map[row][col] is not None:
                        sorted_moves.append((row, col, score_map[row][col]))
                    else:
                        black_score = self.evaluator.evaluate(self.board, row, col, Piece.BLACK.value)
                        white_score = self.evaluator.evaluate(self.board, row, col, Piece.WHITE.value)

                        sorted_moves.append((row, col, black_score + white_score))
        
        if no_active_squares:
            sorted_moves.append((7, 7, 0))

        sorted_moves.sort(key=lambda x: x[2], reverse=True)
        self.sorted_moves[self.zobrist_hash] = sorted_moves
        return sorted_moves



