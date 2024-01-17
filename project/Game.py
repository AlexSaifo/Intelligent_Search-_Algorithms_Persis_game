import numpy as np
import math
import random
from termcolor import colored
import copy
from Board import Board
from utils import prompt_and_validate


class Game:
    # the probability of head (1)
    p_head = 0.443
    max_depth = 2
    # max branching
    max_throw = 2
    # the min probability which is wcommand:cellOutput.enableScrolling?3262775c-2328-4622-bca6-87af4bd691e0e get move less than it we will cut the branch
    min_p = 1e-5
    shells_probabilities = np.array([0, 0, 0, 0, 0, 0, 0])
    shell_value = {
        #  the steps, one step plus, repeate
        0: (6, 0, 1),
        1: (10, 1, 1),
        2: (2, 0, 0),
        3: (3, 0, 0),
        4: (4, 0, 0),
        5: (25, 1, 1),
        6: (12, 0, 1),
    }
    #  list of step , p
    possible_steps = []
    distance = []
    cnt=0

    def __init__(self):
        self.board = Board()
        Game.calc_shells_probabilities()
        Game.get_possible_steps()
        Game.calc_distance_probability()



    @staticmethod
    def update_shells_probabilities(new_values):
        Game.shells_probabilities = np.array(new_values)



    @staticmethod
    def calc_shells_probabilities():
        new_value = []
        for i in range(7):
            new_value.append(
                math.comb(6, i) * Game.p_head**i * (1 - Game.p_head) ** (6 - i)
            )
        Game.update_shells_probabilities(new_value)



    @staticmethod
    def calc_distance_probability():
        probabilit = np.zeros(85)
        for possible_list in Game.possible_steps:
            sums = []
            Game.generate_all_possible_sums(0, 0, possible_list[0], sums)
            for j in range(85):
                if j in sums:
                    probabilit[j] += possible_list[1]
        Game.distance = probabilit



    @staticmethod
    def generate_all_possible_sums(sum, i, moves: list, sums):
        if i == len(moves):
            sums.append(sum)
            return
        Game.generate_all_possible_sums(sum + moves[i], i + 1, moves, sums)
        Game.generate_all_possible_sums(sum, i + 1, moves, sums)



    @staticmethod
    def delete_duplicate_lists(old: [list, float]):
        """
        delete duplicate lists
        """
        sums = {}
        for sublist, value in old:
            sublist.sort()
            tuple_sublist = tuple(sublist)
            if tuple_sublist in sums:
                sums[tuple_sublist] += value
            else:
                sums[tuple_sublist] = value

        result = [[list(key), value] for key, value in sums.items()]

        return result



    @staticmethod
    def get_possible_steps():
        final_lists = []
        curr_lists = []
        last_lists = [[[], 1]]

        for i in range(Game.max_throw):
            for j in last_lists:
                for k in range(7):
                    x = copy.deepcopy(j)
                    val = Game.shell_value[k]
                    x[0].append(val[0])
                    if val[1] != 0:
                        x[0].append(val[1])
                    x[1] *= Game.shells_probabilities[k]
                    # cannot repeate
                    if not val[2] or x[1] < Game.min_p:
                        final_lists.append(x)
                    else:
                        curr_lists.append(x)
            last_lists = Game.delete_duplicate_lists(copy.deepcopy(curr_lists))
            curr_lists = []

        final_lists = Game.delete_duplicate_lists(final_lists + last_lists)

        Game.possible_steps = final_lists




    def throw_shells(self):
        """
        get a random weighted number where the weights is the shells_probabilities
        """
        numbers = np.array(np.nonzero(Game.shells_probabilities)).flatten()
        chosen_number = random.choices(numbers, Game.shells_probabilities, k=1)[0]
        return chosen_number



    def optimize(self,player, first, second, alpha, beta):
        """_summary_

        Args:
            player (int): which player is optimize for, max (0) or min (1)
            first (board,value): the first board and its value
            second (board,value): the second board and its value

        return (board, value) which is optimal
        """
        if first[1] == -1000:
            if player == 0:
                alpha = max(alpha, second[1])
                return second, alpha, beta

            if player == 1:
                beta = min(beta, second[1])
                return second, alpha, beta

        if second[1] == -1000:
            if player == 0:
                alpha = max(alpha, first[1])
                return first, alpha, beta

            if player == 1:
                beta = min(beta, first[1])
                return first, alpha, beta
        
        if player == 0:
            alpha = max(alpha, first[1], second[1])
            if first[1] > second[1]:
                return first, alpha, beta
            return second, alpha, beta
        else:
            beta = min(beta, second[1], first[1])
            if first[1] < second[1]:
                return first, alpha, beta
            return second, alpha, beta




    def stop(self, board, curr_depth):
        if curr_depth >= Game.max_depth or board.is_finished():
            return True
        # if you want to generate search tree comment the last if  and uncomment the follow if
        # if  board.is_finished():
        #     return True

        return False




    def minmax(self, board: Board, player, steps, curr_depth, alpha, beta,b):
        """_summary_

        Args:
            board (Board): current board
            player (int): which player is optimize for, max (0) or min (1)
            steps (list of integer): the list of steps which player get by throw (or expected to get)
            curr_depth (int): number of turn which check it

        Returns:
            (Board, value): the best move and its value
        """
        Game.cnt+=1
        next_boards = board.get_next_possible_move(player, steps)

        if self.stop(board, curr_depth):
            return (board, board.evaluate(Game.distance))

        other = self.board.other_player(player)
        optimal = (board, -1000)
        prompt = []
    
        for i in next_boards:
            curr = self.minmax_expected_value(
                i, other, [], True, 1, 0, curr_depth + 1,  alpha, beta,b
            )
            prompt.append(f"{curr[1]}")
            optimal, alpha, beta = self.optimize(player,optimal, curr, alpha, beta)

        if (b):
            x = "," .join(prompt)
            print (f"the values of minmax node with player: {player}, is: {prompt}") 
            print (f"the return value of minmax node with player: {player}, is: {optimal[1]}") 
        
        return optimal




    def can_repeate(self, is_repeate, curr_probability, repeate_count):
        if (
            is_repeate
            and curr_probability >= Game.min_p
            and repeate_count <= Game.max_throw
        ):
            return True
        return False




    def minmax_expected_value(
        self,
        board: Board,
        player,
        steps,
        is_repeate,
        curr_probability,
        repeate_count,
        curr_depth,
        alpha,
        beta,
        b
    ):
        """_summary_

        Args:
            board (Board): current board
            player (int): which player is optimize for, max (0) or min (1)
            steps (list of integer): the list of steps which player get by throw (or expected to get)
            is_repeate (bool): if has Khal
            curr_probability (float): Cumulative probability from the first throw of this player turn until now
            repeate_count (int): how much Khal get In a row
            curr_depth (int): number of turn which check it

        Returns:
            (Board, value): the best move and its value

        """
        Game.cnt+=1
        
        if self.stop(board, curr_depth):
            return (board, board.evaluate(Game.distance))

        ev = 0  # expected value
        rest_p = 1
        prompt =[]
        # print (len(Game.possible_steps))
        for i in Game.possible_steps:
            # if player == 0:  # Maximize
            #     if beta <= ev + rest_p * Board.max_evaluation:
            #         ev = ev + rest_p * Board.max_evaluation
            #         break
            # if player == 1:  # minimize
            #     if alpha >= ev + rest_p * Board.min_evaluation:
            #         ev = ev + rest_p * Board.min_evaluation
            #         break

            x = self.minmax(board, player, i[0], curr_depth,  alpha, beta,b)
            prompt.append(f"( p= {i[1]} , v= {x[1]})")
            ev += i[1] * x[1]
            rest_p -= i[1]

        if (b):
            x = "," .join(prompt)
            print (f"the values of expected value node with player: {player}, is: {prompt}") 
            print (f"the return value of expected value node with player: {player}, is: {ev}") 
        
        return (board, ev)




    def play(self):
        """
        the iterative for every player game
        """
        x=input("enter 'yes' to print info, or any thing to don't print it ")
        b=False
        if(x=="yes"):
            b=True
        while not self.board.is_finished():
            self.first_player_play(b)
            if self.board.is_finished():
                break
            self.second_player_play()
        
        print (f"your piece is: {self.board.player_pieces[1]}")
        print (f"and computer piece is: {self.board.player_pieces[0]}")
        if(self.board.is_win(0)):
            print ("So Computer is win, Good Luck in next game")
        if(self.board.is_win(1)):
            print ("So you are win, it's Great")
            
      
      
            
    def first_player_play(self,b):
        repeate = True
        steps = []
        cnt=0
        while repeate and cnt < Game.max_throw:
            cnt+=1  
            val = self.throw_shells()
            repeate = (bool)(Game.shell_value[val][2])
            steps.append(Game.shell_value[val][0])
            if Game.shell_value[val][1] != 0:
                steps.append(Game.shell_value[val][1])
        steps.sort()
        cnt=0
        board, value = self.minmax(self.board, 0, steps, 0, -100,100,b)
        self.board = board
        if(b):
            print(f"the number of visited node: {Game.cnt}")
            print(f"the value of this board is: {value}")
        print(steps)
        board.print()
        




    def second_player_play(self):
        repeate = True
        steps = []
        cnt =0
        while repeate and cnt < Game.max_throw:
            cnt+=1
            inp = prompt_and_validate(str, "enter any thing to throw shells: ")
            val = self.throw_shells()
            repeate = (bool)(Game.shell_value[val][2])
            print(f"you get {val} shell, so your repeate is {repeate} ")
            steps.append(Game.shell_value[val][0])
            if Game.shell_value[val][1] != 0:
                steps.append(Game.shell_value[val][1])

        while len(steps) > 0:
            self.board.print()
            print("you have this list to move use it:")
            print("Steps:")
            for ind, val in enumerate(steps):
                print(f"the step number {ind} has value : {val}")

            print("your pieces is:")
            for ind, val in enumerate(self.board.player_pieces[1]):
                print(f"the piece number {ind} has color #### , and is travle: {val}")

            next_steps = self.board.get_next_possible_move(1, steps)
            if (len(next_steps) == 0) or (
                len(next_steps) == 1 and next_steps[0] == self.board
            ):
                print("you cannot move.")
                break

            print("enter the number of piece then enter then the number of step.")

            piece = prompt_and_validate(
                int, "enter the number of piece you want to move: "
            )
            step_index = prompt_and_validate(
                int, "enter the number of step you want to move by it: "
            )

            if (
                step_index >= len(steps)
                or piece >= 4
                or not self.board.can_move(1, piece, steps[step_index])
            ):
                print("this move is not allowed")
            else:
                self.board = self.board.move(1, piece, steps[step_index])
                steps.pop(step_index)
