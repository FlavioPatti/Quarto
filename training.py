import logging
import argparse
import random
import quarto
import copy
from quarto.genetic_algorithm import GeneticAlgorithm
from quarto.QL_agent import QL_Agent
from quarto.QL_agent2 import QL_Agent2
from quarto.QL_agent3 import QL_Agent3
from quarto.RL_agent import RL_Agent
from main import RandomPlayer


def cycle(game, player0, player1, num_matches):
    win = 0
    draw = 0
    loss = 0
    for i in range(num_matches):
        
        game.reset()
        #print("-------- PARTITA ", i)
        game.set_players((player0, player1)) 
        winner = game.run()
        player1.learn(winner)
        #player1.epsilon=max(player1.epsilon*player1.epsilon_decay,player1.min_epsilon)
        #player1.update_q(player1.previous_state, winner)
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
    #counter_r=0
    #for v in player1.q.values():
    #    if  v>1 or v<-1 :
    #        counter_r+=1
    #print("count of cool rewards: ", counter_r)
    print("epsilon= ", player1.epsilon)
    #print("rewards= ", player1.number_rewards)        
    win_rate = win / num_matches
    #print(f"Win rate = {win_rate}")
    return win_rate


if __name__ == '__main__':
    game = quarto.Quarto()
    player0=RandomPlayer(game)
    player1=RL_Agent(game)
    num_matches = 1000
    cycles=20
    #first cycle of training against random player
    for i in range(cycles):
        win_rate=cycle(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle ", i+1," win rate: ",win_rate)
    player1.save()
    player0=RL_Agent(player1.get_game(),False,True)
    num_matches = 1000
    cycles=20
    #second cycle of training against previously pretrained QL agent
    for i in range(cycles):
        win_rate=cycle(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle ", i+1," win rate: ",win_rate)
    player1.save()
    player0=RL_Agent(player1.get_game(),False,True)
    num_matches = 1000
    cycles=20
    #second cycle of training against previously pretrained QL agent
    for i in range(cycles):
        win_rate=cycle(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle ", i+1," win rate: ",win_rate)
    player1.save()
    player0=RandomPlayer(player1.get_game())
    num_matches = 1000
    cycles=20
    #second cycle of training against previously pretrained QL agent
    for i in range(cycles):
        win_rate=cycle(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle ", i+1," win rate: ",win_rate)
    player1.save()
    