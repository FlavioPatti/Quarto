# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
import quarto
import copy
from quarto.genetic_algorithm import GeneticAlgorithm

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
    num_matches = 100
    
    for i in range(num_matches):
        game = quarto.Quarto()
        
        #print("-------- PARTITA ", i)
        game.set_players((RandomPlayer(game), GeneticPlayer(game))) #player 0 = random = avversario, player 1 = risky = io
        winner = game.run()
        if winner == 1:
            win = win + 1
        #print("Winner is: ", winner)
        win_rate = win / (i+1)
        print(f"Match # {i} -> Winner -> {type(game._Quarto__players[winner]).__name__} -> Win rate = {win_rate}")

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
