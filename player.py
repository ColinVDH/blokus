from constants import STARTING_PLACES

class Player:
    def __init__(self, index, is_human=False):
        self.index = index
        self.is_human = is_human
        self.starting_place = STARTING_PLACES[index]

    def get_move(self, board):
        pass