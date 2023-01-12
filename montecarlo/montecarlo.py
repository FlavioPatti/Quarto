import quarto
from montecarlo import node
from copy import deepcopy 

class MonteCarloPlayer(quarto.Player):
    def __init__(self, quarto: quarto.Quarto, node=None) -> None:
        super().__init__(quarto) 
        self.root = node

    def set_root(self, new_root):
        self.root = new_root 
    
    def choose_piece(self) -> int:
        losing_moves = set()
        for piece in list(set(m for m in range(16)) - set(r for row in self.get_game().get_board_status() for r in row if r != -1)):
            for pos in [(idxc, idxr) for idxr, row in enumerate(self.get_game().get_board_status()) for idxc, r in enumerate(row) if r == -1]:
                game_tmp = deepcopy(self.get_game())
                game_tmp.select(piece) 
                game_tmp.place(*pos)
                if game_tmp.check_winner() > -1:
                   losing_moves.add(piece) 
                   break
                else:
                    continue
        root_node = node.Node(self.get_game(), sel=False, selected=None, losing_moves=losing_moves)
        self.set_root(root_node)
        _, action = self.montecarlo()
        return action            

    def place_piece(self) -> tuple[int, int]:
        root_node = node.Node(self.get_game(), sel=True, selected=self.get_game().get_selected_piece(), losing_moves=None)
        self.set_root(root_node)
        _, action = self.montecarlo()   
        return action   

    def montecarlo(self, num_iteration=10000):
        for _ in range(0, num_iteration):   
            v = self.search()
            reward = v.rollout()
            v.backpropagate(reward)
            #if _ % 1000 == 0:
            #    print(_)
        return self.root.best_child(c_param=0.)

    def search(self):                     
        current_node = self.root
        while not current_node.is_terminal_node(current_node.game):
            if not current_node.is_fully_expanded():
                return current_node.balanced_expand()
            else:
                current_node = current_node.best_child()[0]
        return current_node