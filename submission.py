import logic
import random
from AbstractPlayers import *
import time
MAX_PLAYER = 1
MIN_PLAYER = 2
CHANCE_PLAYER = 3
P2 = 0.9
P4 = 0.1

# commands to use for move players. dictionary : Move(enum) -> function(board),
# all the functions {up,down,left,right) receive board as parameter and return tuple of (new_board, done, score).
# new_board is according to the step taken, done is true if the step is legal, score is the sum of all numbers that
# combined in this step.
# (you can see GreedyMovePlayer implementation for example)
commands = {Move.UP: logic.up, Move.DOWN: logic.down,
            Move.LEFT: logic.left, Move.RIGHT: logic.right}


# generate value between {2,4} with probability p for 4
def gen_value(p=PROBABILITY):
    return logic.gen_two_or_four(p)


class GreedyMovePlayer(AbstractMovePlayer):
    """Greedy move player provided to you (no need to change),
    the player receives time limit for a single step and the board as parameter and return the next move that gives
    the best score by looking one step ahead.
    """

    def get_move(self, board, time_limit) -> Move:
        optional_moves_score = {}
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                optional_moves_score[move] = score

        return max(optional_moves_score, key=optional_moves_score.get)


class RandomIndexPlayer(AbstractIndexPlayer):
    """Random index player provided to you (no need to change),
    the player receives time limit for a single step and the board as parameter and return the next indices to
    put 2 randomly.
    """

    def get_indices(self, board, value, time_limit) -> (int, int):
        a = random.randint(0, len(board) - 1)
        b = random.randint(0, len(board) - 1)
        while board[a][b] != 0:
            a = random.randint(0, len(board) - 1)
            b = random.randint(0, len(board) - 1)
        return a, b


# part A
class ImprovedGreedyMovePlayer(AbstractMovePlayer):
    """Improved greedy Move Player,
    implement get_move function with greedy move that looks only one step ahead with heuristic.
    (you can add helper functions as you want).
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        self.helper = HELPER()

    def get_move(self, board, time_limit) -> Move:
        weight = 0.8  ## TODO: Change the weight

        # save the heuristics values for the next step
        optional_moves_score = {}
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                optional_moves_score[move] = self.heuristics(new_board, score, weight)

        # choose the max heuristics value
        return max(optional_moves_score, key=optional_moves_score.get)

    # TODO: add here helper functions in class, if needed
    def heuristics(self, board, score, weight):
        empty_squares = self.helper.countEmptySquares(board)
        return weight * score + empty_squares * (1 - weight)


class HELPER:
    def __init__(self):
        pass

    def RB_MINIMAX(self, board, agent: int, D: int, value: int = 2):
        # check if we reach a goal
        goal, score, empty_squares = self.isGoal(board, agent)
        if goal or D == 0:
            return self.heuristics(score, goal, empty_squares)
        # MAX player
        if agent == MAX_PLAYER:
            # init max
            currMax = float('-inf')
            # loop over the children to find the max
            for move in Move:
                new_board, done, score = commands[move](board)
                if done:
                    v = self.RB_MINIMAX(new_board, MIN_PLAYER, D - 1)
                    currMax = max(currMax, v)
            return currMax
        else:  # MIN player
            # init the min
            currMin = float('inf')
            # save the place of the empty cells
            cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if item == 0]
            # loop over the empty places
            for (i,j) in cells:
                new_board = list(board)
                new_board[i][j] = value
                v = self.RB_MINIMAX(new_board, MAX_PLAYER, D - 1, value)
                currMin = min(currMin, v)
            return currMin

    def AlphaBeta(self, board, agent: int, D: int, Alpha, Beta, value: int = 2):
        # check if we reach a goal
        goal, score, empty_squares = self.isGoal(board, agent)
        if goal or D == 0:
            return self.heuristics(score, goal, empty_squares)
        # MAX player
        if agent == MAX_PLAYER:
            # init max
            currMax = float('-inf')
            # loop over the children to find the max
            for move in Move:
                new_board, done, score = commands[move](board)
                if done:
                    v = self.AlphaBeta(new_board, MIN_PLAYER, D - 1, Alpha, Beta)
                    if currMax < v:
                        currMax = v
                        self.max_move = move
                    Alpha = max(Alpha, currMax)
                    if currMax >= Beta:
                        return float("inf")
            return currMax
        else:  # MIN player
            # init the min
            currMin = float('inf')
            # save the place of the empty cells
            cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if
                     item == 0]
            # loop over the empty places
            for (i, j) in cells:
                new_board = list(board)
                new_board[i][j] = value
                v = self.AlphaBeta(new_board, MAX_PLAYER, D - 1, Alpha, Beta)
                if currMin > v:
                    currMin = v
                    self.min_indicate = (i,j)
                Beta = min(currMin, Beta)
                if currMin <= Alpha:
                    return float("-inf")
            return currMin

    def RB_Expectimax(self, board, agent: int, D: int, value: int = 2):
        # check if we reach a goal
        goal, score, empty_squares = self.isGoal(board, agent)
        if goal or D == 0:
            return self.heuristics(score, goal, empty_squares)
        if agent == CHANCE_PLAYER:
            sum_chance = 0
            sum_chance += (self.RB_Expectimax(board, MIN_PLAYER, D-1) * P2) + (self.RB_Expectimax(board, MIN_PLAYER, D-1, 4) * P4)
            return sum_chance
        if agent == MAX_PLAYER:
            # init max
            currMax = float('-inf')
            # loop over the children to find the max
            for move in Move:
                new_board, done, score = commands[move](board)
                if done:
                    v = self.RB_Expectimax(new_board, CHANCE_PLAYER, D - 1, value)
                    if currMax < v:
                        currMax = v
            return currMax
        else:  # MIN player
            # init the min
            currMin = float('inf')
            # save the place of the empty cells
            cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if
                     item == 0]
            # loop over the empty places
            for (i, j) in cells:
                new_board = list(board)
                new_board[i][j] = value
                v = self.RB_Expectimax(new_board, MAX_PLAYER, D - 1, value)
                if currMin > v:
                    currMin = v
            return currMin

    def countEmptySquares(self, board):
        counter = 0
        for i in range(0, len(board)):
            for j in range(0, len(board)):
                if board[i][j] == 0:
                    counter += 1
        return counter

    def heuristics(self, score, goal, empty_squares, weight=0.8):
        if goal:
            return score
        return weight * score + empty_squares * (1 - weight)

    def isGoal(self, board, agent):
        goal = True
        emptyCells = self.countEmptySquares(board)
        if agent == MAX_PLAYER:
            for move in Move:
                new_board, done, score = commands[move](board)
                if done:
                    goal = False
                    break
        else:
            if emptyCells > 0:
                goal = False
        # find the board score, loop over the non zero, two squares
        board_score = 0
        for i in range(0, len(board)):
            for j in range(0, len(board)):
                if board[i][j] != 0 and board[i][j] != 2:
                    board_score += board[i][j]
        return goal, board_score, emptyCells


# part B
class MiniMaxMovePlayer(AbstractMovePlayer):
    """MiniMax Move Player,
    implement get_move function according to MiniMax algorithm
    (you can add helper functions as you want).
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        self.helper_fun = HELPER()
        self.BestMove = None

    def get_move(self, board, time_limit) -> Move:
        # save the time
        init_time = time.time()
        # init depth
        D = 1
        # init move
        move = None
        while time.time() - init_time <= time_limit:
            currmove = self.play(board, D)
            if time.time() - init_time <= time_limit:
                move = currmove
            D = D + 1
        if move is None:
            exit(7)
        return move

    def play(self, board, D):
        currMax = 0
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                v = self.helper_fun.RB_MINIMAX(new_board, MIN_PLAYER, D - 1)
                if currMax <= v:
                    currMax = v
                    self.BestMove = move
        return self.BestMove


class MiniMaxIndexPlayer(AbstractIndexPlayer):
    """MiniMax Index Player,
    this player is the opponent of the move player and need to return the indices on the board where to put 2.
    the goal of the player is to reduce move player score.
    implement get_indices function according to MiniMax algorithm, the value in minimax player value is only 2.
    (you can add helper functions as you want).
    """

    def __init__(self):
        AbstractIndexPlayer.__init__(self)
        self.helper_fun = HELPER()
        self.BestIndicate = None

    def get_indices(self, board, value, time_limit) -> (int, int):
        # save the time
        init_time = time.time()
        # init depth
        D = 1
        # init move
        inidcate = None
        while time.time() - init_time <= time_limit:
            curr_indicate = self.play(board, D)
            if time.time() - init_time <= time_limit:
                inidcate = curr_indicate
            D = D + 1
        if inidcate is None:
            exit(1)
        return inidcate

    def play(self, board, D, value=2):
        currMin = float('inf')
        # save the place of the empty cells
        cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if
                 item == 0]
        # loop over the empty places
        for (i, j) in cells:
            new_board = list(board)
            new_board[i][j] = value
            v = self.helper_fun.RB_MINIMAX(new_board, MAX_PLAYER, D - 1, value)
            if v < currMin:
                currMin = v
                self.BestIndicate = (i,j)
        return self.BestIndicate



# part C
class ABMovePlayer(AbstractMovePlayer):
    """Alpha Beta Move Player,
    implement get_move function according to Alpha Beta MiniMax algorithm
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        self.helper_fun = HELPER()

    def get_move(self, board, time_limit) -> Move:
        # save the time
        init_time = time.time()
        # init depth
        D = 1
        # init move
        move = None
        while time.time() - init_time <= time_limit:
            v = self.helper_fun.AlphaBeta(board, MAX_PLAYER, D, float("-inf"), float("inf"))
            if time.time() - init_time <= time_limit:
                move = self.helper_fun.max_move
            D = D + 1
        if move is None:
            exit(1)
        return move


# part D
class ExpectimaxMovePlayer(AbstractMovePlayer):
    """Expectimax Move Player,
    implement get_move function according to Expectimax algorithm.
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        self.helper_fun = HELPER()

    def get_move(self, board, time_limit) -> Move:
        # save the time
        init_time = time.time()
        # init depth
        D = 1
        # init move
        move = None
        while time.time() - init_time <= time_limit:
            v = self.helper_fun.RB_Expectimax(board, MAX_PLAYER, D)
            if time.time() - init_time <= time_limit:
                move = self.helper_fun.max_move
            D = D + 1
        if move is None:
            exit(1)
        return move


class ExpectimaxIndexPlayer(AbstractIndexPlayer):
    """Expectimax Index Player
    implement get_indices function according to Expectimax algorithm, the value is number between {2,4}.
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractIndexPlayer.__init__(self)
        self.helper_fun = HELPER()

    def get_indices(self, board, value, time_limit) -> (int, int):
        # save the time
        init_time = time.time()
        # init depth
        D = 1
        # init move
        inidcate = None
        while time.time() - init_time <= time_limit:
            v = self.helper_fun.RB_Expectimax(board, MIN_PLAYER, D)
            if time.time() - init_time <= time_limit:
                inidcate = self.helper_fun.min_indicate
            D = D + 1
        if inidcate is None:
            exit(1)
        return inidcate


# Tournament
class ContestMovePlayer(AbstractMovePlayer):
    """Contest Move Player,
    implement get_move function as you want to compete in the Tournament
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        # TODO: add here if needed

    def get_move(self, board, time_limit) -> Move:
        # TODO: erase the following line and implement this function.
        raise NotImplementedError

    # TODO: add here helper functions in class, if needed
