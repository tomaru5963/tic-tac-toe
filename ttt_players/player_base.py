class PlayerBase(object):

    def __init__(self, name, train):
        self.name = name
        self.train = train

    def on_game_started(self, board, who_am_i):
        pass

    def on_game_finished(self, board, who_am_i):
        pass

    def on_next_move_required(self, board, who_am_i):
        raise NotImplementedError

    def load_params(self, path):
        pass

    def save_params(self, path):
        pass
