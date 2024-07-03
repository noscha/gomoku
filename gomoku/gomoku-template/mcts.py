import math
import random

from game_state import GameState
from evaluator import Evaluator
from constants import Piece
import threading


class MonteCarloNode:

    def __init__(self, move=None, parent=None):
        self.move = move
        self.reward = 0
        self.visits = 0
        self.parent = parent
        self.visited_children = set()
        self.children = []


class MonteCarloEngine:

    def __init__(self, board=None, player=Piece.BLACK.value) -> None:
        self.game_state = GameState(board, player)
        self.root_node = None

        self.identity = player
        self.current_result = (-1, -1)
        self.stop_event = threading.Event()
        self.evaluation_thread = None

        # Statisticss
        self.simulations = 0

    def start_evaluation(self, position, player, iterations=1000):
        """
        Startet die Evaluation aus der GUI

        """
        self.stop_event.clear()

        self.game_state = GameState(position, player)
        self.identity = player

        self.evaluation_thread = threading.Thread(target=self.mcts, args=[iterations])
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

    def mcts(self, iterations=1000):
        """
        Nutzt Monte-Carlo Tree Search um besten Zug zu finden.
        Terminiert entweder wenn maximale Anzahl an Iterationen erreicht wurde oder
        wenn von GUI das Stoppsignal kommt.

        """
        self.root_node = MonteCarloNode()
        k = 0
        simulation_depth = 10
        while not self.stop_event.is_set() and k < iterations:
            next_node = self.tree_policy(self.root_node)
            reward = self.simulate(next_node, simulation_depth)
            self.update(next_node, reward)

            # Nachfolgend sollte nichts verändert werden
            move = self.most_visited_child(self.root_node)
            self.current_result = move
            print(f'simulations: {k}, move: {move}')
            k += 1

    def tree_policy(self, node):
        """
        Select next node to explore / exploit
        """
        while not self.is_terminal(self.game_state.get_heuristic_value()):
            moves = [(col, row) for col, row, _ in self.game_state.get_sorted_moves()]
            if len(moves) > len(node.visited_children):
                move = moves.pop()
                while move in node.visited_children:
                    move = moves.pop()

                # expand
                node.visited_children.add(move)
                self.game_state.make_move(*move)
                new_node = MonteCarloNode(move=move, parent=node)
                node.children.append(new_node)
                return new_node
            else:
                node = self.best_child(node)
        return node

    def best_child(self, node):
        """
        Selects best child node. Should use the UCB-Formula
        """
        ucb_scores = [child.reward / node.visits + math.sqrt(2) * math.sqrt((2 * math.log(node.visits)) / child.visits)
                      for child in node.children]
        best_child = node.children[ucb_scores.index(max(ucb_scores))]
        self.game_state.make_move(*best_child.move)
        return best_child

    def simulate(self, node, depth):
        """
        Simulates from the given node. But only to certain depth
        then uses evaluation function to estimate reward.
        """
        reward, changes = 0, 0
        while depth > 0 and not self.is_terminal(self.game_state.get_heuristic_value()):
            row, col, t = random.choice(self.game_state.get_sorted_moves())
            self.game_state.make_move(row, col)
            reward = self.game_state.get_heuristic_value()
            depth -= 1
            changes += 1

        # undo moves
        for i in range(changes):
            self.game_state.undo_move()

        return reward

    def update(self, node, reward):
        """
        Backpropagates reward up to root node.

        """
        while node.move:
            node.visits += 1
            node.reward += reward
            reward = -reward
            self.game_state.undo_move()
            node = node.parent
        self.root_node.visits += 1

    def most_visited_child(self, node):
        """
        Returns the most visited node.
        """
        return max(node.children, key=lambda child: child.visits).move
