import logging
import argparse
import random
import quarto
import copy
from RL.QL_agent3 import QL_Agent3
from RL.RL_agent import RL_Agent
from RL.QL_agent4 import QL_Agent4
from montecarlo.montecarlo import MonteCarloPlayer
from main import RandomPlayer
from main import RiskyPlayer
from main import GeneticPlayer
from minimax.minimax import MinimaxPlayer


def train(game, player0, player1, num_matches,cycles):
    win = 0
    draw = 0
    loss = 0
    player1.epsilon_decay=1-(1/(num_matches*cycles*0.5)) #0.25
    print("beginning epsilon= ", player1.epsilon)
    for i in range(num_matches):
        
        game.reset()
        #print("-------- PARTITA ", i+1)
        if i%2==0:
            game.set_players((player0, player1))
            winner = game.run()
            player1.learn(winner) 
            if winner == 1:
                win = win + 1
            elif winner == -1:
                draw = draw + 1
            else:
                loss = loss + 1
        else:
            game.set_players((player1, player0))
            winner = game.run()
            player1.learn(1-winner)
            if winner == 1:
                loss = loss + 1
            elif winner == -1:
                draw = draw + 1
            else:
                win = win + 1 
            
        #print("Winner is: ", winner)
        #win_rate = win / (win+loss)
        #draw_rate = draw / (i+1)
        #loss_rate = loss / (win+loss)
        #if winner == 1 or winner == 0:
            #print(f"Match # {i} -> Winner -> {type(game._Quarto__players[winner]).__name__} -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
        #else:
            #print(f"Match # {i} -> Winner -> Both -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
    #counter_r=0
    #for v in player1.q.values():
    #    if  v>1 or v<-1 :
    #        counter_r+=1
    #print("count of cool rewards: ", counter_r)       
    #win_rate = win / num_matches
    win_rate= win / (win+loss)
    return win_rate

def eval(game, player0, player1, num_matches):
    win = 0
    draw = 0
    loss = 0
    for i in range(num_matches):
        
        game.reset()
        #print("-------- PARTITA ", i)

        if i%2==0:
            game.set_players((player0, player1)) 
        else:
            game.set_players((player1, player0))
        winner = game.run()
        if i%2==0:
            if winner == 1:
                win = win + 1
            elif winner == -1:
                draw = draw + 1
            else:
                loss = loss + 1
        else:
            if winner == 1:
                loss = loss + 1
            elif winner == -1:
                draw = draw + 1
            else:
                win = win + 1
        #print("Winner is: ", winner)
        #win_rate = win / (win+loss)
        #draw_rate = draw / (i+1)
        #loss_rate = loss / (win+loss)  1
        #if winner == 1 or winner == 0:
            #print(f"Match # {i} -> Winner -> {type(game._Quarto__players[winner]).__name__} -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
        #else:
            #print(f"Match # {i} -> Winner -> Both -> Win rate = {win_rate}, Draw rate = {draw_rate} Loss rate = {loss_rate}")
    #counter_r=0
    #for v in player1.q.values():
    #    if  v>1 or v<-1 :
    #        counter_r+=1
    #print("count of cool rewards: ", counter_r)       
    #win_rate = win / num_matches
    win_rate= win / (win+loss)
    return win_rate

def train_by_level(player1, levels):
    agents_lrs={
        "minimax-0": 0.1,
        #"random": 0.01,
        "risky": 0.1,
        #"EA": 0.12,
        #"montecarlo-50":0.3,
        #"montecarlo-100":0.35,
        #"montecarlo-200":0.4,
        #"montecarlo-500":0.475,
        #"montecarlo-1000":0.525,
        #"montecarlo-2500":0.6,
        "minimax-4":1
    }
    one=False
    two=False
    three=False
    for level in levels:
        if level==1:
            one=True
        if level==2:
            two=True
        if level==3:
            three=True
    if one:

        print("LEVEL1: training vs Risky Player")
        player1.learning_rate=agents_lrs["risky"]
        player1.epsilon=1
        game=player1.get_game()
        player0=RiskyPlayer(game)
        num_matches = 1000
        cycles=50
        for i in range(cycles):
            win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
            print("cycle train ", i+1," win rate: ",win_rate*100,"%")
        player1.save()   
        
    if two:
        print("LEVEL2: training vs minimax-4")
        player1.learning_rate=agents_lrs["minimax-4"]
        player1.epsilon=1
        game=player1.get_game()
        player0=MinimaxPlayer(game)
        player0.MINMAX_DEPTH=4
        assert player0.MINMAX_DEPTH==4
        num_matches = 1000
        cycles=50
        for i in range(cycles):
            win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
            print("cycle train ", i+1," win rate: ",win_rate*100,"%")
            player1.save()

    if three:
        print("LEVEL3: training vs itself")
        player1.learning_rate=player1.learning_rate+0.05 #if win_rate>=0.5 else 0.1
        player1.epsilon=1
        game=player1.get_game()
        player0=RL_Agent(game,False,True)
        num_matches = 1000
        cycles=10
        for i in range(cycles):
            win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
            print("cycle train ", i+1," win rate: ",win_rate*100,"%")
        player1.save()
        


if __name__ == '__main__':
    
    game = quarto.Quarto()
    training_agent=RL_Agent(game)
    assert training_agent.discount_factor==0.25
    levels=[2]
    train_by_level(training_agent,levels)
    #print(training_agent.q)
    #for key,value in training_agent.q.items():
    #    for reward in value:
    #        if reward[0]>0:
    #            #print(key,"-> reward0-> ",value)
    #            break
    #state=[-1]*17
    #print(training_agent.q[tuple(state)])
    
    print("Evaluation vs Random")
    game = quarto.Quarto()
    player0=RandomPlayer(game)
    player1=RL_Agent(game,False,True)
    num_matches = 100
    cycles=20
    for i in range(cycles):
        win_rate=eval(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle eval ", i+1," win rate: ",win_rate*100,"%")
    
    print("Evaluation vs Risky")
    game = quarto.Quarto()
    player0=RiskyPlayer(game)
    player1=RL_Agent(game,False,True)
    num_matches = 100
    cycles=20
    for i in range(cycles):
        win_rate=eval(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle eval ", i+1," win rate: ",win_rate*100,"%")
    
    print("Evaluation vs minimax-4")
    game = quarto.Quarto()
    player0=MinimaxPlayer(game)
    player0.MINMAX_DEPTH=4
    assert player0.MINMAX_DEPTH==4
    player1=RL_Agent(game,False,True)
    num_matches = 100
    cycles=20
    for i in range(cycles):
        win_rate=eval(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle eval ", i+1," win rate: ",win_rate*100,"%")
    """
    print("Evaluation vs Montecarlo50")
    game = quarto.Quarto()
    player0=MonteCarloPlayer(game)
    assert player0.num_iteration==50
    player1=QL_Agent3(game,False,True)
    num_matches = 100
    cycles=20
    for i in range(cycles):
        win_rate=eval(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle eval ", i+1," win rate: ",win_rate*100,"%")
    """
    """
    game = quarto.Quarto()
    player1=RL_Agent(game,False,True)

    for key,value in player1.q.items():
        for reward in value:
            if reward>0:
                print(key,"->",value)
                break
    state=[-1]*17
    print(player1.q[tuple(state)])
    """
    