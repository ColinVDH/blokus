from human import Human
from loop import game_loop
from bot import RandomBot, MCTSBot, GreedyActionBot, HybridBot
from board import Board
import numpy as np


def main():
    board = Board()
    players = [Human(0), RandomBot(1), GreedyActionBot(2, time=120), MCTSBot(3, adaptive_budget=True)]
    scores = game_loop(board, players, visualize=True)
    print(np.argmax(scores) + 1, 'wins!')
    return scores


if __name__ == "__main__":
    main()




