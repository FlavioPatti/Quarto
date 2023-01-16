import copy
import random
import quarto

class RiskyAlgorithm(quarto.Player):
    def __init__(self, quarto: quarto.Quarto):
        super().__init__(quarto)
        self.quarto = quarto
        self.BOARD_SIDE = 4
    
    def check_winning_move(self, quarto):
        cwmh = quarto._Quarto__check_horizontal()
        cwmv = quarto._Quarto__check_vertical()
        cwmd = quarto._Quarto__check_diagonal()
        if cwmh != -1 or cwmv != -1 or cwmd != -1:
            return 1
        else:
            return 0

    def check_line_of_like_horizontal(self, quarto):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in quarto._board[i] if elem >= 0 and quarto._Quarto__pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in quarto._board[i] if elem >= 0 and quarto._Quarto__pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in quarto._board[i] if elem >= 0 and quarto._Quarto__pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in quarto._board[i] if elem >= 0 and quarto._Quarto__pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in quarto._board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in quarto._board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in quarto._board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in quarto._board[i] if elem >= 0 and not quarto._Quarto__pieces[elem].SQUARE
            ]
            if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
                return 1
        return -1

    def check_line_of_like_vertical(self, quarto):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and quarto._Quarto__pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in quarto._board[:, i] if elem >= 0 and not quarto._Quarto__pieces[elem].SQUARE
            ]
            if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
                return 1
        return -1

    def check_line_of_like_diagonal(self, quarto):
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if quarto._board[i, i] < 0:
                break
            if quarto._Quarto__pieces[quarto._board[i, i]].HIGH:
                high_values.append(quarto._board[i, i])
            else:
                low_values.append(quarto._board[i, i])
            if quarto._Quarto__pieces[quarto._board[i, i]].COLOURED:
                coloured_values.append(quarto._board[i, i])
            else:
                noncolor_values.append(quarto._board[i, i])
            if quarto._Quarto__pieces[quarto._board[i, i]].SOLID:
                solid_values.append(quarto._board[i, i])
            else:
                hollow_values.append(quarto._board[i, i])
            if quarto._Quarto__pieces[quarto._board[i, i]].SQUARE:
                square_values.append(quarto._board[i, i])
            else:
                circle_values.append(quarto._board[i, i])
        if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
            return 1
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if quarto._board[i, self.BOARD_SIDE - 1 - i] < 0:
                break
            if quarto._Quarto__pieces[quarto._board[i, self.BOARD_SIDE - 1 - i]].HIGH:
                high_values.append(quarto._board[i, self.BOARD_SIDE - 1 - i])
            else:
                low_values.append(quarto._board[i, self.BOARD_SIDE - 1 - i])
            if quarto._Quarto__pieces[quarto._board[i, self.BOARD_SIDE - 1 - i]].COLOURED:
                coloured_values.append(
                    quarto._board[i, self.BOARD_SIDE - 1 - i])
            else:
                noncolor_values.append(
                    quarto._board[i, self.BOARD_SIDE - 1 - i])
            if quarto._Quarto__pieces[quarto._board[i, self.BOARD_SIDE - 1 - i]].SOLID:
                solid_values.append(quarto._board[i, self.BOARD_SIDE - 1 - i])
            else:
                hollow_values.append(quarto._board[i, self.BOARD_SIDE - 1 - i])
            if quarto._Quarto__pieces[quarto._board[i, self.BOARD_SIDE - 1 - i]].SQUARE:
                square_values.append(quarto._board[i, self.BOARD_SIDE - 1 - i])
            else:
                circle_values.append(quarto._board[i, self.BOARD_SIDE - 1 - i])
        if len(high_values) >= 2 or len(coloured_values) >=2 or len(solid_values) >=2 or len(
                    square_values) >=2 or len(low_values) >=2 or len(
                        noncolor_values) >=2 or len(
                            hollow_values) >=2 or len(
                                circle_values) >=2:
            return 1
        return -1
    
    def check_line_of_like(self, quarto):
        cllh = self.check_line_of_like_horizontal(quarto)
        cllv = self.check_line_of_like_vertical(quarto)
        clld = self.check_line_of_like_diagonal(quarto)
        if cllh == 1 or cllv == 1 or clld == 1:
            return 1
        else:
            return 0

    def check_piece_in_board(self,quarto, piece):
        for row in range(self.BOARD_SIDE):
            for col in range(self.BOARD_SIDE):
                if quarto._board[col,row] == piece:
                    return 1
        return 0


    def choose_piece(self):
        """Evito di dare un pezzo che fa vincere l'avversario"""
        game_copy = quarto.Quarto()

        for piece in range(self.BOARD_SIDE*self.BOARD_SIDE):
            if self.check_piece_in_board(self.quarto, piece)==0:
                winning_move = 0
                for i in range(self.BOARD_SIDE): #col
                    for j in range(self.BOARD_SIDE): #row

                        game_copy._board = self.quarto.get_board_status()
                        game_copy._Quarto__binary_board = copy.deepcopy(self.quarto._Quarto__binary_board)

                        if winning_move == 0:
                            game_copy.place(i, j)
                            if game_copy.check_finished(): #self.check_winning_move(game_copy): 
                                winning_move = 1
                if winning_move == 0:
                    #print(f"risky sceglie pezzo {piece}")
                    return piece
        "Altrimenti do un pezzo random"
        piece = random.randint(0,15)
        #print(f"risky sceglie pezzo {piece}")
        return piece
    
    def place_piece(self):
        """Controllo se è possibile fare una mossa vincente"""
        winning_move = 0
        line_of_like = 0
       
        piece_ok = False


        game_copy = quarto.Quarto()
        game_copy._Quarto__selected_piece_index = self.quarto.get_selected_piece()
        game_copy._current_player = self.quarto.get_current_player()
        
        
        for i in range(self.BOARD_SIDE): #col
            for j in range(self.BOARD_SIDE): #row
                game_copy._Quarto__binary_board = copy.deepcopy(self.quarto._Quarto__binary_board)
                game_copy._board = self.quarto.get_board_status()
               
                piece_ok = game_copy.place(i, j)
                if piece_ok == True:
                    if game_copy.check_winner() != -1:
                        winning_move = 1
                        #print(f"Non DC piazza in posizione {i}-{j}")
                        return i, j

        """Altrimenti faccio una mossa lines of like se possibile"""
        """lines of like = controllo se ci sono pezzi che hanno almeno una caratteristica in comune"""  
        game_copy.reset()  
        game_copy._Quarto__selected_piece_index = self.quarto.get_selected_piece()
        game_copy._Quarto_current_player = self.quarto.get_current_player()
       
        piece_ok = False    
        if winning_move == 0:
            for i in range(self.BOARD_SIDE): #col
                for j in range(self.BOARD_SIDE): #row

                    game_copy._Quarto__binary_board = copy.deepcopy(self.quarto._Quarto__binary_board)
                    game_copy._board = self.quarto.get_board_status()

                    piece_ok = game_copy.place(i, j)
                    if piece_ok == True:
                        if self.check_line_of_like(game_copy): #da capire
                            line_of_like = 1
                            #print(f"risky piazza in posizione {i}-{j}")
                            return i, j
        """Altrimenti faccio una mossa random""" 
        piece_ok = False
        if line_of_like == 0:
            while not piece_ok:
                x, y = random.randint(0, 3), random.randint(0, 3)
                if self.quarto._board[y,x] == -1:
                    piece_ok = True
                    #print(f"risky piazza in posizione {x}-{y}")
                    return x, y