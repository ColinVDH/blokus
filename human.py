from constants import COLORS, RESET, BOARD_SIZE, STARTING_PLACES
from piece import piece_to_name, Piece, on_board
from board import Board
import keyboard
import numpy as np
from player import Player



class Human(Player):
    def __init__(self, index):
        super().__init__(index, is_human=True)


    def print_screen(self, board, piece, text_list):
        print('\n'*100)

        board_arr = np.array(board.board)
        if piece:
            for p in piece:
                if on_board(p):
                    board_arr[p] = (5)

        output = ''
        for i in range(len(board_arr)):
            for j in range(len(board_arr[i])):
                output += COLORS[int(board_arr[i, j])][1] + '\u25a0 '+ RESET
            output += "\n"
        print(output)

        for t in text_list:
            print(t)


    def get_move(self, board):

        pieces = [p for p in board.piece_played[self.index].keys() if not board.piece_played[self.index][p]]
        string = ""
        for i, p in enumerate(pieces):
            string += '{} - {}. '.format(i+1, piece_to_name[p])

        basic_instructions = ['Human player ({})'.format(COLORS[self.index + 1][0]),
                        "------------------",
                        '',
                        "Select piece with number and enter. Move with WASD. Rotate with R. Flip with F. Press Enter to confirm.",
                        '',
                        string]

        piece = None

        def rotate(x):
            nonlocal piece
            if piece:
                shifted = piece.min()
                piece = Piece((y, -x) for x, y in piece.translate_origin()).translate_origin()
                piece = piece.translated(*shifted)
                self.print_screen(board, piece, basic_instructions)

        def flip(x):
            nonlocal piece
            if piece:
                shifted = piece.min()
                piece = Piece((x, -y) for x, y in piece.translate_origin()).translate_origin()
                piece = piece.translated(*shifted)
                self.print_screen(board, piece, basic_instructions)

        def shift(x):
            nonlocal piece
            if piece:
                if x.name == 'w':
                    piece = piece.translated(-1, 0)
                elif x.name == 's':
                    piece = piece.translated(1, 0)
                elif x.name == 'd':
                    piece = piece.translated(0, 1)
                elif x.name == 'a':
                    piece = piece.translated(0, -1)
                self.print_screen(board, piece, basic_instructions)


        keyboard.on_press_key('r', rotate)
        keyboard.on_press_key('f', flip)
        keyboard.on_press_key('w', shift)
        keyboard.on_press_key('s', shift)
        keyboard.on_press_key('a', shift)
        keyboard.on_press_key('d', shift)

        while True:
            self.print_screen(board, piece, basic_instructions)

            inp = input()

            if inp != '':
                if inp.isdigit() and int(inp) - 1 < len(pieces):
                    piece = pieces[int(inp) - 1]
                    maxp = piece.max()
                    minp = piece.min()
                    trans = []
                    for i in range(2):
                        if self.starting_place[i] == BOARD_SIZE - 1:
                            trans.append(BOARD_SIZE - 1 - maxp[i])
                        else:
                            trans.append(0 - minp[i])
                    piece = piece.translated(*trans)



            elif piece == None:
                instructions = ["No piece selected."]
                self.print_screen(board, piece, instructions)
                input()


            elif piece not in board.get_available_actions(self.index):
                instructions = ["Not a valid action."]
                self.print_screen(board, piece, instructions)
                input()

            elif inp == '':
                break

        keyboard.unhook_all()
        return piece

if __name__ == '__main__':
    human = Human(3)
    board = Board()
    human.get_move(board)
