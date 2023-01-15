import logging
import argparse
import random
import quarto
import copy
from RL.QL_agent3 import QL_Agent3
from RL.RL_agent import RL_Agent
from montecarlo.montecarlo import MonteCarloPlayer
from main import RandomPlayer
from main import RiskyPlayer
from main import GeneticPlayer


def train(game, player0, player1, num_matches,cycles):
    win = 0
    draw = 0
    loss = 0
    player1.epsilon_decay=1-(1/(num_matches*cycles*0.25))
    print("beginning epsilon= ", player1.epsilon)
    for i in range(num_matches):
        
        game.reset()
        #print("-------- PARTITA ", i)
        if i%2==0:
            game.set_players((player0, player1)) 
        else:
            game.set_players((player1, player0)) 
        winner = game.run()
        player1.learn(winner)
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

def train_by_level(player1, level):
    agents_lrs={
        "random": 0.01,
        "risky": 0.2,
        "EA": 0.22,
        "montecarlo-50":0.3,
        "montecarlo-100":0.35,
        "montecarlo-200":0.4,
        "montecarlo-500":0.475,
        "montecarlo-1000":0.525,
        "montecarlo-2500":0.6
    }
    if level==1:
        print("LEVEL 1")
        print("First training: Random Player")
        player1.learning_rate=agents_lrs["random"]
        game=player1.get_game()
        player0=RandomPlayer(game)
        num_matches = 1000
        cycles=50
        for i in range(cycles):
            win_rate=train(game, player0,player1, num_matches, cycles) #player0 for testing, player1 for training
            print("cycle train ", i+1," win rate: ",win_rate)
        player1.save()
        """
        print("Second training. Risky Player")
        player1.learning_rate=agents_lrs["risky"]
        player1.epsilon=1
        game=player1.get_game()
        player0=RiskyPlayer(game)
        num_matches = 1
        cycles=10
        for i in range(cycles):
            win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
            print("cycle train ", i+1," win rate: ",win_rate)
        player1.save()
        """
        print("Third training: vs montecarlo")
        player1.learning_rate=agents_lrs["montecarlo-500"]
        player1.epsilon=1
        game=player1.get_game()
        player0=MonteCarloPlayer(game)
        num_matches = 100
        cycles=20
        for i in range(cycles):
            win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
            print("cycle train ", i+1," win rate: ",win_rate)
        player1.save()
        
    else:
        if level==2:
            print("LEVEL 2")   
            print("Second training: Risky Player")
            player1.learning_rate=agents_lrs["risky"]
            player1.epsilon=1
            game=player1.get_game()
            player0=RiskyPlayer(game)
            num_matches = 100
            cycles=10
            for i in range(cycles):
                win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
                print("cycle train ", i+1," win rate: ",win_rate)
            player1.save()
            print("Third training: vs montecarlo")
            player1.learning_rate=agents_lrs["montecarlo-500"]
            player1.epsilon=1
            game=player1.get_game()
            player0=MonteCarloPlayer(game)
            num_matches = 10
            cycles=10
            for i in range(cycles):
                win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
                print("cycle train ", i+1," win rate: ",win_rate)
            player1.save()
        else:
            #da modificare
            if level==3:
                print("LEVEL 3")    
                print("Third training: vs montecarlo")
                player1.learning_rate=agents_lrs["montecarlo-500"]
                player1.epsilon=1
                game=player1.get_game()
                player0=MonteCarloPlayer(game)
                num_matches = 10
                cycles=10
                for i in range(cycles):
                    win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
                    print("cycle train ", i+1," win rate: ",win_rate)
                player1.save()
                """
                print("Fourth training: vs itself")
                player1.learning_rate=player1.learning_rate+0.05 if win_rate>=0.5 else 0.1
                player1.epsilon=1
                game=player1.get_game()
                player0=RL_Agent(game,False,True)
                num_matches = 1000
                cycles=10
                for i in range(cycles):
                    win_rate=train(game, player0,player1, num_matches,cycles) #player0 for testing, player1 for training
                    print("cycle train ", i+1," win rate: ",win_rate)
                player1.save()
                """
        


if __name__ == '__main__':
    game = quarto.Quarto()
    training_agent=RL_Agent(game)
    level=1

    train_by_level(training_agent,level)

    print("Evaluation")
    game = quarto.Quarto()
    player0=RandomPlayer(game)
    player1=RL_Agent(game,False,True)
    num_matches = 1000
    cycles=20
    for i in range(cycles):
        win_rate=eval(game, player0,player1, num_matches) #player0 for testing, player1 for training
        print("cycle eval ", i+1," win rate: ",win_rate)
    