import numpy as np
import quarto
import random
import copy
import pickle
'''The same QL_Agent but with a state_history instead of a previous state and action.
in this way i can update all the previous states when i know if I won or losed, 
not only the previuos'''
class QL_Agent2(quarto.Player):
    '''In our case, to compress informations, the action that place a piece and the action that choose a piece for the opponent are unified,
    So the upper bound of the number of the possible actions will be 16(number of places)*16(number of pieces). That's the reason of an action space of 256'''
    action_space = 256
    WIN_REWARD, LOSS_REWARD, DRAW_REWARD =   10, -10, 1 #1, -1

    def __init__(self, quarto:quarto.Quarto, train_mode=True, pretrained=False, epsilon = 1, epsilon_decay=0.9998, min_epsilon=0.1, learning_rate = 0.25, discount_factor = 0.25):
        super().__init__(quarto)
        self.train_mode=train_mode
        self.pretrained=pretrained
       
        self.q = {}
        if self.train_mode:
            self.state_history = []
        else:
            self.action=None
        self.epsilon = epsilon   # epsilon   -> the higher epsilon,  the more random I act
        self.epsilon_decay=epsilon_decay
        self.min_epsilon=min_epsilon                      
        self.learning_rate = learning_rate          # alpha     -> the higher alpha,    the more I replace "q"
        self.discount_factor = discount_factor # gamma     -> the higher gamma,    the more I favor long-term reward
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
        '''If I'm in training phase if I've never visited a state, I create it initializing the rewards to 0
        If i'm in test phase I take the rewards of the actions of a state, and if that state isn't in the q-table, I return a list of 0s as reward'''
        state=tuple(state)
        if self.train_mode==True:
            return self.q.setdefault(state, np.zeros(self.action_space))[possActions]
        return self.q.get(state, np.zeros(self.action_space))[possActions]

    def is_terminal(self):
        '''CURRENTLY UNUSED
        returns True if the state is terminal'''
        return self.get_game().check_finished() or self.get_game().check_winner()>=0

    def getActions(self, state):
        '''returns a list of possible actions for a given state'''
        if state.count(-1)==17:
            return [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

        all_pieces={ x for x in range(len(state)-1)}
        available_pieces=list(all_pieces - set(state))
        #To avoid a bug when I'm about to do the last move that will lead to a draw
        if available_pieces==[]:
            available_pieces.append(0)
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
        action_values = self.make_and_get_action_values(state, possActions)
        '''Optimization
            If an action that I can do from a state can make me win, I choose that, so I avoid exploring unuseful states'''
        if self.train_mode==True and self.get_game().get_selected_piece()!=-1:
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

        
        if np.random.random() < self.epsilon and self.train_mode==True:
            # Random -> High exploration rate
            chosen_action_idx = np.random.randint(0, len(possActions))
            return possActions[chosen_action_idx]  

        # Highest reward -> Low exploration rate
        return possActions[np.argmax(action_values)]
    

    def update_state_history(self, state):
        '''Choose the action and updates the state hystory'''
        current_action = self.policy(state)
        self.state_history.append((state, current_action))

        return current_action

    def learn(self,winner):
        """Called only at the end of a match and only for training.
        Calles update_q and updates epsilon"""
        self.update_q(winner)
        self.epsilon=max(self.epsilon*self.epsilon_decay,self.min_epsilon)
        
    def update_q(self, winner=None):
            '''Called by learn at the end of a match
            Updates the Q-table as specified by the standard Q-learning algorithm but then spread information to all the previous states'''
            state, action =self.state_history.pop()
            if self.q[tuple(state)][action]==0:
                if winner==1:
                    reward=self.WIN_REWARD
            
                elif winner==0:
                    reward=self.LOSS_REWARD
                else:
                    reward=self.DRAW_REWARD

                self.q[tuple(state)][action] += \
                    self.learning_rate * (reward - \
                        self.q[tuple(state)][action])
                possibleActions=self.getActions(state)
                action_values = self.make_and_get_action_values(state, possibleActions)
                maxQ = max(action_values)

                for previous_state, previous_action in reversed(self.state_history):  
                    self.q[tuple(previous_state)][previous_action] += \
                        self.learning_rate * (reward + self.discount_factor * maxQ - \
                            self.q[tuple(previous_state)][previous_action])
                    reward=self.q[tuple(previous_state)][previous_action]
                    possibleActions=self.getActions(previous_state)
                    action_values = self.make_and_get_action_values(previous_state, possibleActions)
                    maxQ = max(action_values)
                self.state_history = []

    def save(self):
        '''Save the q-table on the disk for future use''' 
        with open('player.bin', 'wb') as f:
            pickle.dump(dict(self.q), f, protocol=4)
      
            

    def load(self):
        '''load the q-table already saved if I don't have to train from scratch'''
        with open('player.bin', 'rb') as f:
            self.q=pickle.load(f)