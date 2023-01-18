from copy import deepcopy 
import logging
import sys, os
sys.path.append(os.path.abspath(os.path.join('.')))
sys.path.append(os.path.dirname(__file__))
from node import Node, Q
import quarto
import time


class MonteCarloPlayer(quarto.Player):
    def __init__(self, quarto: quarto.Quarto, node=None) -> None:
        super().__init__(quarto) 
        self.root = node
        self.available_seconds = None
        self.num_iteration = 50
        self.verbose = 0
        if self.verbose:
            logging.getLogger().setLevel(level=logging.INFO)


    def set_root(self, new_root):
        self.root = new_root 
    
    def choose_piece(self) -> int:
        start = time.time()
        losing_moves = set()
        status = self.get_game().get_board_status()
        for piece in list(set(m for m in range(16)) - set(r for row in status for r in row if r != -1)):
            for pos in [(idxc, idxr) for idxr, row in enumerate(status) for idxc, r in enumerate(row) if r == -1]:
                status_tmp = deepcopy(status)
                game_tmp = Q(status_tmp)
                game_tmp.select(piece) 
                game_tmp.place(*pos)
                if game_tmp.check_winner() > -1:
                   losing_moves.add(piece) 
                   break
                else:
                    continue
        # print(f"time for check:{time.time() - start}")
        root_node = Node(status, sel=False, selected=None, losing_moves=losing_moves)
        self.set_root(root_node)
        _, action = self.montecarlo()
        logging.info(f" time for select:{time.time() - start}")
        return action            

    def place_piece(self) -> tuple[int, int]:
        start = time.time()
        root_node = Node(self.get_game().get_board_status(), sel=True, selected=self.get_game().get_selected_piece(), losing_moves=None)
        self.set_root(root_node)
        _, action = self.montecarlo()   
        logging.info(f" time for place:{time.time() - start}")
        return action   

    def montecarlo(self):
        if self.available_seconds:
            i = 0
            end_time = time.time() + self.available_seconds-0.03
            while(True):
                v = self.search()
                reward = v.rollout()
                v.backpropagate(reward)
                i += 1
                if time.time() > end_time:
                    break
            logging.info(f" node processed:{i}")
        else:
            for _ in range(0, self.num_iteration):
                v = self.search()
                reward = v.rollout()
                v.backpropagate(reward)
            logging.info(f" node processed:{_+1}")
        # to select best child go for exploitation only
        return self.root.best_child(c_param=0.)

    def search(self):                     
        current_node = self.root
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.balanced_expand()
            else:
                current_node = current_node.best_child()[0]
        return current_node