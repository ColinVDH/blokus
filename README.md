# Blokus
Authors: [Colin Vandenhof](github.com/ColinVDH/) 
©2020 under the [MIT license](www.opensource.org/licenses/mit-license.php)  

## Overview

Blokus is a popular board game generally played with 4 players on a 20x20 grid. Each player has a set of plastic pieces that correspond to all [polyominos](https://en.wikipedia.org/wiki/Polyomino) up to size 5. Each player begins at separate corners of the board, and takes turns placing their pieces in clockwise order. The placement rules are simple: the piece must be placed on an available section of the board, must share a corner with that player's previously placed pieces, but must not share any edges with them. Play continues until no players have any possible moves left. The winner is the player with the most occupied squares of the grid. 

See [here](/board.jpg) for an example of a completed game. Blue is the winner since they have the most occupied grid squares.


## Motivation

This game is deceptively simple. Although each player only has 21 physical pieces, there are, on average, 156 possible moves each turn and 59 turns in a game. A complete search of the game tree would therefore require considering ~2<sup>430</sup> game states.


## Players

Several players are implemented.   
- Human: provides a simple text-based interface for a human player to select piece and play it.
- RandomBot: selects an action uniformly at random.
- GreedyActionBot: plays according a heuristic. Picks whatever action immediately yields the highest number of possible subsequent actions. 
- MCTSBot: implements a version of [Monte Carlo Tree Search](https://en.wikipedia.org/wiki/Monte_Carlo_tree_search).
- HybridBot: begins by playing according to the greedy action heuristic, then switches over to MCTS at turn n.


## Running
Ensure that `numpy`, `progressbar`, and `keyboard` libraries are installed in your Python 3 environment. 

In `game.py`, change the `players` array to include whatever players you wish to include in the game.

Run `python game.py`


## Next Steps
It would be interesting to incorporate a deep RL bot. This could either be a standalone bot or an extension to the MCTS bot. It might use a neural network to evaluate game states (value network) and/or a network to choose actions (policy network).

