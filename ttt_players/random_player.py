import numpy as np

from .player_base import PlayerBase


class RandomPlayer(PlayerBase):

    def __init__(self, name='RandomPlayer', train=False):
        super(RandomPlayer, self).__init__(name, train)

    def on_next_move_required(self, board, who_am_i):
        if board.state != board.ACTIVE:
            return None

        empties = board.get_empty_places()
        pos = empties[np.random.randint(len(empties))]
        return pos
