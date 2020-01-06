import numpy as np
from piece import Piece, on_board, all_pieces, adjacent
from constants import BOARD_SIZE, NUM_PLAYERS, MAX_SIZE, COLORS, STARTING_PLACES, STARTING_PLACES_0, RESET
import copy
import random

# Board state is given by 4 sets of pieces, one for each player.

# To generate moves (given board state), we iteratively build up from each open corner until max piece length reached, adding each play (Piece --> Oriented Piece) to the available moves.
# We can use "piece_to_canonical" to obtain canonical piece and check if we still have it.

# From a earlier board state to the next, we must check if any moves are added/taken away.
# Your move both adds and takes away. Opponent moves can only take away.
# We must take away a move if there are any collisions with a point in "available moves".

class Board:

    def __init__(self):
        self.piece_played = [{a : False for a in all_pieces} for _ in range(NUM_PLAYERS)]
        self.board = np.zeros((BOARD_SIZE,BOARD_SIZE))
        self.available_actions = [list(self.available_from_seed(ind, Piece([point,]))) for ind, point in enumerate(STARTING_PLACES)]
        self.pieces_played = [set([Piece([point,])]) for point in STARTING_PLACES_0] #needed for sim

    def __str__(self):
        output = ''
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                output += COLORS[int(self.board[i, j])][1] + '\u25a0 ' + RESET
            output += "\n"
        return output



    # action is specified as a player index, and a piece
    # remember to update available actions for all players
    def execute_action(self, index, piece, sim=False):
        for (x, y) in piece: #board
            self.board[x, y] = (index + 1)
        self.piece_played[index][piece.canonical()] = True
        self.pieces_played[index].add(piece)

        if sim:
            return

        #THIS PLAYER UPDATE
        # remove all orientations of same piece (get canonical. canonical -> orientations. remove all matches)
        # remove all orientation that collide with given piece and adjacencies (CACHE point -> orientations. remove all matches)
        new_avail = set()
        for p in self.available_actions[index]:
            if p.canonical() != piece.canonical() and not Piece(piece._points + tuple(piece.adjacencies())).collides(p):
                new_avail.add(p)


        # add all orientations from new seeds, making sure not already played
        for adj in piece.corner_adjacencies():
            if self.valid(index, adj):
                available = self.available_from_seed(index, Piece([adj,]))
                for a in available:
                    if not self.piece_played[index][a.canonical()]:
                        new_avail.add(a)

        self.available_actions[index] = list(new_avail)

        #OTHER PLAYER UPDATE
        #remove all orientations that collide with given piece
        for other_ind in range(NUM_PLAYERS):
            if other_ind == index:
                continue
            new_avail = set()
            for p in self.available_actions[other_ind]:
                if not piece.collides(p):
                    new_avail.add(p)

            self.available_actions[other_ind] = list(new_avail)


    def valid(self, ind, point):
        x,y = point
        if not on_board((x, y)):
            return False
        if self.board[x,y] != 0:
            return False
        for adj in adjacent(point):
            if on_board(adj) and self.board[adj] == (ind + 1):
                return False
        return True

    def available_from_seed(self, ind, seed):
        all = set([seed])
        size = 1
        current_gen = set([seed])
        next_gen = set()
        while len(current_gen) > 0 and size < MAX_SIZE:
            for poly in current_gen:
                for (x, y) in poly.adjacencies():
                    if self.valid(ind, (x, y)):
                        new_poly = Piece(poly._points + ((x,y),))
                        next_gen.add(new_poly)
            all.update(next_gen)
            current_gen = next_gen
            next_gen = set()
            size += 1
        return all

    #cheap procedure to randomly get an available action
    def get_available_action(self, ind):
        pieces = copy.deepcopy(self.pieces_played[ind])
        while pieces:

            p = random.choice(list(pieces))
            pieces.remove(p)
            for adj in p.corner_adjacencies():
                if self.valid(ind, adj):
                    available = self.available_from_seed(ind, Piece([adj,]))
                    while available:

                        action = random.choice(list(available))
                        available.remove(action)
                        if not self.piece_played[ind][action.canonical()]:
                            return action
        return None

    #returns all available actions for a particular player (given by index).
    def get_available_actions(self, ind):
        return self.available_actions[ind]


    def get_scores(self):
        return [np.sum(self.board == ind + 1) for ind in range(NUM_PLAYERS)]


if __name__ == '__main__':
    board = Board()



