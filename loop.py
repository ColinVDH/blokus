from constants import NUM_PLAYERS


def game_loop(board, players, visualize=False):
    game_over = False
    while not game_over:
        game_over = True
        for index in range(NUM_PLAYERS):
            if board.get_available_actions(index):
                game_over = False
                action = players[index].get_move(board)
                board.execute_action(index, action)
                if not players[index].is_human and visualize:
                    print('\n'*100)
                    print(board)
    return board.get_scores(), stats



def sim_loop(board, depth=None):
    game_over = False
    d = 0
    while not game_over:
        game_over = True
        for index in range(NUM_PLAYERS):
            a = board.get_available_action(index)
            if a:
                game_over = False
                board.execute_action(index, a, sim=True)
        d += 1
        if depth and d == depth:
            break
    return board.get_scores()



if __name__ == "__main__":
    pass
