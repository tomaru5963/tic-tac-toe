import ttt_board


class TTTGame(object):

    def __init__(self, player1, player2, display=False):
        self.display = display
        self.player1 = player1
        self.player2 = player2

    def play(self):
        board = ttt_board.TTTBoard(self.display)

        if self.display:
            print(f'X: {self.player1.name}, O: {self.player2.name}')

        self.player1.on_game_started(board, board.PLAYER_X)
        self.player2.on_game_started(board, board.PLAYER_O)

        while True:
            pos = self.player1.on_next_move_required(board, board.PLAYER_X)
            board.make_next_move(pos, board.PLAYER_X)
            if board.state != board.ACTIVE:
                break
            pos = self.player2.on_next_move_required(board, board.PLAYER_O)
            board.make_next_move(pos, board.PLAYER_O)
            if board.state != board.ACTIVE:
                break
        pos = self.player1.on_next_move_required(board, board.PLAYER_X)
        assert pos is None
        pos = self.player2.on_next_move_required(board, board.PLAYER_O)
        assert pos is None

        self.player1.on_game_finished(board, board.PLAYER_X)
        self.player2.on_game_finished(board, board.PLAYER_O)

        if self.display:
            print(f'X: {self.player1.name}, O: {self.player2.name}')

        return board.state
