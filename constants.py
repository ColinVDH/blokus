BOARD_SIZE = 20 #length of board edge
MAX_SIZE = 5 #max piece size
NUM_PLAYERS = 4
PROCESSES =   1 #number of subprocesses
SAMPLE_SIZE = 30 #avg samples per action




COLORS = [('White', '\u001b[37m'), ('Red', '\u001b[31m'), ('Green', '\u001b[32m'), ('Yellow', '\u001b[33m'), ('Blue', '\u001b[34m'), ('Bright White', '\u001b[30m'),
          ('Bright Red', '\u001b[31;1m'), ('Bright Green', '\u001b[32;1m'), ('Bright Yellow', '\u001b[33;1m'),
          ('Bright Blue', '\u001b[34;1m')]
RESET = "\u001b[0m"

STARTING_PLACES =  [(0, 0), (0, BOARD_SIZE - 1), (BOARD_SIZE - 1, BOARD_SIZE- 1), (BOARD_SIZE - 1, 0)][:NUM_PLAYERS]
STARTING_PLACES_0 = [(-1,-1), (-1, BOARD_SIZE), (BOARD_SIZE, BOARD_SIZE), (BOARD_SIZE, -1)][:NUM_PLAYERS]

