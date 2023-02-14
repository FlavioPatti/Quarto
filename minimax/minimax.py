import random
import quarto
import math
import copy
import numpy as np
import pickle
import sys

class MinmaxPlayer(quarto.Player):
    """Minimax player"""
    action_space = 256
    MY_TOURN = 1
    MINMAX_DEPTH = 1

    def __init__(self, quarto: quarto.Quarto, withRL=False):
        super().__init__(quarto)
        self.withRL=withRL
        self.current_game = quarto
        self.current_game._board = quarto._board
        self.piece_to_give = None
        self.pos_chosen = None
        if self.withRL==True:
            self.q = {}
            
            self.load_qtable()

    def policy(self, state,possActions):
        '''Policy
        This function takes a state and chooses the action for that state that will lead to the maximum reward'''
        # Highest reward -> Low exploration rate
        action_values = self.get_action_values(state, possActions)
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
    
    def get_action_values(self, state, possActions):
        '''
        returns the action value for each possible action of a certain state
        '''
        state=tuple(state)
        return self.q.get(state, np.zeros((self.action_space,2)))[possActions]

    def choose_piece(self):
        if self.withRL==True:
            if self.get_game().get_selected_piece()==-1:
                possActions = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
                state=[-1]*17
                current_action=self.policy(state, possActions)
                return current_action
        if self.current_game.get_selected_piece() == -1:
            return random.choice(range(15))

        return self.piece_to_give

    def place_piece(self):
        self.pos_chosen, self.piece_to_give = self.move()
        return self.pos_chosen

    def move(self):
        '''
         Returns position of selected piece and the piece selected for the opponent.
         Action is an integer number from 0 to 256 that represents both actions. 

        '''

        action = self.minmax_move()
        
        action_pos = action // 16
        action_piece = action % 16

        return  self.__action_to_pos(action_pos), action_piece
    
    def __action_to_pos(self, pos):
        '''
         "pos" is an integer from 0 to 16 that represents the position on the board, this function converts that number to coordinate
          and swaps them to fit with Quarto class in objects.py 
        '''
        x = pos//4  
        y = pos%4 
        return (y,x) 

    
    def __validActions(self, state):
        '''
         Returns the list of actions available from the current state

        '''
        available_pieces = list(set(range(16)) - set(state))
        if len(available_pieces) == 0:
            available_pieces = [state[16]]
        available_positions = list(filter(lambda x: state[x] == -1,range(16)))

        return  [16 * pos + piece for pos in available_positions for piece in available_pieces]
    
    def __state_to_avlState(self, state, sel_piece):
        '''
        From board and selected piece return the state used by this algorithm, a list of 17 elements
        where the first 16 correspond to the board and the last one corresponds to the piece selected by the opponent

        '''

        return list(np.concatenate((state.ravel(),np.array([sel_piece]))))

    def __tmpMove(self, ply):
        '''
        Temporary move used by minmax function

        '''
        action_pos = ply // 16
        action_piece = ply % 16

        return action_piece,  self.__action_to_pos(action_pos)
    
    def __unplace(self, game, x,y):
        '''
        Take away piece in coordinates (x, y). Returns true on success
        '''
        game._board[y, x] = -1
        game._Quarto__binary_board[y,
                            x][:] = np.nan
        return True

    def check_win(self, game, piece=-1):
        ''' Check if the player can win by placing the assigned piece. returns (x, y). If there is no winning move: returns (-1, -1)'''
        if piece >= 0:
            game.select(piece)
        # else: piece is already chosen, do nothing
        winning_x = -1
        winning_y = -1
        for x in range(game.BOARD_SIDE):
            for y in range(game.BOARD_SIDE):
                # try to place piece in every possible position, return the first that wins.
                if game.place(x, y):
                    # perform victory check
                    if game.check_winner() >= 0:
                        winning_x = x
                        winning_y = y
                        self.__unplace(game, x,y)
                        return winning_x, winning_y
                    self.__unplace(game, x, y)
        return winning_x, winning_y
    
    def from_move_to_action(self, x, y, piece = 0):
        action_pos = y*4+x
        action = action_pos*16 + piece
        return action

    def minmax_move(self):

        '''
            this function first looks to see if it can win by simply placing the given piece in one of the positions in the board,
            if it does not win it executes the minmax which returns the action with the largest reward. 
            If the reward is 0 check the RL table to see if there is a better action.
        '''
        
        game_copy=quarto.Quarto()
        game_copy._board=self.current_game.get_board_status()
        game_copy._Quarto__selected_piece_index=self.current_game.get_selected_piece()
        game_copy._current_player=self.current_game.get_current_player()
        game_copy._Quarto__binary_board=copy.deepcopy(self.current_game._Quarto__binary_board)
        game_copy.savePiece = self.current_game.get_selected_piece()

        x,y = self.check_win(game_copy)

        if (x,y) != (-1,-1):
            action = self.from_move_to_action(x,y)
            return action


        state = self.__state_to_avlState(game_copy._board, game_copy.get_selected_piece())
        
        self.minmaxPolicy(state)
                
        if self.withRL==True:
            losingMoves=[]
            action,reward=self.minmax(game_copy,losingMoves=losingMoves)
        else:
            action,reward=self.minmax(game_copy)
        #RL
        if self.withRL==True:
            if reward==1 or reward==0.5:
                return action
            all_pieces={ x for x in range(len(state)-1)}
            available_pieces=list(all_pieces - set(state))
            # To avoid bugs when you are about to make the last move that will lead to a draw
            if available_pieces==[]:
                available_pieces.append(0)
            
            available_positions=[]

            for i, o in enumerate(state):
                if o==-1:
                    available_positions.append(i)

            possActions = [
                16 * pos + piece for pos in available_positions for piece in available_pieces]
            possActions=list(set(possActions)-set(losingMoves))
            if possActions!=[]:
                current_action=self.policy(state,possActions)
            else:
                return losingMoves[0]

            return current_action
        return action
    
    def minmaxPolicy(self, state):
        '''
            Set the max depth of minmax based on state, the fewer pieces missing from the board 
            the greater the maximum depth.
        '''

        count = 0
        self.MINMAX_DEPTH = 1
        for i in state:
            if i != -1:
                count += 1
                if count == 3:
                    self.MINMAX_DEPTH = 2
                if count == 9:
                    self.MINMAX_DEPTH = 3
                if count == 11:
                    self.MINMAX_DEPTH = 4

    def __isDraw(self, game):
        state = self.__state_to_avlState(game._board, game.get_selected_piece())
        endgame = state.count(-1)==0

        if endgame:
            if game.check_winner() < 0:
                return True
            else:
                return False
        else:
            return False


    
    def __evaluate_move(self, game, myTourn):
        ''' Returns the score of the given state. '''

        if myTourn:
            # I just placed! Did I win?
            if  game.check_winner() >= 0:
                return 1

            elif self.__isDraw(game): # if it's a tie return 0.5
                return 0.5

            # if I didn't win, return 0
            return 0
        else:
            # opponent just placed. Did I lose?
            if game.check_winner() >= 0:
                return -1

            elif self.__isDraw(game): # if it's a tie return 0.5
                return 0.5

            # if I didn't win, return 0
            return 0
    

    def minmax(self, game, deep = 0, maximizingPlayer = True, alpha = -math.inf , beta = math.inf, losingMoves=[]): 

        '''
            Implementation of minmax with alpha-beta pruning
        '''

        val = self.__evaluate_move(game, deep%2)

        state = self.__state_to_avlState(game.get_board_status(), game.get_selected_piece())
        possible_moves = self.__validActions(state)
        

        if val != 0 or not possible_moves:
            return None, val

        evaluations = list()
        
        #deep pruning
        if deep >= self.MINMAX_DEPTH:
            return None, 0

        tmp = copy.deepcopy(game)

        if maximizingPlayer: # my tourn

            maxVal = -math.inf
            for ply in possible_moves:
                
                piece, (x,y) = self.__tmpMove(ply)
                tmp.place(x,y)
                tmp._Quarto__selected_piece_index = piece

                _ , val = self.minmax(tmp, deep+1, False, alpha, beta)

                evaluations.append((ply, val))
                if self.withRL==True:
                    if deep==0 and val==-1:
                        losingMoves.append(ply)

                maxVal = max(maxVal, val)
                alpha = max(alpha, maxVal)

                if beta < alpha:
                    break

                tmp._Quarto__selected_piece_index = game._Quarto__selected_piece_index
                self.__unplace(tmp, x,y)

            return max(evaluations, key=lambda k: k[1])
        
        else: 

            minVal = math.inf
            for ply in possible_moves:
                
                piece, (x,y) = self.__tmpMove(ply)
                tmp.place(x,y)
                tmp._Quarto__selected_piece_index = piece

                _ , val = self.minmax(tmp, deep+1, True, alpha, beta)

                evaluations.append((ply, val))

                minVal = min(minVal, val)
                beta = min(alpha, minVal)

                if beta < alpha:
                    break

                tmp._Quarto__selected_piece_index = game._Quarto__selected_piece_index
                self.__unplace(tmp, x,y)
                
            return min(evaluations, key=lambda k: k[1])

    def load_qtable(self):
        with open('player.bin', 'rb') as f:
            self.q=pickle.load(f)
