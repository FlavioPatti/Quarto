import logging
import argparse
import random
import quarto
import copy
from quarto.genetic_algorithm import GeneticAlgorithm
from quarto.QL_agent import QL_Agent
from main import RandomPlayer
def cycle(game, player1, num_matches):
    win = 0
    draw = 0
    loss = 0
    
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
        #if winner == 1 or winner == 0:
            #print(f"Match # {i} -> Winner -> {type(game._Quarto__players[winner]).__name__} -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
        #else:
            #print(f"Match # {i} -> Winner -> Both -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
    #print(player1.q)
    print("epsilon= ", player1.epsilon)
    print("rewards= ", player1.number_rewards)        
    win_rate = win / num_matches
    #print(f"Win rate = {win_rate}")
    return win_rate

if __name__ == '__main__':
    game = quarto.Quarto()
    player1=QL_Agent(game)
    num_matches = 500
    cycles=1
    for i in range(cycles):
        win_rate=cycle(game, player1,num_matches)
        print("cycle ", i+1,": ",win_rate)
    