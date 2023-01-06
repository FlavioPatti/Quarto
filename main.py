# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import logging
import argparse
import random
import quarto
import copy
from genetic_algorithm import GeneticAlgorithm

class RandomPlayer(quarto.Player):
    """Random player"""

    def __init__(self, quarto: quarto.Quarto):
        super().__init__(quarto)

    def choose_piece(self):
        return random.randint(0, 15)

    def place_piece(self):
        return random.randint(0, 3), random.randint(0, 3) #column, row
    
class GeneticPlayer(quarto.Player):
    """GA player"""

    def __init__(self, quarto: quarto.Quarto):
        super().__init__(quarto)
        self.geneticAlgorithm = GeneticAlgorithm(quarto)

    def choose_piece(self):
        return self.geneticAlgorithm.my_move()[0]

    def place_piece(self):
        return self.geneticAlgorithm.my_move()[1]


def main():
    
    win = 0
    num_matches = 1
    game = quarto.Quarto()
    for i in range(num_matches):
        game.set_players((RandomPlayer(game), GeneticPlayer(game))) #player 0 = random = avversario, player 1 = risky = io
        winner = game.run()
        if winner == 1:
            win = win + 1
        game.clear()
    win_rate = win / num_matches
    print(f"win rate = {win_rate}")



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