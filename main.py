# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
import quarto
import copy
from EA.genetic_algorithm import GeneticAlgorithm
from Risky.risky_algorithm import RiskyAlgorithm
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
    
    def __init__(self, quarto: quarto.Quarto):
        #super().__init__(quarto)
        self.risky = RiskyAlgorithm(quarto)

    def choose_piece(self):
        return self.risky.choose_piece()

    def place_piece(self):
        return self.risky.place_piece()
                
class GeneticPlayer(quarto.Player):
    """GA player"""

    def __init__(self, quarto: quarto.Quarto):
        #super().__init__(quarto)
        self.geneticAlgorithm = GeneticAlgorithm(quarto)

        self.piece_to_give = None
        self.pos_chosen = None

    def choose_piece(self):
        (self.piece_to_give, self.pos_chosen) = self.geneticAlgorithm.my_move()
        return self.piece_to_give

    def place_piece(self):
        (self.piece_to_give, self.pos_chosen) = self.geneticAlgorithm.my_move()
        return self.pos_chosen



def main():
    win = 0
    draw = 0
    loss = 0
    num_matches = 1
    Xsecondo = True
    
    for i in range(num_matches):
        game = quarto.Quarto()
        
        #game.set_players((GeneticPlayer(game), RandomPlayer(game)))
        game.set_players((RandomPlayer(game), RiskyAlgorithm(game)))  
        winner = game.run()
        if Xsecondo:
            if winner == 1:
                win = win + 1
            elif winner == -1:
                draw = draw + 1
            else:
                loss = loss + 1
        else:
            if winner == 0:
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