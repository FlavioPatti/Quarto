# Free for personal or classroom use; see 'LICENSE.md' for details.
# https://github.com/squillero/computational-intelligence

import numpy as np
from abc import abstractmethod
import copy
import math
import copy 
import random


class Player(object):

    def __init__(self, quarto):
        self.__quarto = quarto

    @abstractmethod
    def choose_piece(self):
        pass

    @abstractmethod
    def place_piece(self):
        pass

    def get_game(self):
        return self.__quarto

class Piece(object):

    def __init__(self, high: bool, coloured: bool, solid: bool, square: bool):
        self.HIGH = high
        self.COLOURED = coloured
        self.SOLID = solid
        self.SQUARE = square
        
class Quarto(object):

    MAX_PLAYERS = 2
    BOARD_SIDE = 4
    
    def __init__(self):
        self.__players = ()
        self.reset()
    
    def reset(self):
        self.__board = np.ones(shape=(self.BOARD_SIDE, self.BOARD_SIDE), dtype=int) * -1
        """Draw configuration
        self.__board[0,0] = 0
        self.__board[1,0] = 12
        self.__board[2,0] = 7
        self.__board[3,0] = 11
        self.__board[0,1] = 9
        self.__board[1,1] = 1
        self.__board[2,1] = 13
        self.__board[3,1] =6
        self.__board[0,2] = 10
        self.__board[1,2] = 2
        self.__board[2,2] = 4
        self.__board[3,2] = 5
        self.__board[0,3] = 15
        self.__board[1,3] = 8
        self.__board[2,3] = 3
        #self.__board[3,3] = 14
        """
        
        self.__pieces = []
        self.__pieces.append(Piece(False, False, False, False))  # 0
        self.__pieces.append(Piece(False, False, False, True))  # 1
        self.__pieces.append(Piece(False, False, True, False))  # 2
        self.__pieces.append(Piece(False, False, True, True))  # 3
        self.__pieces.append(Piece(False, True, False, False))  # 4
        self.__pieces.append(Piece(False, True, False, True))  # 5
        self.__pieces.append(Piece(False, True, True, False))  # 6
        self.__pieces.append(Piece(False, True, True, True))  # 7
        self.__pieces.append(Piece(True, False, False, False))  # 8
        self.__pieces.append(Piece(True, False, False, True))  # 9
        self.__pieces.append(Piece(True, False, True, False))  # 10
        self.__pieces.append(Piece(True, False, True, True))  # 11
        self.__pieces.append(Piece(True, True, False, False))  # 12
        self.__pieces.append(Piece(True, True, False, True))  # 13
        self.__pieces.append(Piece(True, True, True, False))  # 14
        self.__pieces.append(Piece(True, True, True, True))  # 15
        self.__current_player = 0
        self.__selected_piece_index = -1
        

    def set_players(self, players: tuple[Player, Player]):
        self.__players = players

    def select(self, pieceIndex: int):
        '''
        select a piece. Returns True on success
        '''
        if pieceIndex not in self.__board:
            self.__selected_piece_index = pieceIndex
            #return self.__selected_piece_index
            return True
        return False

    def print(self):
        '''
        Print the board
        '''
        for row in self.__board:
            print("\n -------------------")
            print("|", end="")
            for element in row:
                print(f" {element: >2}", end=" |")
        print("\n -------------------\n")
        #print(f"Selected piece: {self.__selected_piece_index}\n")

    def get_piece_charachteristics(self, index: int):
        '''
        Gets charachteristics of a piece (index-based)
        '''
        return copy.deepcopy(self.__pieces[index])

    def get_board_status(self):
        '''
        Get the current board status (pieces are represented by index)
        '''
        return copy.deepcopy(self.__board)

    def get_selected_piece(self):
        '''
        Get index of selected piece
        '''
        return copy.deepcopy(self.__selected_piece_index)
    
    def __placeable(self, x: int, y: int):
        return not (y < 0 or x < 0 or x > 3 or y > 3 or self.__board[y, x] >= 0)

    def place(self, x: int, y: int):
        '''
        Place piece in coordinates (x, y). Returns true on success
        '''
        if self.__placeable(x, y):
            self.__board[y, x] = self.__selected_piece_index
            return True
        return False
      

    def __check_horizontal(self):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in self.__board[i] if elem >= 0 and self.__pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in self.__board[i] if elem >= 0 and self.__pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in self.__board[i] if elem >= 0 and self.__pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in self.__board[i] if elem >= 0 and self.__pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in self.__board[i] if elem >= 0 and not self.__pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in self.__board[i] if elem >= 0 and not self.__pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in self.__board[i] if elem >= 0 and not self.__pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in self.__board[i] if elem >= 0 and not self.__pieces[elem].SQUARE
            ]
            if len(high_values) == self.BOARD_SIDE or len(
                    coloured_values
            ) == self.BOARD_SIDE or len(solid_values) == self.BOARD_SIDE or len(
                    square_values) == self.BOARD_SIDE or len(low_values) == self.BOARD_SIDE or len(
                        noncolor_values) == self.BOARD_SIDE or len(
                            hollow_values) == self.BOARD_SIDE or len(
                                circle_values) == self.BOARD_SIDE:
                return self.__current_player
        return -1

    def __check_vertical(self):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and self.__pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and self.__pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and self.__pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and self.__pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and not self.__pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and not self.__pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and not self.__pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in self.__board[:, i] if elem >= 0 and not self.__pieces[elem].SQUARE
            ]
            if len(high_values) == self.BOARD_SIDE or len(
                    coloured_values
            ) == self.BOARD_SIDE or len(solid_values) == self.BOARD_SIDE or len(
                    square_values) == self.BOARD_SIDE or len(low_values) == self.BOARD_SIDE or len(
                        noncolor_values) == self.BOARD_SIDE or len(
                            hollow_values) == self.BOARD_SIDE or len(
                                circle_values) == self.BOARD_SIDE:
                return self.__current_player
        return -1

    def __check_diagonal(self):
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if self.__board[i, i] < 0:
                break
            if self.__pieces[self.__board[i, i]].HIGH:
                high_values.append(self.__board[i, i])
            else:
                low_values.append(self.__board[i, i])
            if self.__pieces[self.__board[i, i]].COLOURED:
                coloured_values.append(self.__board[i, i])
            else:
                noncolor_values.append(self.__board[i, i])
            if self.__pieces[self.__board[i, i]].SOLID:
                solid_values.append(self.__board[i, i])
            else:
                hollow_values.append(self.__board[i, i])
            if self.__pieces[self.__board[i, i]].SQUARE:
                square_values.append(self.__board[i, i])
            else:
                circle_values.append(self.__board[i, i])
        if len(high_values) == self.BOARD_SIDE or len(coloured_values) == self.BOARD_SIDE or len(
                solid_values) == self.BOARD_SIDE or len(square_values) == self.BOARD_SIDE or len(
                    low_values
                ) == self.BOARD_SIDE or len(noncolor_values) == self.BOARD_SIDE or len(
                    hollow_values) == self.BOARD_SIDE or len(circle_values) == self.BOARD_SIDE:
            return self.__current_player
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if self.__board[i, self.BOARD_SIDE - 1 - i] < 0:
                break
            if self.__pieces[self.__board[i, self.BOARD_SIDE - 1 - i]].HIGH:
                high_values.append(self.__board[i, self.BOARD_SIDE - 1 - i])
            else:
                low_values.append(self.__board[i, self.BOARD_SIDE - 1 - i])
            if self.__pieces[self.__board[i, self.BOARD_SIDE - 1 - i]].COLOURED:
                coloured_values.append(
                    self.__board[i, self.BOARD_SIDE - 1 - i])
            else:
                noncolor_values.append(
                    self.__board[i, self.BOARD_SIDE - 1 - i])
            if self.__pieces[self.__board[i, self.BOARD_SIDE - 1 - i]].SOLID:
                solid_values.append(self.__board[i, self.BOARD_SIDE - 1 - i])
            else:
                hollow_values.append(self.__board[i, self.BOARD_SIDE - 1 - i])
            if self.__pieces[self.__board[i, self.BOARD_SIDE - 1 - i]].SQUARE:
                square_values.append(self.__board[i, self.BOARD_SIDE - 1 - i])
            else:
                circle_values.append(self.__board[i, self.BOARD_SIDE - 1 - i])
        if len(high_values) == self.BOARD_SIDE or len(coloured_values) == self.BOARD_SIDE or len(
                solid_values) == self.BOARD_SIDE or len(square_values) == self.BOARD_SIDE or len(
                    low_values
                ) == self.BOARD_SIDE or len(noncolor_values) == self.BOARD_SIDE or len(
                    hollow_values) == self.BOARD_SIDE or len(circle_values) == self.BOARD_SIDE:
            return self.__current_player
        return -1

    def check_winner(self):
        '''
        Check who is the winner
        '''
        l = [self.__check_horizontal(), self.__check_vertical(), self.__check_diagonal()]
        for elem in l:
            if elem >= 0:
                return elem
        return -1

    def check_finished(self):
        '''
        Check who is the loser
        '''
        for row in self.__board:
            for elem in row:
                if elem == -1:
                    return False
        return True

    """
    def into_bit(self, piece: int):
        first_bit = piece % 2
        piece = math.floor(piece / 2)
        second_bit = piece % 2
        piece = math.floor(piece / 2)
        third_bit = piece % 2
        piece = math.floor(piece / 2)
        forth_bit = math.floor(piece % 2)
        return (forth_bit, third_bit, second_bit, first_bit)
    """   
    
    """0 = il mio avversario = random player, 1 = io = risky"""
    def run(self):
        '''
        Run the game (with output for every move)
        '''
        winner = -1
        while winner < 0 and not self.check_finished():
            #print("condizione board iniziale: ")
            #self.print()
            piece_ok = False
            while not piece_ok: 
                piece_ok = self.select(self.__players[self.__current_player].choose_piece()) #scelgo il pezzo 
            #piece_ok_bit = self.into_bit(piece_ok)
            #print(f"Player {self.__current_player} sceglie pezzo = {self.__selected_piece_index}")
            piece_ok = False
            
            self.__current_player = (self.__current_player + 1) % self.MAX_PLAYERS #lo do all'avversario
            
            while not piece_ok:
                x, y = self.__players[self.__current_player].place_piece() #scelgo dove posizionarlo
                piece_ok = self.place(x, y) #lo piazzo
            #print(f"Player {self.__current_player} posiziona il pezzo in ({x},{y})")
            #print("condizione board finale: ")
            #self.print()
            winner = self.check_winner() 
            #print(f"winning = {winner}") 
        return winner