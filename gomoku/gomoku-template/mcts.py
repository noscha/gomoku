from game_state import GameState
from evaluator import Evaluator
from constants import Piece
import threading

class MonteCarloNode:
    """
    TODO: Implement
    """
    def __init__(self):
        pass

class MonteCarloEngine:

    def __init__(self, board=None, player=Piece.BLACK.value) -> None:
        self.game_state = GameState(board, player, self.zobrist) 
        
        # TODO: Change if necessary
        self.root_node = None
        
        self.identity = player
        self.current_result = (-1, -1)
        self.stop_event = threading.Event()
        self.evaluation_thread = None

        # Statisticss
        self.simulations = 0

    def start_evaluation(self, position, player, max_depth = 20):
        """
        Startet die Evaluation aus der GUI
        Muss nicht verändert werden.
        """
        self.stop_event.clear()

        self.game_state = GameState(position, player)
        self.identity = player

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
    
    def mcts(self):
        """
        Nutzt Iterative Deepening um für jede Tiefe den besten Zug zu finden.
        Terminiert entweder wenn maximale Tiefe erreicht wurde oder
        wenn von GUI das Stoppsignal kommt.

        """
        k = 0
        simulation_depth = 10
        while not self.stop_event.is_set():
            next_node = self.tree_policy(self.root_node)
            reward = self.simulate(next_node, simulation_depth)
            self.update(next_node, reward)

            # Nachfolgend sollte nichts verändert werden
            move = self.most_visited_child(self.root_node)
            self.current_result = move
            print(f'simulations: {k}, move: {move}') 
            k+=1
    
    def tree_policy(self, node):
        """
        Select next node to explore / exploit
        """
        pass

    def best_child(self, node):
        """
        Selects best child node. Should use the UCB-Formula
        """
        pass

    def simulate(self, node, depth):
        """
        Simulates from the given node. But only to certain depth
        then uses evaluation function to estimate reward.
        """
        pass

    def update(self, node, reward):
        """
        Backpropagates reward up to root node.
        """
        pass

    def most_visited_child(self, node):
        """
        Returns the most visited node.
        """
        pass