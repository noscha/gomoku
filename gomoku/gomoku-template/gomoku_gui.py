import tkinter as tk
from alpha_beta_engine import AlphaBetaEngine
from mcts import MonteCarloEngine
import numpy as np

class GomokuGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Gomoku")
        self.board_size = 15
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        self.ai_algorithm = tk.StringVar(value="None")
        self.hover_item = None
        self.winner = None
        self.winning_line = []
        self._ai_suggestion = (-1, -1)
        self.engine = None

        self.show_ai_sugg_black = tk.IntVar()
        self.show_ai_sugg_white = tk.IntVar()

        self.create_widgets()
        self.draw_board()

    @property
    def ai_suggestion(self):
        return self._ai_suggestion
    
    @ai_suggestion.setter
    def ai_suggestion(self, new_value):
        self._ai_suggestion = new_value
        self.draw_board()

    def create_widgets(self):
        # Create board canvas
        self.canvas = tk.Canvas(self.master, width=600, height=600)
        self.canvas.pack(side=tk.LEFT)
        self.canvas.bind("<Button-1>", self.handle_click)
        self.canvas.bind("<Motion>", self.handle_motion)
        
        # Create control panel
        self.control_panel = tk.Frame(self.master)
        self.control_panel.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.control_panel, text="Select AI Algorithm:").pack()
        self.ai_selection = tk.OptionMenu(self.control_panel, self.ai_algorithm, "None", "alpha-beta", "mcts")
        self.ai_selection.pack()
        self.ai_algorithm.trace_add('write', self.trigger_ai_eval)

        self.ai_sugg_box_black = tk.Checkbutton(self.control_panel, text="Show AI Suggestions Black", variable=self.show_ai_sugg_black).pack()
        self.ai_sugg_box_white = tk.Checkbutton(self.control_panel, text="Show AI Suggestion WHITE", variable=self.show_ai_sugg_white).pack()

        self.reset_button = tk.Button(self.control_panel, text="Reset Game", command=self.reset_game)
        self.reset_button.pack()

        self.winner_label = tk.Label(self.control_panel, text="Winner: None")
        self.winner_label.pack()

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(self.board_size):
            self.canvas.create_line(20 + i * 40, 20, 20 + i * 40, 580)
            self.canvas.create_line(20, 20 + i * 40, 580, 20 + i * 40)
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j] == 1:
                    self.canvas.create_oval(20 + j * 40 - 15, 20 + i * 40 - 15, 20 + j * 40 + 15, 20 + i * 40 + 15, fill="black")
                elif self.board[i, j] == -1:
                    self.canvas.create_oval(20 + j * 40 - 15, 20 + i * 40 - 15, 20 + j * 40 + 15, 20 + i * 40 + 15, fill="white")
                elif i == self.ai_suggestion[0] and j == self.ai_suggestion[1]:
                    if self.show_ai_sugg_black.get() == 1 and self.current_player == 1:
                        self.canvas.create_oval(20 + j * 40 - 15, 20 + i * 40 - 15, 20 + j * 40 + 15, 20 + i * 40 + 15, fill='black' if self.current_player==1 else 'white', outline='green', width=5)
                    elif self.show_ai_sugg_white.get() == 1 and self.current_player == -1:
                        self.canvas.create_oval(20 + j * 40 - 15, 20 + i * 40 - 15, 20 + j * 40 + 15, 20 + i * 40 + 15, fill='black' if self.current_player==1 else 'white', outline='green', width=5)
        if self.winning_line:
            for r, c in self.winning_line:
                self.canvas.create_oval(20 + c * 40 - 15, 20 + r * 40 - 15, 20 + c * 40 + 15, 20 + r * 40 + 15,  outline="red", width=3)

    def handle_click(self, event):
        if self.winner:
            return

        x, y = event.x, event.y
        col = (x - 20) // 40
        row = (y - 20) // 40
        if abs(x - (20 + col * 40)) <= 20 and abs(y - (20 + row * 40)) <= 20:
            if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row, col] == 0:
                self.board[row, col] = self.current_player
                self.draw_board()
                if self.check_winner(row, col):
                    self.winner = self.current_player
                    self.winner_label.config(text=f"Winner: Player {self.current_player}")
                    self.draw_board()
                    return
                self.current_player = self.current_player * (-1)
                self.ai_suggestion = (-1, -1)
                self.trigger_ai_eval()

    def handle_motion(self, event):
        if self.winner:
            return

        x, y = event.x, event.y
        col = (x - 20) // 40
        row = (y - 20) // 40
        if abs(x - (20 + col * 40)) <= 20 and abs(y - (20 + row * 40)) <= 20:
            if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row, col] == 0:
                if self.hover_item:
                    self.canvas.delete(self.hover_item)
                self.hover_item = self.canvas.create_oval(20 + col * 40 - 15, 20 + row * 40 - 15, 20 + col * 40 + 15, 20 + row * 40 + 15, outline="gray", width=2)
        else:
            if self.hover_item:
                self.canvas.delete(self.hover_item)
                self.hover_item = None

    def check_winner(self, row, col):
        def check_line(start, direction):
            count = 0
            line = []
            for step in range(-4, 5):
                r = start[0] + step * direction[0]
                c = start[1] + step * direction[1]
                if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r, c] == self.current_player:
                    count += 1
                    line.append((r, c))
                    if count == 5:
                        self.winning_line = line
                        return True
                else:
                    count = 0
                    line = []
            return False

        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for direction in directions:
            if check_line((row, col), direction):
                return True
        return False

    def reset_game(self):
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        if self.engine is not None:
            self.engine.stop_evaluation()
            self.engine = None
            self.ai_suggestion = (-1, -1)
        self.current_player = 1
        self.winner = None
        self.winning_line = []
        self.winner_label.config(text="Winner: None")
        self.draw_board()

    def trigger_ai_eval(self, a1 = None, a2 = None, a3 = None):
        ai_selected = self.ai_algorithm.get()
        if self.ai_algorithm.get() == "None":
            return 
        elif ai_selected == 'alpha-beta':
            if self.engine is None:
                self.engine = AlphaBetaEngine()
            self.engine.stop_evaluation()
            self.engine.start_evaluation(self.board.tolist(), self.current_player)
            self.check_results()
        elif ai_selected == 'mcts':
            if self.engine is None:
                self.engine = MonteCarloEngine()
            self.engine.stop_evaluation()
            self.engine.start_evaluation(self.board.tolist(), self.current_player)
            self.check_results()

    
    def check_results(self):
        if self.engine is not None:
            new = self.engine.get_results()
            if self.ai_suggestion != new:
                self.ai_suggestion = new
                
            if not self.engine.stop_event.is_set():
                self.master.after(200, self.check_results)


def main():
    root = tk.Tk()
    game = GomokuGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
