# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
import quarto
import copy
from EA.genetic_algorithm import GeneticAlgorithm
import numpy as np

class RandomPlayer(quarto.Player):
    """Random player"""

    def __init__(self, quarto: quarto.Quarto):
        super().__init__(quarto)

    def choose_piece(self):
        piece = random.randint(0, 15)
        #print("Random chooses piece - ", piece)
        return piece

    def place_piece(self):
        pos = (random.randint(0, 3), random.randint(0, 3))
        #print("Random chooses pos - ", pos)
        return pos #column, row
    
   
class RiskyPlayer(quarto.Player):
    """Risky player"""
    
    BOARD_SIDE = 4
    
    def __init__(self, quarto: quarto.Quarto):
        super().__init__(quarto)
        
    def check_piece_in_board(self,quarto, piece):
        for row in range(self.BOARD_SIDE):
            for col in range(self.BOARD_SIDE):
                if quarto._Quarto__board[col,row] == piece:
                    return 1
        return 0
    
    def check_winning_move(self, quarto):
        cwmh = quarto._Quarto__check_horizontal()
        cwmv = quarto._Quarto__check_vertical()
        cwmd = quarto._Quarto__check_diagonal()
        if cwmh != -1 or cwmv != -1 or cwmd != -1:
            return 1
        else:
            return 0
        
    def check_line_of_like_horizontal(self, quarto):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and quarto._Quarto__pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and quarto._Quarto__pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and quarto._Quarto__pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and quarto._Quarto__pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in quarto._Quarto__board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].SQUARE
            ]
            if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
                return 1
        return -1

    def check_line_of_like_vertical(self, quarto):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in quarto._Quarto__board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].SQUARE
            ]
            if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
                return 1
        return -1

    def check_line_of_like_diagonal(self, quarto):
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if quarto._Quarto__board[i, i] < 0:
                break
            if quarto._Quarto__pieces[quarto._Quarto__board[i, i]].HIGH:
                high_values.append(quarto._Quarto__board[i, i])
            else:
                low_values.append(quarto._Quarto__board[i, i])
            if quarto._Quarto__pieces[quarto._Quarto__board[i, i]].COLOURED:
                coloured_values.append(quarto._Quarto__board[i, i])
            else:
                noncolor_values.append(quarto._Quarto__board[i, i])
            if quarto._Quarto__pieces[quarto._Quarto__board[i, i]].SOLID:
                solid_values.append(quarto._Quarto__board[i, i])
            else:
                hollow_values.append(quarto._Quarto__board[i, i])
            if quarto._Quarto__pieces[quarto._Quarto__board[i, i]].SQUARE:
                square_values.append(quarto._Quarto__board[i, i])
            else:
                circle_values.append(quarto._Quarto__board[i, i])
        if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
            return 1
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i] < 0:
                break
            if quarto._Quarto__pieces[quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i]].HIGH:
                high_values.append(quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
            else:
                low_values.append(quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
            if quarto._Quarto__pieces[quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i]].COLOURED:
                coloured_values.append(
                    quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
            else:
                noncolor_values.append(
                    quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
            if quarto._Quarto__pieces[quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i]].SOLID:
                solid_values.append(quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
            else:
                hollow_values.append(quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
            if quarto._Quarto__pieces[quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i]].SQUARE:
                square_values.append(quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
            else:
                circle_values.append(quarto._Quarto__board[i, self.BOARD_SIDE - 1 - i])
        if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
            return 1
        return -1
    
    def check_line_of_like(self, quarto):
        cllh = self.check_line_of_like_horizontal(quarto)
        cllv = self.check_line_of_like_vertical(quarto)
        clld = self.check_line_of_like_diagonal(quarto)
        if cllh == 1 or cllv == 1 or clld == 1:
            return 1
        else:
            return 0

    def choose_piece(self):
        """Evito di dare un pezzo che fa vincere l'avversario"""
        quarto = self.get_game()
        for piece in range(self.BOARD_SIDE*self.BOARD_SIDE):
            if self.check_piece_in_board(quarto, piece)==0:
                winning_move = 0
                for i in range(self.BOARD_SIDE): #col
                    for j in range(self.BOARD_SIDE): #row
                        game_copy = copy.deepcopy(quarto)
                        if winning_move == 0:
                            game_copy.place(i, j)
                            if self.check_winning_move(game_copy):
                                winning_move = 1
                if winning_move == 0:
                    print(f"risky sceglie pezzo {piece}")
                    return piece
        "Altrimenti do un pezzo random"
        piece = random.randint(0,15)
        print(f"risky sceglie pezzo {piece}")
        return piece

    def place_piece(self):
        """Controllo se è possibile fare una mossa vincente"""
        winning_move = 0
        line_of_like = 0
        piece_ok = False
        quarto = self.get_game()
        for i in range(self.BOARD_SIDE): #col
            for j in range(self.BOARD_SIDE): #row
                game_copy = copy.deepcopy(quarto)
                piece_ok = game_copy.place(i, j)
                if piece_ok == True:
                    if self.check_winning_move(game_copy):
                        winning_move = 1
                        print(f"risky piazza in posizione {i}-{j}")
                        return i, j
        """Altrimenti faccio una mossa lines of like se possibile"""
        """lines of like = controllo se ci sono pezzi che hanno almeno una caratteristica in comune"""    
        piece_ok = False    
        if winning_move == 0:
            quarto = self.get_game()
            for i in range(self.BOARD_SIDE): #col
                for j in range(self.BOARD_SIDE): #row
                    game_copy = copy.deepcopy(quarto)
                    piece_ok = game_copy.place(i, j)
                    if piece_ok == True:
                        if self.check_line_of_like(game_copy):
                            line_of_like = 1
                            print(f"risky piazza in posizione {i}-{j}")
                            return i, j;
        """Altrimenti faccio una mossa random""" 
        piece_ok = False
        quarto = self.get_game()
        if line_of_like == 0:
            while not piece_ok:
                x, y = random.randint(0, 3), random.randint(0, 3)
                if quarto._Quarto__board[y,x] == -1:
                    piece_ok = True
                    print(f"risky piazza in posizione {x}-{y}")
                    return x, y 
                
class GeneticPlayer(quarto.Player):
    """GA player"""

    def __init__(self, quarto: quarto.Quarto):
        #super().__init__(quarto)
        self.geneticAlgorithm = GeneticAlgorithm(quarto)

        self.piece_to_give = None
        self.pos_chosen = None

    def choose_piece(self):
        # How to handle first case??
        #print("G chooses piece - ", self.piece_to_give)
        return self.piece_to_give

    def place_piece(self):
        (self.piece_to_give, self.pos_chosen) = self.geneticAlgorithm.my_move()
        #print("G chooses pos - ", self.pos_chosen)
        return self.pos_chosen


    
class GeneticPlayer(quarto.Player):
    """GA player"""

    def __init__(self, quarto: quarto.Quarto):
        #super().__init__(quarto)
        self.geneticAlgorithm = GeneticAlgorithm(quarto)

        self.piece_to_give = None
        self.pos_chosen = None

    def choose_piece(self):
        # How to handle first case??
        #print("G chooses piece - ", self.piece_to_give)
        return self.piece_to_give

    def place_piece(self):
        (self.piece_to_give, self.pos_chosen) = self.geneticAlgorithm.my_move()
        #print("G chooses pos - ", self.pos_chosen)
        return self.pos_chosen


def main():
    win = 0
    draw = 0
    loss = 0
    num_matches = 3000
    game = quarto.Quarto()
    player1=QL_Agent(game)
    
    for i in range(num_matches):
        
        game.reset()
        #print("-------- PARTITA ", i)
        game.set_players((RandomPlayer(game), player1)) #player 0 = random = avversario, player 1 = risky = io
        winner = game.run()
        player1.epsilon=max(player1.epsilon*player1.epsilon_decay,player1.min_epsilon)
        if winner == 1:
            win = win + 1
        elif winner == -1:
            draw = draw + 1
        else:
            loss = loss + 1
        #print("Winner is: ", winner)
        win_rate = win / (i+1)
        draw_rate = draw / (i+1)
        loss_rate = loss / (i+1)
        if winner == 1 or winner == 0:
            print(f"Match # {i} -> Winner -> {type(game._Quarto__players[winner]).__name__} -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
        else:
            print(f"Match # {i} -> Winner -> Both -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
    #print(player1.q)
    print(player1.epsilon)        
    win_rate = win / num_matches
    print(f"Win rate = {win_rate}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0, help='increase log verbosity')
    parser.add_argument('-d',
                        '--debug',
                        action='store_const',
                        dest='verbose',
                        const=2,
                        help='log debug messages (same as -vv)')
    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)

    main()