import numpy as np
import quarto
import random
import copy
import pickle
import math
import sys
'''Implementation of a custom RL with some elements that are similar to a minmax'''
class RL_Agent2(quarto.Player):
    '''In our case, to compress informations, the action that place a piece and the action that choose a piece for the opponent are unified,
    So the upper bound of the number of the possible actions will be 16(number of places)*16(number of pieces). That's the reason of an action space of 256'''
    action_space = 256

    def __init__(self, quarto:quarto.Quarto, train_mode=True, pretrained=False):
        super().__init__(quarto)
        self.train_mode=train_mode
        self.pretrained=pretrained
        
        self.q = {}
        if self.train_mode:
            self.state_history = []
        else:
            self.action=None

        if self.pretrained==True:
            self.load() 


    def choose_piece(self):
        if self.get_game().get_selected_piece()==-1:
            state=[-1]*17
            current_action=self.policy(state)
            if self.train_mode:
                self.state_history.append((state, current_action))
            return current_action
        if self.train_mode:
            return self.state_history[-1][1] % 16
        else:
            return self.action %16

    def place_piece(self):
        #the state consists in a list of 17 elements (the 16 values of the board + the piece chosen by the opponent)
        board=self.get_game().get_board_status()
        state=[]
        for yp in board:
            for xp in yp:
                state.append(xp)
        state.append(self.get_game().get_selected_piece())
        if self.train_mode:
            current_action=self.update_state_history(state)
        else:
            current_action=self.policy(state)
            self.action= current_action

        pos=current_action//16
        y=pos//4
        x=pos%4
        return (x,y)

    def make_and_get_action_values(self, state, possActions):
        '''If I'm in training phase if I've never visited a state, I create it initializing the rewards to couples of 0s
        If i'm in test phase I take the rewards of the actions of a state, and if that state isn't in the q-table, I return a list of couples of 0s as reward'''
        state=tuple(state)
        def_list=[]
        if self.train_mode==True:
            return self.q.setdefault(state, np.zeros((self.action_space,2)))[possActions]
        return self.q.get(state, np.zeros((self.action_space,2)))[possActions]

    def is_terminal(self):
        '''CURRENTLY UNUSED
        returns True if the state is terminal'''
        return self.get_game().check_finished() or self.get_game().check_winner()>=0

    def getActions(self, state):
        '''returns a list of possible actions for a given state'''
        count=state.count(-1)
        '''Optimization to explore less states
        Basing on simmetries, if I begin for first, any piece I choose is the same '''
        if count==17:
            return [0]#,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] 
        
        all_pieces={ x for x in range(len(state)-1)}
        available_pieces=list(all_pieces - set(state))
        #To avoid a bug when I'm about to do the last move that will lead to a draw
        if available_pieces==[]:
            available_pieces.append(0)
        '''Optimization to explore less states
        Basing on simmetries, if I begin for second, any place I choose to put the piece chosen by my opponent
        is equivalent to putting the piece in the position 0 or 1'''
        if count==16:
            available_positions=[0,1]
        else:
            available_positions=[]
            for i, o in enumerate(state):
                if o==-1:
                    available_positions.append(i)
        possible_actions = [
            16 * pos + piece for pos in available_positions for piece in available_pieces]
        return possible_actions


    def policy(self, state):
        '''Policy
        This function takes a state and chooses the action for that state that will lead to the maximum reward'''
        possActions = self.getActions(state)
        if self.train_mode==True:
            action_values = self.make_and_get_action_values(state, possActions)
            '''Optimization
            If an action that I can do from a state can make me win, I choose that, so I avoid exploring unuseful states'''
            if self.get_game().get_selected_piece()!=-1:
                game=quarto.Quarto()
                game._board=self.get_game().get_board_status()
                game._Quarto__selected_piece_index=self.get_game().get_selected_piece()
                game._current_player=self.get_game().get_current_player()
                game._Quarto__binary_board=copy.deepcopy(self.get_game()._Quarto__binary_board)
                available_positions=[]
                #print("available pieces: ", available_pieces)
                for i, o in enumerate(state):
                    if o==-1:
                        available_positions.append(i)
                for pos in available_positions:
                    y=pos//4
                    x=pos%4
                    game.place(x, y)
                    if game.check_winner()==game.get_current_player():
                        all_pieces={ x for x in range(len(state)-1)}
                        available_pieces=list(all_pieces - set(state))
                        if available_pieces==[]:
                            available_pieces.append(0)
                        return pos*16+available_pieces[0]
                    game._board[y, x] = -1
                    game._Quarto__binary_board[y,x][:] = np.nan
        
        
            for i,o in enumerate(action_values):
                if o[1]==0:
                    return possActions[i]
            ind=random.randint(0,len(possActions)-1)
            return possActions[ind]
        else:
            
            action_values = self.make_and_get_action_values(state, possActions)
            ind=-1
            max_reward=sys.float_info.min
            for i,o in enumerate(action_values):
                if o[0]==0 or o[1]==0:
                    continue
                rew=o[0]/o[1]
                if rew>max_reward:
                    max_reward=rew
                    ind=i
            if ind==-1:
                ind=random.randint(0,len(possActions)-1)
                return possActions[ind]
            else:
                return possActions[ind]
            
        
      
     
    def update_state_history(self, state):
        '''Choose the action and updates the state hystory'''
        current_action = self.policy(state)
        self.state_history.append((state, current_action))

        return current_action

    def learn(self, winner):
        """Called only at the end of a match and only for training.
        Spread the rewards of the final states"""
        prev_state, prev_action =self.state_history[-1]
        if self.q[tuple(prev_state)][prev_action][1]==0:
          
            for prev_state, prev_action in reversed(self.state_history):
                if winner==1:
                    self.q[tuple(prev_state)][prev_action][0]+=1 
                    self.q[tuple(prev_state)][prev_action][1]+=1 
                elif winner==0:
                    self.q[tuple(prev_state)][prev_action][1]+=1
                else:
                    self.q[tuple(prev_state)][prev_action][0]+=0.1
                    self.q[tuple(prev_state)][prev_action][1]+=1
                    
        self.state_history = []
        


    def save(self):
        '''Save the q-table on the disk for future use'''
        with open('player.bin', 'wb') as f:
            pickle.dump(dict(self.q), f, protocol=4)
      
            

    def load(self):
        '''load the q-table already saved if I don't have to train from scratch'''
        with open('player.bin', 'rb') as f:
            self.q=pickle.load(f)