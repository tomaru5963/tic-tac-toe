import argparse

import pygame

from ttt_board import TTTBoard
from ttt_players.player_base import PlayerBase
from ttt_players.q_table_player import QTablePlayer
from ttt_players.random_player import RandomPlayer


TILE_SIZE = (96, 96)
BOARD_SIZE = (TILE_SIZE[0] * TTTBoard.NUM_COLS,
              TILE_SIZE[1] * TTTBoard.NUM_ROWS)
MSG_AREA_SIZE = (BOARD_SIZE[0], TILE_SIZE[1])
FONT_SIZE = TILE_SIZE[1] // 3
WINDOW_SIZE = (BOARD_SIZE[0], BOARD_SIZE[1] + MSG_AREA_SIZE[1])


class HumanPlayer(PlayerBase):

    def __init__(self, name='Human', train=False):
        super(HumanPlayer, self).__init__(name, train)


PLAYERS = {'random': RandomPlayer,
           'q_table': QTablePlayer,
           'human': HumanPlayer}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('player1', nargs='?', default='random')
    parser.add_argument('player2', nargs='?', default='human')
    parser.add_argument('--load1', metavar='FILE')
    parser.add_argument('--load2', metavar='FILE')
    args = parser.parse_args()

    player1 = PLAYERS[args.player1](train=False)
    player2 = PLAYERS[args.player2](train=False)

    if args.load1:
        player1.load_params(args.load1)
    if args.load2:
        player2.load_params(args.load2)

    pygame.init()
    GUIGame(player1, player2).play()
    pygame.quit()


class GUIGame(object):

    def __init__(self, player1, player2):
        self.players = {TTTBoard.PLAYER_X: player1,
                        TTTBoard.PLAYER_O: player2}
        self.who_am_i = TTTBoard.PLAYER_X
        self.board = TTTBoard(display=False)

        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        self.font = pygame.font.Font(None, FONT_SIZE)
        images = self.build_images(self.screen.get_size())
        self.background = images['background']
        self.mouse_images = {TTTBoard.PLAYER_X: images['cross'],
                             TTTBoard.PLAYER_O: images['circle']}

        self.tiles = pygame.sprite.RenderUpdates()
        for row in range(TTTBoard.NUM_ROWS):
            for col in range(TTTBoard.NUM_COLS):
                self.tiles.add(self.Tile(col * TILE_SIZE[0],
                                         row * TILE_SIZE[1],
                                         images,
                                         (row, col), self.board))
        self.msg_area_rect = pygame.Rect(
            (0, TTTBoard.NUM_ROWS * TILE_SIZE[1]),
            (TTTBoard.NUM_COLS * TILE_SIZE[0], TILE_SIZE[1])
        )

    def play(self):
        for who_am_i in (TTTBoard.PLAYER_X, TTTBoard.PLAYER_O):
            self.players[who_am_i].on_game_started(self.board, who_am_i)

        clock = pygame.time.Clock()
        mouse_pos = (0, 0)
        is_running = True
        while is_running:
            clock.tick(30)

            place = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False
                else:
                    place = self.handle_event(event)
                    if event.type == pygame.MOUSEMOTION:
                        mouse_pos = event.pos

            self.make_next_move(place)
            self.update(mouse_pos)

        if self.board.state != TTTBoard.ACTIVE:
            for who_am_i in (TTTBoard.PLAYER_X, TTTBoard.PLAYER_O):
                if not self.is_human(who_am_i):
                    place = self.players[who_am_i].on_next_move_required(self.board, who_am_i)
                    assert place is None
                self.players[who_am_i].on_game_finished(self.board, who_am_i)

    def is_human(self, who_am_i):
        return isinstance(self.players[who_am_i], HumanPlayer)

    def make_next_move(self, place):
        if self.board.state != TTTBoard.ACTIVE:
            return

        if self.is_human(self.who_am_i):
            if place is None:
                return
        else:
            place = self.players[self.who_am_i].on_next_move_required(self.board, self.who_am_i)

        self.board.make_next_move(place, self.who_am_i)
        if self.who_am_i == TTTBoard.PLAYER_X:
            self.who_am_i = TTTBoard.PLAYER_O
        else:
            self.who_am_i = TTTBoard.PLAYER_X

    def update(self, mouse_pos):
        self.tiles.update()
        self.screen.blit(self.background, (0, 0))
        self.tiles.draw(self.screen)

        player = 'X' if self.who_am_i == TTTBoard.PLAYER_X else 'O'
        message = f"{player}: {self.players[self.who_am_i].name}'s turn"
        if self.board.state != TTTBoard.ACTIVE:
            if self.board.state == TTTBoard.WON_X:
                message = f"X: {self.players[TTTBoard.WON_X].name} won"
            elif self.board.state == TTTBoard.WON_O:
                message = f"O: {self.players[TTTBoard.WON_O].name} won"
            else:
                message = 'The game was drawn'
        text = self.font.render(message, True, (250, 250, 250))
        message_rect = text.get_rect()
        message_rect.center = self.msg_area_rect.center
        self.screen.blit(text, message_rect)

        if (self.is_human(self.who_am_i) and
                self.board.state == TTTBoard.ACTIVE):
            image = self.mouse_images[self.who_am_i]
            rect = image.get_rect()
            rect.center = mouse_pos
            self.screen.blit(image, rect)

        pygame.display.update()

    def handle_event(self, event):
        place = None
        for tile in self.tiles:
            place = tile.handle_event(event) if place is None else place
        return place

    @staticmethod
    def build_images(screen_size):
        WHITE = (250, 250, 250)
        GREEN = (0, 128, 0)

        images = {}
        image = pygame.Surface(TILE_SIZE, flags=pygame.SRCALPHA)
        rect = image.get_rect()

        # cross
        images['cross'] = image.copy()
        temp_rect = rect.copy()
        temp_rect.width = int(temp_rect.width * .7)
        temp_rect.height = int(temp_rect.height * .7)
        temp_rect.center = rect.center
        pygame.draw.line(images['cross'], WHITE, temp_rect.topleft, temp_rect.bottomright, 5)
        pygame.draw.line(images['cross'], WHITE, temp_rect.topright, temp_rect.bottomleft, 5)

        # circle
        images['circle'] = image.copy()
        pygame.draw.circle(images['circle'], WHITE, temp_rect.center, temp_rect.width // 2, 5)

        # empty tile
        images['empty_tile'] = image.copy()
        pygame.draw.rect(images['empty_tile'], WHITE, rect, 2)

        # placeable tile
        images['placeable_tile'] = images['empty_tile'].copy()
        images['placeable_tile'].fill((255, 255, 255, 128))

        # cross tile
        images['cross_tile'] = images['empty_tile'].copy()
        images['cross_tile'].blit(images['cross'], (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # circle tile
        images['circle_tile'] = images['empty_tile'].copy()
        images['circle_tile'].blit(images['circle'], (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # background
        images['background'] = pygame.Surface(screen_size)
        images['background'].fill(GREEN)

        return images

    class Tile(pygame.sprite.Sprite):

        def __init__(self, x, y, images, place, board):
            super(GUIGame.Tile, self).__init__()
            self.images = images
            self.image = self.images['empty_tile']
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
            self.is_mouse_on = False

            self.place = place
            self.board = board

        def handle_event(self, event):
            self.is_mouse_on = False
            if (event.type == pygame.MOUSEMOTION and
                    self.rect.collidepoint(event.pos)):
                self.is_mouse_on = True

            place = None
            if (event.type == pygame.MOUSEBUTTONUP and
                    self.board.board[self.place] == TTTBoard.EMPTY and
                    self.rect.collidepoint(event.pos)):
                place = self.place
            return place

        def update(self):
            if self.board.board[self.place] == TTTBoard.EMPTY:
                if self.is_mouse_on:
                    self.image = self.images['placeable_tile']
                else:
                    self.image = self.images['empty_tile']
            elif self.board.board[self.place] == TTTBoard.PLAYER_X:
                self.image = self.images['cross_tile']
            else:
                self.image = self.images['circle_tile']


if __name__ == '__main__':
    main()
