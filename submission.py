import logic
import random
from AbstractPlayers import *
import time

MAX_PLAYER = 1
MIN_PLAYER = 2
CHANCE_PLAYER = 3
P2 = 0.9
P4 = 0.1
MUL_TIME = 20

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
        # weight = 0.8  ## TODO: Change the weight

        # save the heuristics values for the next step
        optional_moves_score = {}
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                optional_moves_score[move] = self.helper.heuristics(new_board, score)

        # choose the move of the max heuristic value
        return max(optional_moves_score, key=optional_moves_score.get)

    # TODO: add here helper functions in class, if needed


class HELPER:
    def __init__(self):
        pass

    def RB_MINIMAX(self, board, agent: int, D: int, value: int = 2):
        # check if we reach a goal
        goal, score, empty_squares = self.isGoal(board, agent)
        if goal or D == 0:
            return self.heuristics(board, score)
        # MAX player
        if agent == MAX_PLAYER:
            # init max
            currMax = float('-inf')
            # loop over the children to find the max
            for move in Move:
                new_board, done, score = commands[move](board)
                if done:
                    currMax = max(currMax, self.RB_MINIMAX(new_board, MIN_PLAYER, D - 1))
            return currMax
        else:  # MIN player
            # init the min
            currMin = float('inf')
            # save the place of the empty cells
            cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if
                     item == 0]
            new_board = board.copy()
            # loop over the empty places
            for (i, j) in cells:
                new_board[i][j] = value
                currMin = min(currMin, self.RB_MINIMAX(new_board, MAX_PLAYER, D - 1, value))
                new_board[i][j] = 0
            return currMin

    def AlphaBeta(self, board, agent: int, D: int, Alpha, Beta, value: int = 2):
        # check if we reach a goal
        goal, score, empty_squares = self.isGoal(board, agent)
        if goal or D == 0:
            return self.heuristics(board, score)
        # MAX player
        if agent == MAX_PLAYER:
            # init max
            currMax = float('-inf')
            # loop over the children to find the max
            for move in Move:
                new_board, done, score = commands[move](board)
                if done:
                    currMax = max(currMax, self.AlphaBeta(new_board, MIN_PLAYER, D - 1, Alpha, Beta))
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
            new_board = board.copy()
            # loop over the empty places
            for (i, j) in cells:
                new_board[i][j] = value
                currMin = min(currMin, self.AlphaBeta(new_board, MAX_PLAYER, D - 1, Alpha, Beta, value))
                new_board[i][j] = 0
                Beta = min(currMin, Beta)
                if currMin <= Alpha:
                    return float("-inf")
            return currMin

    def RB_Expectimax(self, board, agent: int, D: int, value: int = 2):
        # check if we reach a goal
        goal, score, empty_squares = self.isGoal(board, agent)
        if goal or D == 0:
            return self.heuristics(board, score)
        if agent == CHANCE_PLAYER:
            return (self.RB_Expectimax(board, MIN_PLAYER, D - 1, 2) * P2) + (self.RB_Expectimax(board, MIN_PLAYER, D - 1, 4) * P4)
        if agent == MAX_PLAYER:
            # init max
            currMax = float('-inf')
            # loop over the children to find the max
            for move in Move:
                new_board, done, score = commands[move](board)
                if done:
                    currMax = max(currMax, self.RB_Expectimax(new_board, CHANCE_PLAYER, D - 1, value))
            return currMax
        else:  # MIN player
            # init the min
            currMin = float('inf')
            # save the place of the empty cells
            cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if
                     item == 0]
            new_board = board.copy()
            # loop over the empty places
            for (i, j) in cells:
                new_board[i][j] = value
                currMin = min(currMin, self.RB_Expectimax(new_board, MAX_PLAYER, D - 1, value))
                new_board[i][j] = 0
            return currMin

    def countEmptySquares(self, board):
        counter = 0
        for i in range(0, len(board)):
            for j in range(0, len(board)):
                if board[i][j] == 0:
                    counter += 1
        return counter

    def countArroundSquares(self, board):
        counter = 0
        for i in range(0, len(board)):
            for j in range(0, len(board)):
                if (i == 0 or j == 0 or i == len(board) - 1 or j == len(board) - 1) and board[i][j] > 0:
                    counter += 1
        return counter

    def findMaxVal(self, board):
        currMax = 0
        for i in range(0, len(board)):
            for j in range(0, len(board)):
                if board[i][j] > currMax:
                    currMax = board[i][j]
        return currMax

    def countEqualNear(self, board):
        counter = 0
        for i in range(0, len(board)):
            for j in range(0, len(board)):
                if i - 1 >= 0 and board[i - 1][j] == board[i][j]:
                    counter += 1
                if j - 1 >= 0 and board[i][j - 1] == board[i][j]:
                    counter += 1
                if i + 1 < len(board) and board[i + 1][j] == board[i][j]:
                    counter += 1
                if j + 1 < len(board) and board[i][j + 1] == board[i][j]:
                    counter += 1
        return counter

    def isMonotonic(self, board):
        numMonotonic = 0
        mono = True
        for i in range(0, len(board)):
            rise = True
            for j in range(0, len(board) - 1):
                if board[i][j] > board[i][j + 1] and rise:
                    continue
                elif board[i][j] > board[i][j + 1] and not rise:
                    mono = False
                    break
                elif j == 0 and board[i][j] < board[i][j + 1]:
                    rise = False
                elif board[i][j] < board[i][j + 1] and not rise:
                    continue
            if mono:
                numMonotonic += 1
            mono = True
        return numMonotonic

    def heuristics(self, board, score):
        empty_squares = self.countEmptySquares(board)
        around_squares = self.countArroundSquares(board)
        max_val = self.findMaxVal(board)
        near = self.countEqualNear(board)
        monotonic = self.isMonotonic(board)
        return score * 50 + 150 * (empty_squares + around_squares) + 50 * max_val + 200 * near + 200 * monotonic

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

    def get_move(self, board, time_limit) -> Move:
        # init depth
        D = 1
        started = time.time()
        move = self.play(board, D, time_limit)
        itr_time = time.time() - started
        curr_time = itr_time
        next_itr_time = itr_time * MUL_TIME
        while next_itr_time + curr_time < time_limit:
            D += 1
            started_time = time.time()
            curr_move = self.play(board, D, next_itr_time)
            if curr_move is not None:
                move = curr_move
            itr_time = time.time() - started_time
            next_itr_time = itr_time * MUL_TIME
            curr_time = time.time() - started
        return move

    def play(self, board, D, allowed_time):
        started_time = time.time()
        currMax = float('-inf')
        bestMove = None
        # loop over the children to find the max
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                v = self.helper_fun.RB_MINIMAX(new_board, MIN_PLAYER, D - 1)
                if currMax < v:
                    currMax = v
                    bestMove = move
            if time.time() - started_time > allowed_time:
                return None
        return bestMove


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

    def get_indices(self, board, value, time_limit) -> (int, int):
        # init depth
        D = 1
        started = time.time()
        indicate = self.play(board, D, time_limit)
        itr_time = time.time() - started
        curr_time = itr_time
        next_itr_time = itr_time * MUL_TIME
        while next_itr_time + curr_time < time_limit:
            D += 1
            started_time = time.time()
            curr_indicate = self.play(board, D, next_itr_time)
            if curr_indicate is not None:
                indicate = curr_indicate
            itr_time = time.time() - started_time
            next_itr_time = itr_time * MUL_TIME
            curr_time = time.time() - started
        return indicate

    def play(self, board, D, allowed_time, value=2):
        started_time = time.time()
        currMin = float('inf')
        bestIndicate = None
        # save the place of the empty cells
        cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if
                 item == 0]
        new_board = board.copy()
        # loop over the empty places
        for (i, j) in cells:

            new_board[i][j] = value
            v = self.helper_fun.RB_MINIMAX(new_board, MAX_PLAYER, D - 1, value)
            new_board[i][j] = 0
            if currMin > v:
                currMin = v
                bestIndicate = (i, j)
            if time.time() - started_time > allowed_time:
                return None
        return bestIndicate


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
        # init depth
        D = 1
        started = time.time()
        move = self.play(board, D, time_limit)
        itr_time = time.time() - started
        curr_time = itr_time
        next_itr_time = itr_time * MUL_TIME
        while next_itr_time + curr_time < time_limit:
            D += 1
            started_time = time.time()
            curr_move = self.play(board, D, next_itr_time)
            if curr_move is not None:
                move = curr_move
            itr_time = time.time() - started_time
            next_itr_time = itr_time * MUL_TIME
            curr_time = time.time() - started
        return move

    def play(self, board, D, allowed_time=None):
        started_time = time.time()
        currMax = float('-inf')
        Alpha = float("-inf")
        Beta = float("inf")
        bestMove = None
        # loop over the children to find the max
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                v = self.helper_fun.AlphaBeta(new_board, MIN_PLAYER, D - 1, Alpha, Beta)
                if v > currMax:
                    currMax = v
                    bestMove = move
                    Alpha = v
            if time.time() - started_time > allowed_time:
                return None
        return bestMove


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
        # init depth
        D = 1
        started = time.time()
        move = self.play(board, D, time_limit)
        itr_time = time.time() - started
        curr_time = itr_time
        next_itr_time = itr_time * MUL_TIME
        while next_itr_time + curr_time < time_limit:
            D += 1
            started_time = time.time()
            curr_move = self.play(board,next_itr_time,  D)
            if curr_move is not None:
                move = curr_move
            itr_time = time.time() - started_time
            next_itr_time = itr_time * MUL_TIME
            curr_time = time.time() - started
        return move

    def play(self, board, allowed_time, D):
        started_time = time.time()
        currMax = float('-inf')
        bestMove = None
        # loop over the children to find the max
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                v = self.helper_fun.RB_Expectimax(new_board, CHANCE_PLAYER, D - 1)
                if currMax < v:
                    currMax = v
                    bestMove = move
            if time.time() - started_time > allowed_time:
                return None
        return bestMove


class ExpectimaxIndexPlayer(AbstractIndexPlayer):
    """Expectimax Index Player
    implement get_indices function according to Expectimax algorithm, the value is number between {2,4}.
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractIndexPlayer.__init__(self)
        self.helper_fun = HELPER()

    def get_indices(self, board, value, time_limit) -> (int, int):
        # init depth
        D = 1
        started = time.time()
        indicate = self.play(board, D, time_limit)
        itr_time = time.time() - started
        curr_time = itr_time
        next_itr_time = itr_time * MUL_TIME
        while next_itr_time + curr_time < time_limit:
            D += 1
            started_time = time.time()
            curr_indicate = self.play(board, D, next_itr_time)
            if curr_indicate is not None:
                indicate = curr_indicate
            itr_time = time.time() - started_time
            next_itr_time = itr_time * MUL_TIME
            curr_time = time.time() - started
        return indicate

    def play(self, board, D, allowed_time):
        started_time = time.time()
        currMin = float('inf')
        bestIndicate = None
        # save the place of the empty cells
        cells = [(row_idx, col_idx) for row_idx, row in enumerate(board) for col_idx, item in enumerate(row) if
                 item == 0]
        new_board = board.copy()
        # loop over the empty places
        for (i, j) in cells:

            new_board[i][j] = 2
            v1 = self.helper_fun.RB_Expectimax(new_board, MAX_PLAYER, D - 1)
            new_board[i][j] = 4
            v2 = self.helper_fun.RB_Expectimax(new_board, MAX_PLAYER, D - 1)
            new_board[i][j] = 0
            v = P2 * v1 + P4 * v2
            if currMin > v:
                currMin = v
                bestIndicate = (i, j)
            curr_time = time.time() - started_time
            if curr_time > allowed_time:
                return None
        return bestIndicate


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
