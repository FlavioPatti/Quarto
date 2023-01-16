import random
from copy import deepcopy
import numpy as np
from collections import defaultdict
import sys, os
sys.path.append(os.path.abspath(os.path.join('.')))
import quarto

class Q(quarto.Quarto):
    def __init__(self, status) -> None:
        super().__init__() 
        self._board = status
        self._Quarto__binary_board = self.build_binary_map(status)

    def build_binary_map(self, status):
        binary_board = np.full(shape=(status.shape[0], status.shape[0], 4), fill_value=np.nan)
        for piece, pos in [(r,(idxc, idxr)) for idxr, row in enumerate(status) for idxc, r in enumerate(row) if r != -1]:
            array = np.zeros((status.shape[0]))
            for pow in range(status.shape[0]):
                array[-1-pow] = piece % 2
                piece = piece // 2
            binary_board[pos][:] = array
        return binary_board


class Node():
    def __init__(self, status, sel, selected, losing_moves=set()):
        self.n = 0
        self.parent = None
        self.status = status 
        self.sel = sel 
        self.children = []
        self.pos_moves = self.possible_moves(sel, losing_moves)                                                                                               
        self.pos_next_moves = self.possible_moves(not sel)
        self._results = defaultdict(int)                     
        self.selected = selected
        self.BOARD_SIDE = 4

    def add_Child(self, child):
        self.children.append(child)

    def set_Parent(self, parent):
        self.parent = parent

    def expand(self):
        status_tmp = deepcopy(self.status)
        game_tmp = Q(status_tmp)
        if not self.sel:                                
            action = self.pos_moves.pop(random.randint(0, len(self.pos_moves)-1))        
            game_tmp.select(action)                                                 
            piece_ok = False
            while not piece_ok:
                x, y = self.place_random_piece()                   
                piece_ok = game_tmp.place(x, y)
        else:
            piece_ok = False
            while not piece_ok:
                if self.selected != None:
                    piece_ok = game_tmp.select(self.selected)
                else:
                    piece_ok = game_tmp.select(self.choose_random_piece())   
            action = self.pos_moves.pop(random.randint(0, len(self.pos_moves)-1)) 
            game_tmp.place(*action) 
        child_node = Node(status_tmp, not self.sel, None)
        child_node.set_Parent(self)
        self.children.append([child_node, action])
        return child_node 


    def balanced_expand(self):
        status_tmp = deepcopy(self.status)
        game_tmp = Q(status_tmp)
        if not self.sel:                                    
            action = self.pos_moves.pop(random.randint(0, len(self.pos_moves)-1))        
            game_tmp.select(action)                                                 
            x, y = self.pos_next_moves.pop(random.randint(0, len(self.pos_next_moves)-1))                  
            game_tmp.place(x, y)
        else:
            if self.selected != None:
                game_tmp.select(self.selected)
            else:
                game_tmp.select(self.pos_next_moves.pop(random.randint(0, len(self.pos_next_moves)-1)) )   
            action = self.pos_moves.pop(random.randint(0, len(self.pos_moves)-1)) 
            game_tmp.place(*action) 
        child_node = Node(status_tmp, not self.sel, None)
        child_node.set_Parent(self)
        self.children.append([child_node, action])    
        return child_node            

    def is_terminal_node(self):
        game = Q(self.status)
        if game.check_winner() >= 0 or game.check_finished():
            return True
        else:
            return False

    def is_fully_expanded(self):
        return len(self.pos_moves) == 0

    def possible_moves(self, sel, losing_moves=set()):
        state = self.status
        if not sel:
            pos_moves = list(set(m for m in range(16)) - set(r for row in state for r in row if r != -1) - losing_moves)
            if len(pos_moves):
                return pos_moves
            else:
                return list(losing_moves)
        else:
            return [(idxc, idxr) for idxr, row in enumerate(state) for idxc, r in enumerate(row) if r == -1]


    def rollout(self):
        sel = self.sel
        status_tmp = deepcopy(self.status)
        game = Q(status_tmp)
        winner = -1
        if sel:         # vuol dire che lui ha posizionato (tocca a lui scegliere)
            winner = game.check_winner()
            current_player = 1
        else:            # vuol dire che ho posizionato (tocca a me scegliere)
            winner = game.check_winner()
            current_player = 0
        while winner < 0 and not game.check_finished():  
            piece_ok = False
            while not piece_ok:
                piece_ok = game.select(self.choose_random_piece())   
            piece_ok = False
            current_player = (current_player + 1) % game.MAX_PLAYERS
            while not piece_ok:
                x, y = self.place_random_piece()                 
                piece_ok = game.place(x, y) 
            winner = game.check_winner()            
        self.my_turn = current_player
        if winner > -1:
            return current_player
        else:
            return -1

    def backpropagate(self, result):
        self.n += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def best_child(self, c_param=1.4):
        choices_weights = [
            (c[0].q() / c[0].n) + c_param * np.sqrt((2 * np.log(self.n) / c[0].n))
            for c in self.children  
        ]
        return self.children[np.argmax(choices_weights)]

    def q(self):
        wins = self._results[0]
        loses = self._results[1]
        return wins

    def choose_random_piece(self) -> int:
        return random.randint(0, 15) 
           

    def place_random_piece(self) -> tuple[int, int]:
        return random.randint(0, 3), random.randint(0, 3) 