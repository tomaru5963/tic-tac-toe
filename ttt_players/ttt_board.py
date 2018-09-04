import numpy as np


class TTTBoard(object):

    NUM_ROWS = 3
    NUM_COLS = 3

    EMPTY = 0
    PLAYER_X = 1
    PLAYER_O = 2

    ACTIVE = 0
    WON_X = 1
    WON_O = 2
    DRAW = 3

    def __init__(self, display=True):
        self.display = display
        self.board = np.zeros((self.NUM_ROWS, self.NUM_COLS))
        self.state = self.ACTIVE

    def get_empty_places(self):
        rows, cols = np.where(self.board == self.EMPTY)
        return list(zip(rows, cols))

    def make_next_move(self, pos, player):
        assert self.board[pos] == self.EMPTY

        self.board[pos] = player
        self.update_state()
        if self.display:
            self.show()

    def update_state(self):
        for row in range(self.NUM_ROWS):
            if self.is_lined_up(self.board[row]):
                return
        for col in range(self.NUM_COLS):
            if self.is_lined_up(self.board[:, col]):
                return
        if self.is_lined_up(self.board.diagonal()):
            return
        if self.is_lined_up(np.flip(self.board, axis=1).diagonal()):
            return
        if np.all(self.board != self.EMPTY):
            self.state = self.DRAW
            return

    def is_lined_up(self, line):
        if len(set(line)) == 1 and line[0] != self.EMPTY:
            if line[0] == self.PLAYER_X:
                self.state = self.WON_X
            else:
                self.state = self.WON_O
            return True
        else:
            return False

    def show(self):
        head_tail = '----' * self.NUM_COLS + '-'
        state_message = {self.ACTIVE: '',
                         self.WON_X: 'Won by X',
                         self.WON_O: 'Won by O',
                         self.DRAW: 'Drawn'}

        for row in self.board:
            print(head_tail)
            for cell in row:
                if cell == self.EMPTY:
                    print('|   ', end='')
                elif cell == self.PLAYER_X:
                    print('| X ', end='')
                else:
                    print('| O ', end='')
            print('|')
        print(head_tail, state_message[self.state])
