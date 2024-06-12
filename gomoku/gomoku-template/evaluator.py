from constants import Piece, Threats

class Evaluator:
    """
    Diese Klasse ist für die Evaluationslogik verantwortlich. Hier muss nichts verändert werden.
    """

    # Das ist der Threshold-Wert, ab dem eine Stellung gewonnen ist.
    WIN = 1e14

    def __init__(self) -> None:
        self.pattern_hash = {}

    def get_lines_in_each_direction(self, board: list[list[Piece]], row: int, col: int, player: Piece):

        def walk(dir_x: int, dir_y: int):
            seq = []
            empty = 0

            for i in range(1, 6):
                cur_row = row + dir_y * i
                cur_col = col + dir_x * i

                if not (cur_col >= 0 and cur_col < 15 and cur_row >= 0 and cur_row < 15):
                    seq.append(player * (-1))
                    break
                
                piece = board[cur_row][cur_col]
                if piece == 0:
                    seq.append(0)
                    if empty > 0:
                        break
                    empty += 1
                else:
                    seq.append(piece)
                    if piece == player * (-1):
                        break
                        
            return seq
        
        def get_line(neg_dir_x, neg_dir_y, pos_dir_x, pos_dir_y):
            seq = walk(neg_dir_x, neg_dir_y)
            seq.reverse()
            seq.append(player)
            seq += walk(pos_dir_x, pos_dir_y)

            return tuple(seq)

        h_seq = get_line(-1, 0, 1, 0)
        v_seq = get_line(0, -1, 0, 1)
        d1_seq = get_line(-1, 1, 1, -1)
        d2_seq = get_line(-1, -1, 1, 1)

        return (h_seq, v_seq, d1_seq, d2_seq)
    
    def find_patterns(self, seq: list[Piece], a: int, b: int, player: Piece) -> list:
        gap = 0
        same = 0
        started = False
        startIdx = -1
        endIdx = -1
        pendingGap = 0
        gapIdx = -1
        identifiedPattern = []

        for i in range(a, b):
            piece = seq[i]
            assert piece != player*(-1)

            if piece == 0:
                if started:
                    pendingGap += 1
            else:
                same += 1
                gap += pendingGap
                if gap > 1:
                    endIdx = i - 2

                    pattern = (same - 1, 1, startIdx, endIdx, gapIdx)
                    identifiedPattern.append(pattern)

                    startIdx = endIdx
                    tmp = 0
                    while seq[startIdx - 1] == player:
                        startIdx -= 1
                        tmp += 1
                    endIdx = startIdx
                    same = tmp + 1
                    gap = 1
                
                if pendingGap == 1:
                    gapIdx = i - 1 - startIdx
                
                pendingGap = 0

                if not started:
                    startIdx = i
                
                started = True

            if pendingGap > 1:
                endIdx = i - pendingGap
                pattern = (same, gap, startIdx, endIdx, gapIdx)
                identifiedPattern.append(pattern)

                pendingGap = 0
                startIdx = i
                same = 0
                gap = 0
                endIdx = i
                started = False

        endIdx = b
        if pendingGap == 1:
            endIdx -= 1
        pattern = (same, gap, startIdx, endIdx, gapIdx)
        identifiedPattern.append(pattern)

        return list(filter(lambda x: x[0] > 1, identifiedPattern))
    
    def get_threats_in_line(self, seq: list[Piece], player: Piece) -> list[Threats]:
        left_blocked = seq[0] == player * (-1)
        right_blocked = seq[-1] == player * (-1)

        if left_blocked and right_blocked:
            if len(seq) -2 < 5:
                return []
            else:
                start = 1
                end = len(seq) - 1
                patterns = self.find_patterns(seq, start, end, player)
                threat_types = []

                for i in range(len(patterns)):
                    p = patterns[i]
                    blocked = p[2] == start or p[3] == end
                    t = self.get_threat_type(p, blocked)
                    threat_types.append(t)
        elif left_blocked:
            patterns = self.find_patterns(seq, 1, len(seq), player)
            threat_types = []

            for i in range(len(patterns)):
                p = patterns[i]
                blocked = p[2] == 1
                t = self.get_threat_type(p, blocked)
                threat_types.append(t)
        
        elif right_blocked:
            patterns = self.find_patterns(seq, 0, len(seq) - 1, player)
            threat_types = []

            for i in range(len(patterns)):
                p = patterns[i]
                blocked = p[2] == len(seq) - 1
                t = self.get_threat_type(p, blocked)
                threat_types.append(t)
        else:
            patterns = self.find_patterns(seq, 0, len(seq), player)
            threat_types = []

            for i in range(len(patterns)):
                p = patterns[i]
                t = self.get_threat_type(p, False)
                threat_types.append(t)
        
        return threat_types
    
    def get_threat_type(self, pattern: tuple[int, int, int, int, int], blocked: bool):
        same = pattern[0]
        gap = pattern[1]
        gap_index = pattern[4]

        if gap > 1:
            return Threats.NONE
        if gap == 1:
            if same == 2:
                return Threats.BLOCKED_POKED_TWO if blocked else Threats.OPEN_POKED_TWO
            elif same == 3:
                return Threats.BLOCKED_POKED_THREE if blocked else Threats.OPEN_POKED_THREE
            elif same == 4:
                return Threats.BLOCKED_POKED_FOUR if blocked else Threats.OPEN_POKED_FOUR
            else:
                # 5
                if same > 5:
                    if gap_index == 5 or same - gap_index == 5:
                        return Threats.FIVE
        else: # gap = 0
            if same == 2:
                 return Threats.BLOCKED_TWO if blocked else Threats.OPEN_TWO
            elif same == 3:
                return Threats.BLOCKED_THREE if blocked else Threats.OPEN_THREE
            elif same == 4:
                return Threats.BLOCKED_FOUR if blocked else Threats.OPEN_FOUR
            elif same == 5:
                return Threats.FIVE
            else:
                return Threats.NONE
        
        return Threats.NONE
    
    def evaluate(self, board: list[list[Piece]], row, col, player: int):
        sequences = self.get_lines_in_each_direction(board, row, col, player)
        threats = []
        for seq in sequences:
            if seq in self.pattern_hash:
                threats += self.pattern_hash[seq]
            else:
                t = self.get_threats_in_line(seq, player)
                self.pattern_hash[seq] = t
                threats += t

        threats.sort(key=lambda x: x.value, reverse=True)
        
        if len(threats) == 0:
            return 0
        elif len(threats) == 1:
            return threats[0].value
        else:
            return threats[0].value + threats[1].value