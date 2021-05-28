import logic
import random
from AbstractPlayers import *
import time

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
        # TODO: add here if needed

    def get_move(self, board, time_limit) -> Move:
        weight = 0.9  ## TODO: Change the weight

        # save the heuristics values for the next step
        optional_moves_score = {}
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                optional_moves_score[move] = self.heuristics(new_board, score, weight)

        # choose the max heuristics value
        return max(optional_moves_score, key=optional_moves_score.get)

    # TODO: add here helper functions in class, if needed
    def countEmptySquares(self, board):
        counter = 0
        for i in len(board):
            for j in len(board):
                if board[i][j] == 0:
                    counter += 1
        return counter

    def heuristics(self, board, score, weight):
        empty_squares = self.countEmptySquares(board)
        ## TODO: edit to return utility if its a goal
        return weight * score + empty_squares * (1 - weight)


# part B
class MiniMaxMovePlayer(AbstractMovePlayer):
    """MiniMax Move Player,
    implement get_move function according to MiniMax algorithm
    (you can add helper functions as you want).
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        # TODO: add here if needed
        self.index = MiniMaxIndexPlayer()
        self.h = ImprovedGreedyMovePlayer()

    def get_move(self, board, time_limit) -> Move:
        # save init time
        init_time = time.time()

        # if the time limit ended
        if time_limit < 0:
            return -1

        # check if we done
        goal, score = self.isGoal(board)
        if goal or time_limit < 0.04:
            return self.h.heuristics(board, score, 0.5)

        # init max
        currMax = float('-inf')

        # loop over the children to fine the max
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                v = self.index.get_indices(board, 2, time_limit - (time.time() - init_time))
                currMax = max(v, currMax)
        return currMax

    # TODO: add here helper functions in class, if needed
    def isGoal(self, board):
        """isGoal get the board and check if its a goal,
            return true if its a goal, and the score of the board
            """
        goal = True
        for move in Move:
            new_board, done, score = commands[move](board)
            if done:
                goal = False
        # find the board score, loop over the non zero, two squares
        board_score = 0
        for i in len(board):
            for j in len(board):
                if board[i][j] != 0 and board[i][j] != 2:
                    board_score += board[i][j]
        return goal, board_score


class MiniMaxIndexPlayer(AbstractIndexPlayer):
    """MiniMax Index Player,
    this player is the opponent of the move player and need to return the indices on the board where to put 2.
    the goal of the player is to reduce move player score.
    implement get_indices function according to MiniMax algorithm, the value in minimax player value is only 2.
    (you can add helper functions as you want).
    """

    def __init__(self):
        AbstractIndexPlayer.__init__(self)
        # TODO: add here if needed
        self.move = MiniMaxMovePlayer()
        self.h = ImprovedGreedyMovePlayer()

    def get_indices(self, board, value, time_limit) -> (int, int):
        # check the limit time
        if time_limit <= 0:
            return -1, -1

        # save the time
        init_time = time.time()

        # save the place of the empty cells
        cells = [i for i, x in enumerate(board) if x == 0]

        # check if we done
        if len(cells) == 0 or time_limit - (time.time() - init_time) < 0.04:
            return self.h.heuristics(board, score, 0.5)

        # init the min
        currMin = float('inf')

        # generate the children
        children = []
        for cell in cells:
            copy = list(board)
            copy[cell] = value
            children.append(copy)

        # loop over the children
        for child in children:
            move =  MiniMaxMovePlayer()
            v = move.get_move(board, time_limit - (time.time() - init_time))
            currMin = min(currMin, v)
        return currMin

    # TODO: add here helper functions in class, if needed


# part C
class ABMovePlayer(AbstractMovePlayer):
    """Alpha Beta Move Player,
    implement get_move function according to Alpha Beta MiniMax algorithm
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        # TODO: add here if needed

    def get_move(self, board, time_limit) -> Move:
        # TODO: erase the following line and implement this function.
        raise NotImplementedError

    # TODO: add here helper functions in class, if needed


# part D
class ExpectimaxMovePlayer(AbstractMovePlayer):
    """Expectimax Move Player,
    implement get_move function according to Expectimax algorithm.
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractMovePlayer.__init__(self)
        # TODO: add here if needed

    def get_move(self, board, time_limit) -> Move:
        # TODO: erase the following line and implement this function.
        raise NotImplementedError

    # TODO: add here helper functions in class, if needed


class ExpectimaxIndexPlayer(AbstractIndexPlayer):
    """Expectimax Index Player
    implement get_indices function according to Expectimax algorithm, the value is number between {2,4}.
    (you can add helper functions as you want)
    """

    def __init__(self):
        AbstractIndexPlayer.__init__(self)
        # TODO: add here if needed

    def get_indices(self, board, value, time_limit) -> (int, int):
        # TODO: erase the following line and implement this function.
        raise NotImplementedError

    # TODO: add here helper functions in class, if needed


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
