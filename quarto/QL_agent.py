import numpy as np
import quarto
import random
import copy

class QL_Agent(quarto.Player):
    action_space = 256
    q = {}
    previous_state = previous_action = None
    WIN_REWARD, LOSS_REWARD =   100, -100 #1, -1

    def __init__(self, quarto:quarto.Quarto, k = None, epsilon = 1, epsilon_decay=0.999, min_epsilon=0.1, learning_rate = 0.1, discount_factor = 0.9):
        self.__quarto=quarto
        self.number_rewards=0 #FOR DEBUGGING
        #q is a function f: State x Action -> R and is internally represented as a Map.

        #alpha is the learning rate and determines to what extent the newly acquired 
        #information will override the old information

        #gamma is the discount rate and determines the importance of future rewards

        #epsilon serves as the exploration rate and determines the probability 
        #that the agent, in the learning process, will randomly select an action

        self.epsilon = epsilon   # epsilon   -> the higher epsilon,  the more random I act
        self.epsilon_decay=epsilon_decay
        self.min_epsilon=0.1                      
        self.learning_rate = learning_rate          # alpha     -> the higher alpha,    the more I replace "q"
        self.discount_factor = discount_factor      # gamma     -> the higher gamma,    the more I favor long-term reward
        # as I get closer and closer to the deadline, my preference for near-term reward should increase, 
        # which means my gamma should decrease.

    def choose_piece(self):
        if self.previous_action==None:
            return int(random.random(15))
        return self.previous_action % 16

    def place_piece(self):
        #the state consists in a list of 17 elements (the 16 values of the board + the piece chosen by the opponent)
        board=self.__quarto.get_board_status()
        state=[]
        for yp in board:
            for xp in yp:
                state.append(xp)
        state.append(self.__quarto.get_selected_piece())
        #print(state)
        current_action=self.update_q(state)
        pos=current_action//16
        y=pos//4
        x=pos%4
        #print(x , "-" , y)
        return (x,y)

    def makeKey(self, state):
        possActions = list(self.getActions(state))
        someAction = possActions[0]

        # generating Q Table
        if (tuple(state), someAction) not in self.q:
            for i in possActions:
                self.q[(tuple(state), i)] = np.random.uniform(0.0, 0.01)

    def is_terminal(self):
        '''returns True if the state is terminal'''
        return self.__quarto.check_finished() or self.__quarto.check_winner()>=0

    def getActions(self, state):
        '''returns a list of possible actions for a given state'''
        if self.is_terminal():
            return [None]
        all_pieces={ x for x in range(len(state)-1)}
        available_pieces=all_pieces - set(state)
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
        possActions = list(self.getActions(state))

        if np.random.random() < self.epsilon:
            # Random -> High exploration rate
            chosen_action_idx = np.random.randint(0, len(possActions))
            return possActions[chosen_action_idx]  
        else:
            # Highest reward -> Low exploration rate
            q_values = [self.q[(tuple(state),i)] for i in possActions]
            return possActions[np.argmax(q_values)]
    # Updates the Q-table as specified by the standard Q-learning algorithm
    def update_q(self, state):
      
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
        