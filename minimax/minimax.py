import logging
import argparse
import random
import quarto
import math
import copy
import numpy as np
import pickle

self_choose_cache = dict()  # state: score
self_place_cache = dict()
opponent_choose_cache = dict()
opponent_place_cache = dict()


# IDEA: if there are three in a row (win opportunity) and I can place a piece
# that doesn't lead to a win, keep it for later (unless all next choices are losing). 
class MinimaxPlayer(quarto.Player):
    """Minimax player"""

    # move type constants
    SELF_CHOOSE = 0
    SELF_PLACE = 1
    OPPONENT_CHOOSE = 2 
    OPPONENT_PLACE = 3
    # Minmax depth
    MINMAX_DEPTH = 8

    def __init__(self, quarto: quarto.Quarto, cache_file=None) -> None:
        super().__init__(quarto)
        self.current_game = quarto
        self.current_game._board = quarto._board
        if cache_file is not None:
            # load cache
            load_cache(cache_file)
    
    def get_game(self):
        # override
        return self.current_game
    
    # custom quarto methods
    def try_select(self, game, pieceIndex: int) -> bool:
        '''
        try to select a piece. Returns True on success
        '''
        if pieceIndex not in game._board:
            return True
        return False
    
    def try_place(self, game, x: int, y: int) -> bool:
        '''
        Verify if a piece is placeable but don't actually place it 
        '''
        if game._Quarto__placeable(x, y):
            return True
        return False
    
    def unplace(self, game, x: int, y: int) -> bool:
        '''
        Take away piece in coordinates (x, y). Returns true on success
        '''
        game._board[y, x] = -1
        game._Quarto__binary_board[y,
                            x][:] = np.nan
        return True
    
    # provided methods
    def choose_piece(self) -> int:
        # move = self.choose_move_minimax(self.SELF_CHOOSE)
        move = self.choose_move_alphabeta(self.SELF_CHOOSE)
        return move

    def place_piece(self) -> tuple[int, int]:
        # move = self.choose_move_minimax(self.SELF_PLACE)
        move = self.choose_move_alphabeta(self.SELF_PLACE)
        return move


    # custom methods
    def check_win(self, game, piece=-1):
        ''' Check if the player can win by placing the assigned piece. returns (x, y). If there is no winning move: returns (-1, -1)'''
        if piece >= 0:
            game.select(piece)
        # else: piece is already chosen, do nothing
        winning_x = -1
        winning_y = -1
        for x in range(game.BOARD_SIDE):
            for y in range(game.BOARD_SIDE):
                # try to place piece in every possible position, return the first that wins.
                if game.place(x, y):
                    # perform victory check
                    if game.check_winner() >= 0:
                        winning_x = x
                        winning_y = y
                        self.unplace(game, x,y)
                        return winning_x, winning_y
                    self.unplace(game, x, y)
        return winning_x, winning_y

    def make_choosing_move(self, game):
        ''' Check if the player can lose by choosing a piece. Returns (move, score)'''
        safe_moves = list()
        for i in range(16):
            if game.select(i):
                # check if the opponent can win if I choose this piece
                xx, yy = self.check_win(game, i)
                if xx < 0 and yy < 0: # the opponent can't win
                    # there is no winning move for the opponent using this piece
                    safe_moves.append(i)
        if len(safe_moves) > 0:
            return random.choice(safe_moves), 0
        return random.randint(0, 15), -1

    def make_placing_move(self, game):
        # if there's a winning move, do that. otherwise random move
        move = self.check_win(game)
        if move == (-1, -1):
        # choose random (eligible) move
            x, y = random.randint(0, 3), random.randint(0, 3)
            while not self.try_place(game, x, y):
                x, y = random.randint(0, 3), random.randint(0, 3)
            return (x, y), 0
        return move, 1
    

    def choose_move_minimax(self, move_type):
        # for each possible move: compute minimax score
        # play the maximum scoring move
        game = copy.deepcopy(self.current_game)
        if move_type == self.SELF_CHOOSE:
            # explore all possible choosing moves
            valid_choices = self.get_valid_choices(game)
            winning_choices = list()
            draw_choices = list()
            losing_choices = list()
            for choice in valid_choices:
                game.select(choice)
                # run minimax
                score = self.minimax(game, self.MINMAX_DEPTH, self.SELF_CHOOSE)
                if score == 1:
                    winning_choices.append(choice)
                elif score == 0:
                    draw_choices.append(choice)
                else:
                    losing_choices.append(choice)
            # finally choose a move.
            if len(winning_choices) > 0:
                return random.choice(winning_choices)
            if len(draw_choices) > 0:
                return random.choice(draw_choices)
            if len(losing_choices) > 0:
                return random.choice(losing_choices)
            # if I'm here, something went wrong
            randomchoice = random.randint(0, 15)
            while not self.try_select(game, randomchoice):
                randomchoice = random.randint(0, 15)
            return randomchoice
            
        elif move_type == self.SELF_PLACE:
            # explore all possible placing moves
            possible_moves = self.get_valid_placements(game)
            winning_moves = list()
            draw_moves = list()
            losing_moves = list()
            for (x, y) in possible_moves:
                game.place(x, y)
                score = self.minimax(game, self.MINMAX_DEPTH, self.SELF_PLACE)
                self.unplace(game, x, y)
                if score == 1:
                    winning_moves.append((x, y))
                elif score == 0:
                    draw_moves.append((x, y))
                elif score == -1:
                    losing_moves.append((x, y))
            # finally choose a move.
            if len(winning_moves) > 0:
                return random.choice(winning_moves)
            if len(draw_moves) > 0:
                return random.choice(draw_moves)
            if (len(losing_moves) > 0):
                return random.choice(losing_moves)
            # I shouldn't be here
            while not self.try_place(game, x, y):
                x, y = random.randint(0, 3), random.randint(0, 3)
            return (x, y)

    def choose_move_alphabeta(self, move_type):
        # for each possible move: compute minimax score
        # play the maximum scoring move
        game = copy.deepcopy(self.current_game)
        if move_type == self.SELF_CHOOSE:
            # explore all possible choosing moves
            valid_choices = self.get_valid_choices(game)
            winning_choices = list()
            draw_choices = list()
            losing_choices = list()
            for choice in valid_choices:
                game.select(choice)
                # run minimax
                score = self.alphabeta(game, self.MINMAX_DEPTH, -math.inf, math.inf, self.SELF_CHOOSE)
                if score == 1:
                    winning_choices.append(choice)
                elif score == 0:
                    draw_choices.append(choice)
                else:
                    losing_choices.append(choice)
            # finally choose a move.
            if len(winning_choices) > 0:
                return random.choice(winning_choices)
            if len(draw_choices) > 0:
                return random.choice(draw_choices)
            if len(losing_choices) > 0:
                return random.choice(losing_choices)
            # if I'm here, something went wrong
            randomchoice = random.randint(0, 15)
            while not self.try_select(game, randomchoice):
                randomchoice = random.randint(0, 15)
            return randomchoice
            
        elif move_type == self.SELF_PLACE:
            # explore all possible placing moves
            possible_moves = self.get_valid_placements(game)
            winning_moves = list()
            draw_moves = list()
            losing_moves = list()
            for (x, y) in possible_moves:
                game.place(x, y)
                score = self.alphabeta(game, self.MINMAX_DEPTH, -math.inf, math.inf, self.SELF_PLACE)
                self.unplace(game, x, y)
                if score == 1:
                    winning_moves.append((x, y))
                elif score == 0:
                    draw_moves.append((x, y))
                elif score == -1:
                    losing_moves.append((x, y))
            # finally choose a move.
            if len(winning_moves) > 0:
                return random.choice(winning_moves)
            if len(draw_moves) > 0:
                return random.choice(draw_moves)
            if (len(losing_moves) > 0):
                return random.choice(losing_moves)
            # I shouldn't be here
            while not self.try_place(game, x, y):
                x, y = random.randint(0, 3), random.randint(0, 3)
            return (x, y)

    def __evaluate_position(self, game, move_type) -> int:
        ''' Returns the score of the given position. '''
        # evaluate score of the position based on turn
        if move_type == self.SELF_PLACE:
            # I just placed! Did I win?
            if game.check_winner() >= 0:
                return 1
            # if I didn't win, return 0
            return 0
        elif move_type == self.OPPONENT_PLACE:
            # opponent just placed. Did I lose?
            if game.check_winner() >= 0:
                return -1
            # if I didn't lose, return 0
            return 0
        elif move_type == self.SELF_CHOOSE:
            # I just chose! can opponent win?
            _, score = self.make_placing_move(game)
            return -score
        elif move_type == self.OPPONENT_CHOOSE:
            # opponent just chose! Can I win?
            _, score = self.make_placing_move(game)
            return score
    
    def minimax(self, current_state, depth, move_type) -> int:
        # move_type: la mossa che è appena stata fatta
        score = self.__evaluate_position(current_state,move_type)
        if score == 1 or score == -1:
            # Terminal node
            # save to cache
            hash = str(current_state.get_board_status())
            if move_type == self.SELF_CHOOSE:
                if hash not in self_choose_cache.keys():
                    self_choose_cache[hash] = score
            elif move_type == self.SELF_PLACE:
                if hash not in self_place_cache.keys():
                    self_place_cache[hash] = score
            elif move_type == self.OPPONENT_CHOOSE:
                if hash not in opponent_choose_cache.keys():
                    opponent_choose_cache[hash] = score
            else:
                if hash not in opponent_place_cache.keys():
                    opponent_place_cache[hash] = score
            return score
        if depth <= 0:
           return 0
        # else: recursively explore game tree
        game = copy.deepcopy(current_state)
        if move_type == self.SELF_CHOOSE:
            # check if it's in cache
            hash = str(current_state.get_board_status())
            if hash in opponent_place_cache.keys():
                return opponent_place_cache[hash]
            score = math.inf
            # get all possible moves
            possible_moves = self.get_valid_placements(game)
            for (x, y) in possible_moves:
                game.place(x, y)
                move_score = self.minimax(game, depth - 1, self.OPPONENT_PLACE) # OPPONENT JUST PLACED
                score = min(move_score, score)
                self.unplace(game, x, y)
            # save to cache
            opponent_place_cache[hash] = score
            return score
        
        if move_type == self.OPPONENT_PLACE: # LUI HA APPENA PIAZZATO -> TOCCA A LUI SCEGLIERE
            # check if it's in cache
            hash = str(current_state.get_board_status())
            if hash in opponent_choose_cache.keys():
                return opponent_choose_cache[hash]
            score = math.inf
            # get all possible choices
            possible_choices = self.get_valid_choices(game)
            last_choice = game.get_selected_piece()
            for choice in possible_choices:
                game.select(choice)
                choice_score = self.minimax(game, depth - 1, self.OPPONENT_CHOOSE) # HA APPENA SCELTO
                score = min(choice_score, score)
            # restore last piece
            game.select(last_choice)
            # save to cache
            opponent_choose_cache[hash] = score
            return score

        if move_type == self.SELF_PLACE:  # HO APPENA PIAZZATO, ORA SCELGO
            hash = str(current_state.get_board_status())
            if hash in self_choose_cache.keys():
                return self_choose_cache[hash]
            score = -math.inf
            # get all possible choices
            possible_choices = self.get_valid_choices(game)
            last_choice = game.get_selected_piece()
            for choice in possible_choices:
                game.select(choice)
                choice_score = self.minimax(game, depth - 1, self.SELF_CHOOSE) # HO APPENA SCELTO
                score = max(choice_score, score)
            # restore last piece
            game.select(last_choice)
            # save to cache
            self_choose_cache[hash] = score
            return score
        
        if move_type == self.OPPONENT_CHOOSE: #OPPONENT HA APPENA SCELTO
            # check if it's in cache
            hash = str(current_state.get_board_status())
            if hash in self_place_cache.keys():
                return self_place_cache[hash]
            score = -math.inf
            # get all possible moves
            possible_moves = self.get_valid_placements(game)
            for (x, y) in possible_moves:
                game.place(x, y)
                move_score = self.minimax(game, depth - 1, self.SELF_PLACE) # piazzo io
                score = max(move_score, score)
                self.unplace(game, x, y)
            # save to cache
            self_place_cache[hash] = score
            return score

    def alphabeta(self, current_state, depth, alpha, beta, move_type) -> int:
        # move_type: la mossa che è appena stata fatta
        score = self.__evaluate_position(current_state,move_type)
        if score == 1 or score == -1:
            # Terminal node
            # save to cache
            hash = str(current_state.get_board_status())
            if move_type == self.SELF_CHOOSE:
                if hash not in self_choose_cache.keys():
                    self_choose_cache[hash] = score
            elif move_type == self.SELF_PLACE:
                if hash not in self_place_cache.keys():
                    self_place_cache[hash] = score
            elif move_type == self.OPPONENT_CHOOSE:
                if hash not in opponent_choose_cache.keys():
                    opponent_choose_cache[hash] = score
            else:
                if hash not in opponent_place_cache.keys():
                    opponent_place_cache[hash] = score
            return score
        if depth <= 0:
           return 0
        # else: recursively explore game tree
        game = copy.deepcopy(current_state)
        if move_type == self.SELF_CHOOSE:
            # check if it's in cache
            hash = str(current_state.get_board_status())
            if hash in opponent_place_cache.keys():
                return opponent_place_cache[hash]
            score = math.inf # minimizing player's turn (opponent)
            # get all possible moves
            possible_moves = self.get_valid_placements(game)
            for (x, y) in possible_moves:
                game.place(x, y)
                move_score = self.alphabeta(game, depth - 1, alpha, beta, self.OPPONENT_PLACE) # OPPONENT JUST PLACED
                score = min(move_score, score)
                beta = min(beta, score)
                self.unplace(game, x, y)
                if score <= alpha:
                    break # alpha cutoff
            # save to cache
            opponent_place_cache[hash] = score
            return score
        
        if move_type == self.OPPONENT_PLACE: # LUI HA APPENA PIAZZATO -> TOCCA A LUI SCEGLIERE
            # check if it's in cache
            hash = str(current_state.get_board_status())
            if hash in opponent_choose_cache.keys():
                return opponent_choose_cache[hash]
            score = math.inf
            # get all possible choices
            possible_choices = self.get_valid_choices(game)
            last_choice = game.get_selected_piece()
            for choice in possible_choices:
                game.select(choice)
                choice_score = self.alphabeta(game, depth - 1, alpha, beta, self.OPPONENT_CHOOSE) # HA APPENA SCELTO
                score = min(choice_score, score)
                beta = min(beta, score)
                if score <= alpha:
                    break
            # restore last piece
            game.select(last_choice)
            # save to cache
            opponent_choose_cache[hash] = score
            return score

        if move_type == self.SELF_PLACE:  # HO APPENA PIAZZATO, ORA SCELGO
            hash = str(current_state.get_board_status())
            if hash in self_choose_cache.keys():
                return self_choose_cache[hash]
            score = -math.inf
            # get all possible choices
            possible_choices = self.get_valid_choices(game)
            last_choice = game.get_selected_piece()
            for choice in possible_choices:
                game.select(choice)
                choice_score = self.alphabeta(game, depth - 1, alpha, beta, self.SELF_CHOOSE) # HO APPENA SCELTO
                score = max(choice_score, score)
                alpha = max(alpha, score)
                if score >= beta:
                    break
            # restore last piece
            game.select(last_choice)
            # save to cache
            self_choose_cache[hash] = score
            return score
        
        if move_type == self.OPPONENT_CHOOSE: #OPPONENT HA APPENA SCELTO
            # check if it's in cache
            hash = str(current_state.get_board_status())
            if hash in self_place_cache.keys():
                return self_place_cache[hash]
            score = -math.inf
            # get all possible moves
            possible_moves = self.get_valid_placements(game)
            for (x, y) in possible_moves:
                game.place(x, y)
                move_score = self.alphabeta(game, depth - 1, alpha, beta, self.SELF_PLACE) # piazzo io
                score = max(move_score, score)
                alpha = max(alpha, score)
                self.unplace(game, x, y)
                if score >= beta:
                    break
            # save to cache
            self_place_cache[hash] = score
            return score

    def get_valid_choices(self, game):
        all_choices = list(range(16))
        valid_choices = list()
        for choice in all_choices:
            if self.try_select(game, choice):
                valid_choices.append(choice)
        return valid_choices
    
    def get_valid_placements(self, game):
        all_x = list(range(4))
        all_y = list(range(4))
        valid_moves = list()
        for x in all_x:
            for y in all_y:
                if self.try_place(game, x, y):
                    valid_moves.append((x, y))
        return valid_moves
    
def save_cache(filename):
    picklefile = open(filename, 'wb')
    data = [self_place_cache, self_choose_cache, opponent_place_cache, opponent_choose_cache]
    pickle.dump(data, picklefile)
    picklefile.close()

def load_cache(filename):
    picklefile = open(filename, 'rb')
    data = pickle.load(picklefile)
    picklefile.close()
    # overwrite existing cache
    global self_place_cache
    global self_choose_cache
    global opponent_place_cache
    global opponent_choose_cache

    self_place_cache = data[0]
    self_choose_cache = data[1]
    opponent_place_cache = data[2]
    opponent_choose_cache = data[3]
    