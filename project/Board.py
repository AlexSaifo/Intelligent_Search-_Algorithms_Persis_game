import numpy as np
import math
import random
from termcolor import colored
import copy


class Board:
    protected_cell = np.array([11, 22, 28, 39, 45, 56, 62, 73])
    protected_cell_2d = [
        (2, 8),
        (2, 10),
        (8, 2),
        (8, 16),
        (10, 2),
        (10, 16),
        (16, 8),
        (16, 10),
    ]
    distance_to_intersect = 34
    final_distance = 7
    min_evaluation =-100
    max_evaluation = 100
    W = [5, 1, 5, 1]
    range_len = (4 * W[0] + 4 * 84 * W[2]) - (-4 * W[1] - 4 * 84 * W[3])
    scale = (max_evaluation-min_evaluation) / range_len

    def __init__(self):
        self.player_pieces = np.array([[0, 0, 0, 0], [0, 0, 0, 0]])



    def __eq__(self, __value: object) -> bool:
        return np.array_equal(self.player_pieces, __value.player_pieces)



    def __ge__(self, __value: object) -> bool:
        """check if self >= __value"""
        # Assume x and y are your 2D arrays
        x = self.player_pieces
        y = __value.player_pieces

        # Define the two arrays
        eq = np.equal(x, y)
        ge = np.greater_equal(x, y)

        # Find the index of the first False value in eq
        index = np.argmax(np.logical_not(eq))

        # Get the corresponding element from ge
        corresponding_element = ge.flatten()[index]

        return corresponding_element



    def is_second_player(self, player):
        return player == 1



    def other_player(self, player):
        return (int)(player == 0)



    def is_finished(self):
        if np.all(self.player_pieces[0] == 84) or np.all(self.player_pieces[1] == 84):
            return True
        return False



    def get_index(self, player, dist):
        """_summary_

        Args:
            player (int): which player has this piece
            dist (int): the value of piece, how many steps this piece has moved

        Returns:
            i,j: the index in the 2d array, usually using for printing
        """
        x = dist
        i, j = -1, -1
        if x >= 17 and x <= 67:
            # detrmine quarter
            if x // 17 == 1:
                if x <= 24:
                    i, j = 10, 11 + x - 17
                elif x == 25:
                    i, j = 9, 18
                else:
                    i, j = 8, 33 - x + 11

            if x // 17 == 2:
                if x <= 41:
                    i, j = 41 - x, 10
                elif x == 42:
                    i, j = 0, 9
                else:
                    i, j = x - 43, 8

            if x // 17 == 3:
                if x <= 58:
                    i, j = 8, 58 - x
                elif x == 59:
                    i, j = 9, 0
                else:
                    i, j = 10, x - 60

        elif 1 <= x <= 8:
            i, j = 10 + x, 9

        elif 9 <= x <= 16:
            i, j = 18 - x + 9, 10

        elif 68 <= x <= 75:
            i, j = 11 + x - 68, 8

        elif 76 <= x <= 83:
            i, j = 18 - x + 76, 9

        if i == -1 or j == -1:
            return i, j

        if self.is_second_player(player):
            i, j = 18 - i, 18 - j

        return i, j




    def print(self):
        """
        print the Board, Like:
            the empty cell: ⬜
            the protect cell: <⬜>
            the piece of the first player: red number (1,2,3,4)
            the piece of the second player: green number (1,2,3,4)
            if the piece on a protect cell print the number between < >
        """
        mp = {
            -1: "    ",
            0: " 🔳 ",
            1: colored(" 1 ", "red"),
            2: colored(" 2 ", "red"),
            3: colored(" 3 ", "red"),
            4: colored(" 4 ", "red"),
            5: colored(" 1 ", "blue"),
            6: colored(" 2 ", "blue"),
            7: colored(" 3 ", "blue"),
            8: colored(" 4 ", "blue"),
            10: "<🔳>",
            11: colored("<1>", "red"),
            12: colored("<2>", "red"),
            13: colored("<3>", "red"),
            14: colored("<4>", "red"),
            15: colored("<1>", "blue"),
            16: colored("<2>", "blue"),
            17: colored("<3>", "blue"),
            18: colored("<4>", "blue"),
        }

        arr = np.zeros((19, 19))
        n = arr.shape[0] - 1
        for i in range(8):
            for j in range(8):
                arr[i][j] = arr[i][n - j] = arr[n - i][j] = arr[n - i][n - j] = -1

        for i in range(3):
            for j in range(3):
                arr[8 + i][8 + j] = -1

        for x in self.protected_cell_2d:
            arr[x[0]][x[1]] += 10

        for i in range(self.player_pieces.shape[0]):
            for j in range(self.player_pieces.shape[1]):
                x, y = self.get_index(i, self.player_pieces[i][j])
                if x != -1 and y != -1:
                    if i == 1 and arr[x][y] % 10 == 0:
                        arr[x][y] += 4
                    arr[x][y] += 1

        for i in range(n + 1):
            for j in range(n + 1):
                print(mp[arr[i][j]], end=" ")
            print()
            print()



    def is_win(self, player):
        if np.all(self.player_pieces[player] == 84):
            return True
        return False



    def evaluate(self, distance):
        """
        we will make in the end
        calc the value of current Board, the value is between -100 and 100, like:
            100 mean  the first player certainly will win
            -100 mean  the second player certainly will win
            0 mean draw
            50 mean the first player likly to win
        """
        if self.is_finished():
            if self.is_win(0):
                return 100
            return -100
        ret = 0
        for i in self.player_pieces[0]:
            for j in self.player_pieces[1]:
                d = self.get_distance(i, j)
                if 0 <= d[0] <= 84:
                    ret += Board.W[0] * distance[d[0]]
                if 0 <= d[1] <= 84:
                    ret -= Board.W[1] * distance[d[1]]
        for i in range(len(self.player_pieces[0])):
            ret += Board.W[2] * self.player_pieces[0][i]
            ret -= Board.W[3] * self.player_pieces[1][i]

        return ret * Board.scale



    def can_move(self, player, piece, step):
        """
        Args:
            player (int): the player who is play (0,1)
            piece (int): the piece which will move (0,1,2,3)
            step (int): the step which will add to its position

        return:
            bool if it can move or not
        """
        dist = self.player_pieces[player][piece]

        # can't start (need Khal)
        if dist == 0 and step != 1:
            return False

        # can't end the game
        if dist + step > 84:
            return False

        # opponnent in protected cell

        i, j = self.get_index(player, dist + step)

        if (i, j) in self.protected_cell_2d:
            other = self.other_player(player)
            for x in self.player_pieces[other]:
                i2, j2 = self.get_index(other, x)
                if i == i2 and j == j2:
                    return False

        return True



    def move(self, player, piece, step):
        """_summary_

         Args:
            player (int): the player who is play (0,1)
            piece (int): the piece which will move (0,1,2,3)
            step (int): the step which will add to its position

        return:
        it will check if we can move, if:
            we can't it will be return false, a copy of the same board
            we can it will return true, a copy of new board

        """
        if not self.can_move(player, piece, step):
            return copy.deepcopy(self)

        new_board = copy.deepcopy(self)

        dist = new_board.player_pieces[player][piece] = (
            new_board.player_pieces[player][piece] + step
        )

        i, j = new_board.get_index(player, dist)

        other = new_board.other_player(player)

        for ind, val in enumerate(new_board.player_pieces[other]):
            i2, j2 = new_board.get_index(other, val)
            if i == i2 and j == j2:
                new_board.player_pieces[other][ind] = 0

        return new_board



    def get_next_possible_move(self, player, steps):
        """_summary_

        Args:
            player (int): the player who is play (0,1)
            steps (array of int): an array which generate from throw the shell

        it will call rec_next_move and return a np array of boards
        """

        steps = np.sort(steps)
        steps= (list)(steps)
        res = self.__rec_next_move(player, steps)
        # delete duplicate
        
        x = []
        for i in res:
            if not i in x:
                x.append(i)
        
        return x



    def __rec_next_move(self, player, steps):
        """_summary_

        Args:
            player (int): the player who is play (0,1)
            steps (array of int): an array which generate from throw the shell
            index (int, optional): the index of step which we will move with it

        it will try to move with this step for each piece.
        then for each board generate call rec_next_move and increase index by 1
        then add the result of each recursion call to a list and return the list
        """
        if  len(steps) == 0:
            return [self]
        
        

        ret = []
        unique_step= set(steps)
        
        for i in unique_step:
            for piece_index, val in enumerate(self.player_pieces[player]):

                if self.can_move(player, piece_index,i):
                    new_board = copy.deepcopy(self)
                    new_steps = copy.deepcopy(steps)
                    new_steps.remove(i)
                    new_board = new_board.move(player, piece_index, i)
                    ret  = ret + new_board.__rec_next_move(player, new_steps)
                    

        return ret



    def get_position(self, player, i, j, is_return=False):
        """_summary_

        Args:
            player (int): the current player
            i (int): the coordinate on the vertical axis
            j (int): the coordinate on the horizontal access
            is_return (bool): whether the piece is return to the start column
        convert 1-D coordinates to 2-D coordinates
        """
        # convert to second player grid
        if player == 1:
            i = 18 - i
            j = 18 - j

        # TODO: solve issue in overalpping path near start/end

        # quarter 1:
        if 11 <= j <= 18:
            if i == 10:
                return j - 11 + 17
            elif i == 9:
                return 18
            else:
                return 44 - j

        # quarter 2:
        if 0 <= i <= 7:
            if j == 10:
                return 41 - i
            elif j == 9:
                return 42
            elif j == 8:
                return 43 - i

        # quarter 3:
        if 0 <= j <= 7:
            if i == 8:
                return 58 - j
            if i == 9:
                return 59
            if i == 10:
                return j + 60

        # quarter 4:
        if 11 <= i <= 18:
            # left-most column:
            if j == 8:
                return i - 11 + 68
            elif j == 10:
                return 18 + 9 - i

        if is_return:
            return 94 - i
        else:
            return i - 10



    def get_distance(self, piece0, piece1):
        i0, j0 = self.get_index(0, piece0)
        i1, j1 = self.get_index(1, piece1)

        ret = [1000, 1000]

        if i0 == j0 and i1 == j1:
            return ret

        if 8 <= piece1 <= 76 and (i0, j0) in Board.protected_cell_2d:
            x = self.get_position(0, i1, j1, piece1 == 76)
            if x > piece0:
                ret[0] = x - piece0

        if 8 <= piece0 <= 76 and (i1, j1) in Board.protected_cell_2d:
            x = self.get_position(1, i0, j0, piece0 == 76)
            if x > piece1:
                ret[1] = x - piece1

        return ret
