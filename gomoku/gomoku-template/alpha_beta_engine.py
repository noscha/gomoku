from game_state import GameState
from evaluator import Evaluator
from constants import Piece
import threading

class AlphaBetaEngine:

    def __init__(self, board=None, player=Piece.BLACK.value) -> None:
        self.game_state = GameState(board, player) 
        self.transposition_table = {}
        
        self.identity = player
        self.current_result = (-1, -1)
        self.stop_event = threading.Event()
        self.evaluation_thread = None

        # Statistics
        self.nodes = 0
        self.alpha_cuts = 0
        self.beta_cuts = 0

    def start_evaluation(self, position, player, max_depth = 20):
        """
        Startet die Evaluation aus der GUI
        Muss nicht verändert werden.
        """
        self.stop_event.clear()

        self.game_state = GameState(position, player)
        #self.transposition_table = {}
        self.identity = player
        self.nodes, self.alpha_cuts, self.beta_cuts = 0, 0, 0

        self.evaluation_thread = threading.Thread(target=self.iterative_deepening, args=[max_depth])
        self.evaluation_thread.start()

    def stop_evaluation(self):
        """
        Stoppt die Evaluation aus der GUI
        Muss nicht verändert werden.
        """
        if self.evaluation_thread is not None:
            self.stop_event.set()
            self.evaluation_thread.join()
            self.evaluation_thread = None
            self.current_result = (-1, -1)

    def get_results(self):
        """
        Meldet den aktuell besten Zug an die GUI
        """
        return self.current_result
    
    def is_terminal(self, score):
        return score >= Evaluator.WIN or score <= -Evaluator.WIN
    
    def iterative_deepening(self, max_depth = 10):
        """
        Nutzt Iterative Deepening um für jede Tiefe den besten Zug zu finden.
        Terminiert entweder wenn maximale Tiefe erreicht wurde oder
        wenn von GUI das Stoppsignal kommt.
        """
        d = 1

        while d <= max_depth and not self.stop_event.is_set():
            score, move = self.alpha_beta(1, d, self.identity)
            self.current_result = move
            print(f'depth: {d}, move: {move}, eval: {score}, nodes: {self.nodes}, alpha-cuts: {self.alpha_cuts}, beta-cuts: {self.beta_cuts}') 
            d+= 1

    def alpha_beta(self, depth: int, remaining_depth, player: int, alpha: int = float('-inf'), beta: int = float('inf')) :
        pass
    