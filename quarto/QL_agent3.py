import numpy as np
import quarto
import random
import copy
import pickle

class QL_Agent3(quarto.Player):
    action_space = 256
    WIN_REWARD, LOSS_REWARD =   100, -100 #1, -1

    def __init__(self, quarto:quarto.Quarto, train_mode=True, pretrained=False, epsilon = 1, epsilon_decay=0.9998, min_epsilon=0.1, learning_rate = 1, discount_factor = 0.9):
        super().__init__(quarto)
        #self.number_rewards=0 #FOR DEBUGGING
        #q is a function f: State x Action -> R and is internally represented as a Map.

        #alpha is the learning rate and determines to what extent the newly acquired 
        #information will override the old information

        #gamma is the discount rate and determines the importance of future rewards

        #epsilon serves as the exploration rate and determines the probability 
        #that the agent, in the learning process, will randomly select an action
        self.q = {}
        self.previous_state = None
        self.previous_action= None
        self.train_mode=train_mode
        self.pretrained=pretrained
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
            self.previous_state = None
            self.previous_action=None

        if self.previous_action==None:
            return random.randint(0,15)
        return self.previous_action % 16

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
            current_action=self.update_q(state)
        else:
            current_action=self.policy(state)
            self.previous_state, self.previous_action = state, current_action

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
        possActions = self.getActions(state)

        if np.random.random() < self.epsilon and self.train_mode==True:
            # Random -> High exploration rate
            chosen_action_idx = np.random.randint(0, len(possActions))
            return possActions[chosen_action_idx]  
        else:
            # Highest reward -> Low exploration rate
            action_values = self.make_and_get_action_values(state, possActions)
            return possActions[np.argmax(action_values)]
    """
    # Updates the Q-table as specified by the standard Q-learning algorithm
    def update_q(self, state, winner=None):
        if winner is not None:
            current_action = self.previous_state = self.previous_action = None
        else:
      
            self.makeKey(state)
            current_action = self.policy(state)

            if self.previous_action is not None:
                reward=0
                quarto_bis=copy.deepcopy(self.__quarto)
                pos=current_action//16
                y=pos//4
                x=pos%4
                quarto_bis.place(x,y)
                if quarto_bis.check_winner()>-1:
                    reward = self.WIN_REWARD
                else:
                    board=quarto_bis.get_board_status()
                    for yi, yp in enumerate(board):
                        for xi, xp in enumerate(yp):
                            quarto_bis.select(current_action % 16)
                            if xp==-1:
                                quarto_bis.place(xi,yi)
                                if quarto_bis.check_winner()>-1:
                                    reward = self.LOSS_REWARD
                                    break
                                quarto_bis.select(-1)
                                quarto_bis.place(xi,yi)

                print(reward)
                self.number_rewards+=1
                maxQ = max(self.q[(tuple(state), a)] for a in self.getActions(state))
                self.q[(tuple(self.previous_state), self.previous_action)] += \
                    self.learning_rate * (reward + self.discount_factor * maxQ - \
                        self.q[(tuple(self.previous_state), self.previous_action)])

            self.previous_state, self.previous_action = tuple(state), current_action
        return current_action
        
    """
    # Updates the Q-table as specified by the standard Q-learning algorithm
    def update_q(self, state, winner=None):
        reward=0
        #print("winner is: ", winner)
        
        if winner==1:
            reward=self.WIN_REWARD
            self.q[tuple(self.previous_state)][self.previous_action] += \
                    self.learning_rate * (reward  - self.q[tuple(self.previous_state)][self.previous_action])
            current_action = self.previous_state = self.previous_action = None
        elif winner==0:
            reward=self.LOSS_REWARD
            possibleActions=self.getActions(state)
            action_values = self.make_and_get_action_values(state, possibleActions)
            maxQ = max(action_values)
            self.q[tuple(self.previous_state)][self.previous_action] += \
                self.learning_rate * (reward + self.discount_factor * maxQ - \
                    self.q[tuple(self.previous_state)][self.previous_action])
            #print("final loss reward: ", self.q[(tuple(self.previous_state), self.previous_action)])
            current_action = self.previous_state = self.previous_action = None
        elif winner==-1:
            self.q[tuple(self.previous_state)][self.previous_action] += \
                    self.learning_rate * (reward  - self.q[tuple(self.previous_state)][self.previous_action])
            current_action = self.previous_state = self.previous_action = None
            
        else:
      
            current_action = self.policy(state)

            if self.previous_action is not None:

                #self.number_rewards+=1
                possibleActions=self.getActions(state)
                action_values = self.make_and_get_action_values(state, possibleActions)
                maxQ = max(action_values)
                self.q.setdefault(tuple(self.previous_state), np.zeros(self.action_space))
                self.q[tuple(self.previous_state)][self.previous_action] += \
                    self.learning_rate * (reward + self.discount_factor * maxQ - \
                        self.q[tuple(self.previous_state)][self.previous_action])

            self.previous_state, self.previous_action = state, current_action
        #print(reward)
        return current_action

    def learn(self,winner):
        self.update_q(self.previous_state, winner)
        self.epsilon=max(self.epsilon*self.epsilon_decay,self.min_epsilon)
        

    def save(self):
        # Save the q-table on the disk for future use 
        with open('player.bin', 'wb') as f:
            pickle.dump(dict(self.q), f, protocol=4)
      
            

    def load(self):
        with open('player.bin', 'rb') as f:
            self.q=pickle.load(f)
                