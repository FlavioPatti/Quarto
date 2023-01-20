import numpy as np
import quarto
import random
import copy
import pickle

class RL_Agent(quarto.Player):
    action_space = 256
    WIN_REWARD, LOSS_REWARD =   1000, -0.1 #1, -1

    def __init__(self, quarto:quarto.Quarto, train_mode=True, pretrained=False, epsilon = 1, epsilon_decay=0.9995, min_epsilon=0.01, learning_rate = 1, discount_factor=0.25): #0.15):
        super().__init__(quarto)
        self.train_mode=train_mode
        self.pretrained=pretrained
        #self.number_rewards=0 #FOR DEBUGGING
        #q is a function f: State x Action -> R and is internally represented as a Map.

        #alpha is the learning rate and determines to what extent the newly acquired 
        #information will override the old information

        #gamma is the discount rate and determines the importance of future rewards

        #epsilon serves as the exploration rate and determines the probability 
        #that the agent, in the learning process, will randomly select an action
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
        # as I get closer and closer to the deadline, my preference for near-term reward should increase, 
        # which means my gamma should decrease.

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
        #print(state)
        if self.train_mode:
            current_action=self.update_state_history(state)
        else:
            current_action=self.policy(state)
            self.action= current_action

        pos=current_action//16
        y=pos//4
        x=pos%4
        #print(x , "-" , y)
        return (x,y)

    def make_and_get_action_values(self, state, possActions):
        state=tuple(state)
        if self.train_mode==True:
            return self.q.setdefault(state, np.zeros(self.action_space))[possActions]
        return self.q.get(state, np.zeros(self.action_space))[possActions]

    def is_terminal(self):
        '''returns True if the state is terminal'''
        return self.get_game().check_finished() or self.get_game().check_winner()>=0

    def getActions(self, state):
        '''returns a list of possible actions for a given state'''
        #if self.is_terminal():
        #    return [None]
        if state.count(-1)==17:
            return [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        all_pieces={ x for x in range(len(state)-1)}
        available_pieces=list(all_pieces - set(state))
        # per evitare bug quando si sta per fare l'ultima mossa che porterà a un draw!
        if available_pieces==[]:
            available_pieces.append(0)
        available_positions=[]
        #print("available pieces: ", available_pieces)
        for i, o in enumerate(state):
            if o==-1:
                available_positions.append(i)
        #print("available positions: ", available_positions)
        possible_actions = [
            16 * pos + piece for pos in available_positions for piece in available_pieces]
        #print("possible actions: ", possible_actions)
        return possible_actions


    def policy(self, state):
        '''Policy
        This function takes a state and chooses the action for that state that will lead to the maximum reward'''
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
                if game.check_winner()==game.get_current_player:
                    return pos*16
                game._board[y, x] = -1
                game._Quarto__binary_board[y,x][:] = np.nan
        possActions = self.getActions(state)
        if np.random.random() < self.epsilon and self.train_mode==True:
            # Random -> High exploration rate
            self.make_and_get_action_values(state, possActions)
            chosen_action_idx = np.random.randint(0, len(possActions))
            return possActions[chosen_action_idx]  
        else:
            # Highest reward -> Low exploration rate
            action_values = self.make_and_get_action_values(state, possActions)
            return possActions[np.argmax(action_values)]
   
    # Updates the Q-table as specified by the standard Q-learning algorithm
    def update_state_history(self, state):
    
        current_action = self.policy(state)
        self.state_history.append((state, current_action))

        return current_action

    def learn(self, winner):

        if winner==1:
            target=self.WIN_REWARD
        elif winner==0:
            target=self.LOSS_REWARD  
        else:
            target=0
        for prev_state, prev_action in reversed(self.state_history):
            reward=self.q[tuple(prev_state)][prev_action]
            self.q[tuple(prev_state)][prev_action]+= self.learning_rate * (target - self.q[tuple(prev_state)][prev_action])
            target +=reward
            target*=self.discount_factor
        self.epsilon=max(self.epsilon*self.epsilon_decay,self.min_epsilon)
        self.state_history = []
        


    def save(self):
        # Save the q-table on the disk for future use 
        with open('player.bin', 'wb') as f:
            pickle.dump(dict(self.q), f, protocol=4)
      
            

    def load(self):
        with open('player.bin', 'rb') as f:
            self.q=pickle.load(f)