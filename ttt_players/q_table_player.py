import numpy as np
import pickle

from .player_base import PlayerBase


class QTablePlayer(PlayerBase):

    def __init__(self, name='QTablePlayer', train=False):
        super(QTablePlayer, self).__init__(name, train)
        self.q_table = None
        self.greedy_rate = 0.3
        self.learning_rate = 0.1
        self.discount_rate = 0.9

    def on_game_started(self, board, who_am_i):
        super(QTablePlayer, self).on_game_started(board, who_am_i)
        self.state = None
        self.action = None
        if self.q_table is None:
            num_cells = board.NUM_ROWS * board.NUM_COLS
            # self.q_table = np.random.uniform(-1, 1, (3 ** num_cells, num_cells))
            self.q_table = np.zeros((3 ** num_cells, num_cells))

    @staticmethod
    def action_to_pos(board, action):
        return (action // board.NUM_COLS, action % board.NUM_COLS)

    @staticmethod
    def pos_to_action(board, pos):
        return pos[0] * board.NUM_COLS + pos[1]

    def on_next_move_required(self, board, who_am_i):
        if self.train:
            return self.on_next_move_required_for_train(board, who_am_i)

        if board.state != board.ACTIVE:
            return None

        _, action = self.choose_action(board, who_am_i)
        return QTablePlayer.action_to_pos(board, action)

    def on_next_move_required_for_train(self, board, who_am_i):
        if self.action is None:
            self.state, self.action = self.choose_action(board, who_am_i)
            return QTablePlayer.action_to_pos(board, self.action)

        reward = 0
        done = False
        if ((board.state == board.WON_X and who_am_i == board.PLAYER_X) or
                (board.state == board.WON_O and who_am_i == board.PLAYER_O)):
            reward = 1
            done = True
        elif ((board.state == board.WON_X and who_am_i == board.PLAYER_O) or
              (board.state == board.WON_O and who_am_i == board.PLAYER_X)):
            reward = -1
            done = True
        elif board.state == board.DRAW:
            done = True

        if done:
            self.q_table[self.state, self.action] = (
                (1 - self.learning_rate) * self.q_table[self.state, self.action] +
                self.learning_rate * reward)
            self.state = None
            self.action = None
            return None
        else:
            next_state, next_action = self.choose_action(board, who_am_i)
            self.q_table[self.state, self.action] = (
                (1 - self.learning_rate) * self.q_table[self.state, self.action] +
                self.learning_rate * (reward +
                                      self.discount_rate *
                                      self.q_table[next_state, next_action]))
            self.state = next_state
            self.action = next_action
            return QTablePlayer.action_to_pos(board, self.action)

    def choose_action(self, board, who_am_i):
        empties = []
        for pos in board.get_empty_places():
            empties.append(QTablePlayer.pos_to_action(board, pos))
        assert len(empties) != 0

        # calc state from board
        state = 0
        for c in board.board.reshape((-1,)):
            state *= 3
            if c == board.EMPTY:
                state += 0
            elif ((c == board.PLAYER_X and who_am_i == board.PLAYER_X) or
                  (c == board.PLAYER_O and who_am_i == board.PLAYER_O)):
                state += 1
            else:
                state += 2
        state = int(state)

        if not self.train or np.random.random() >= self.greedy_rate:
            row = self.q_table[state]
            action_idx = np.argmax(row[empties])
            action = empties[action_idx]
        else:
            action = np.random.choice(empties)
        return state, action

    def load_params(self, path):
        with open(path, 'rb') as f:
            self.q_table = pickle.load(f)

    def save_params(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.q_table, f)
