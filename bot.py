from player import Player
from copy import deepcopy
import numpy as np
import random
from constants import NUM_PLAYERS, PROCESSES, SAMPLE_SIZE
from multiprocessing import Pool
from loop import sim_loop
import time
import math
import progressbar

#HybridBot begins by using the greedy-action heuristic, then switches over to MCTS at some predefined turn (threshold)
class HybridBot(Player):
    def __init__(self, index, threshold=6, **kwargs):
        super().__init__(index)
        self.mcts = MCTSBot(index, **kwargs)
        self.greedy = GreedyActionBot(index, **kwargs)
        self.turns = 0
        self.threshold = threshold

    def get_move(self, board):
        self.turns += 1
        if self.turns <= self.threshold:
            return self.greedy.get_move(board)
        else:
            return self.mcts.get_move(board)

#Random plays actions uniformly at random
class RandomBot(Player):
    def __init__(self, index):
        super().__init__(index)

    def get_move(self, board):
        actions = board.get_available_actions(self.index)
        return random.sample(actions, 1)[0]
#

def softmax_selection(actions):
    values = [len(a) for a in actions]
    probs = np.exp(values)/sum(np.exp(values))
    i = np.random.choice(len(values), p=probs)
    return i


class SoftmaxSizeBot(Player):
    def __init__(self, index):
        super().__init__(index)

    def get_move(self, board):
        actions = list(board.get_available_actions(self.index))
        i = softmax_selection(actions)
        return actions[i]


#GreedyActionBot scores each action according to what immediately yields the highest number of possible subsequent actions after being taken.
class GreedyActionBot(Player):
    def __init__(self, index, budget=None, time=None):
        super().__init__(index)
        self.budget = budget
        self.time = time


    def get_move(self, board):
        actions = list(board.get_available_actions(self.index))

        values = np.zeros(len(actions))
        tried = np.zeros(len(actions))

        start = time.time()
        b = 0
        def loop():
            nonlocal b, start
            if self.budget:
                while b < self.budget:
                    b += 1
                    yield
            elif self.time:
                while time.time() - start < self.time:
                    yield
            else:
                while True:
                    yield


        for _ in progressbar.progressbar(loop()):

            indices = np.where(tried == 0)[0]
            if indices.size == 0:
                break

            action_subset = [actions[i] for i in indices]
            index = softmax_selection(action_subset)
            i = indices[index]
            tried[i] = 1

            b = deepcopy(board)
            b.execute_action(self.index, actions[i])
            values[i] = (len(b.get_available_actions(self.index)))

        i = np.argmax(values)
        return actions[i]


class Node:
    def __init__(self, action, board, index):
        self.visits = 0
        self.index = index
        self.wins = 0
        self.action = action
        self.board = board
        self.children = []


# MCTSBot performs Monte Carlo Tree Search. There are 4 steps.
# (1 - 2) Selection and expansion:
# - At a given node in the tree, compute proportion of children that have been previously selected (f_sel).
# - If random() < f_sel, select one of these children according to upper-confidence bound (UCB). Repeat.
# - Else, expand one of the child nodes that has never been selected before according to softmax on the piece size (i.e. action that plays a larger pieces more likely to be considered). Continue to next step.
# (3) Simulation:
# - For the current node, perform a simulation of remaining game using a random policy for all players.
# - Record if it was a win (1), tie (0.5) or loss (0).
# (4) Backpropagation:
# - For all nodes from the current node back to the root, update the visit and win statistics.
# - Note that wins are only incremented at nodes that correspond to the winning players.
class MCTSBot(Player):

    def __init__(self, index, depth=None, budget=None, time=None, adaptive_budget=False):
        super().__init__(index)
        self.budget = budget
        self.depth = depth
        self.root = None
        self.time = time
        self.adaptive_budget = adaptive_budget


    def selection_index(self, parent, children):

        values = np.zeros(len(children))
        ind = np.array([1 if c == None else 0 for c in children])
        hidden_best = np.sum(ind) / ind.size
        if np.random.random() < hidden_best and np.sum(ind) != 0:

            indices = np.where(ind == 1)[0]
            action_subset = [parent.board.get_available_actions((parent.index + 1) % NUM_PLAYERS)[i] for i in indices]
            index = self.expansion_index(action_subset)
            return indices[index]

        for i, c in enumerate(children):
            if c != None:
                values[i] = c.wins/c.visits + math.sqrt(2) * math.sqrt(math.log(parent.visits) / c.visits)

        i = np.argmax(values)
        return i

    def expansion_index(self, actions):
        return softmax_selection(actions)

    def expanded(self, root):
        stats = [0 for _ in range(100)]
        q = [(0, root)]
        while len(q) != 0:
            depth, node = q.pop()
            stats[depth] += 1
            for c in node.children:
                if c is not None:
                    q.append((depth + 1, c))
        print(stats)

    def mcts(self, board):
        self.root = Node(None, board, (self.index - 1) % NUM_PLAYERS)

        start = time.time()
        b = 0

        def loop():
            nonlocal b, start, board
            if self.budget:
                while b < self.budget:
                    b += 1
                    yield
            elif self.time:
                while time.time() - start < self.time:
                    yield
            else:
                while True:
                    yield

        for _ in progressbar.progressbar(loop()):

            #selection
            l = []
            curr = self.root
            l.append(curr)
            early_expand = None

            while curr.children:
                ind = self.selection_index(curr, curr.children)

                if curr.children[ind] != None:
                    curr = curr.children[ind]
                    l.append(curr)
                else:
                    early_expand = ind
                    break

            i = (curr.index + 1) % NUM_PLAYERS
            actions = curr.board.get_available_actions(i)
            child_b = deepcopy(curr.board)


            if early_expand != None:
                action_i = early_expand
            elif actions:
                curr.children = [None for _ in range(len(actions))]
                action_i = self.expansion_index(actions)

            if actions: #execute action if needed, update children
                child_b.execute_action(i, actions[action_i])
                curr.children[action_i] = Node(actions[action_i], child_b, i)
                curr = curr.children[action_i]
                l.append(curr)
                scores = sim_loop(deepcopy(curr.board), depth=self.depth)

            elif not all(not child_b.get_available_actions(i) for i in range(NUM_PLAYERS)): #no actions but game not over
                curr.children = [Node(None, child_b, i)]
                curr = curr.children[0]
                l.append(curr)
                scores = sim_loop(deepcopy(curr.board), depth=self.depth)

            else: #game over
                scores = curr.board.get_scores()

            winners = np.flatnonzero(scores == np.max(scores))
            if winners.size == 1:
                val = 1
            else:
                val = 0.5

            for node in l:
                if node.index in winners:
                    node.wins += val
                node.visits += 1
        self.expanded(self.root)
        return self.root.children


    #Parallelization is possible by performing MCTS on N copies of the tree, and then combining statistics at the end.
    def get_move(self, board):
        actions = board.get_available_actions(self.index)
        if self.adaptive_budget:
            self.budget = max(SAMPLE_SIZE * len(actions) / PROCESSES, 1000 / PROCESSES)

        with Pool(processes=PROCESSES) as pool:
            boards = [deepcopy(board) for _ in range(PROCESSES)]
            wins, visits, children = None, None, None
            for children in pool.imap_unordered(self.mcts, boards):
                if wins is None:
                    wins = np.array([c.wins if c != None else 0 for c in children], dtype=float)
                    visits = np.array([c.visits if c != None else 0 for c in children], dtype=float)
                else:
                    wins += np.array([c.wins if c != None else 0 for c in children], dtype=float)
                    visits += np.array([c.visits if c != None else 0 for c in children], dtype=float)

        print(['{}/{}'.format(w,v) for w, v in zip(wins, visits)])
        indices = np.flatnonzero(visits == np.max(visits))
        i = indices[np.argmax(wins[indices])]
        print('action:', i)
        return actions[i]




