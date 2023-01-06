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
    board = np.ones(shape=(BOARD_SIDE, BOARD_SIDE), dtype=int) * -1
    pieces = []
    pieces.append(Piece(False, False, False, False))  # 0
    pieces.append(Piece(False, False, False, True))  # 1
    pieces.append(Piece(False, False, True, False))  # 2
    pieces.append(Piece(False, False, True, True))  # 3
    pieces.append(Piece(False, True, False, False))  # 4
    pieces.append(Piece(False, True, False, True))  # 5
    pieces.append(Piece(False, True, True, False))  # 6
    pieces.append(Piece(False, True, True, True))  # 7
    pieces.append(Piece(True, False, False, False))  # 8
    pieces.append(Piece(True, False, False, True))  # 9
    pieces.append(Piece(True, False, True, False))  # 10
    pieces.append(Piece(True, False, True, True))  # 11
    pieces.append(Piece(True, True, False, False))  # 12
    pieces.append(Piece(True, True, False, True))  # 13
    pieces.append(Piece(True, True, True, False))  # 14
    pieces.append(Piece(True, True, True, True))  # 15
    current_player = 0
    selected_piece_index = -1

    def __init__(self):
        self.__players = ()
    
    def clear(self):
        self.__players = ()
        self.current_player = 0
        self.selected_piece_index = -1
        self.board = np.ones(shape=(self.BOARD_SIDE, self.BOARD_SIDE), dtype=int) * -1
        

    def set_players(self, players: tuple[Player, Player]):
        self.__players = players

    def select(self, pieceIndex: int):
        '''
        select a piece. Returns True on success
        '''
        if pieceIndex not in self.board:
            self.selected_piece_index = pieceIndex
            return self.selected_piece_index
        return False

    def print(self):
        '''
        Print the board
        '''
        for row in self.board:
            print("\n -------------------")
            print("|", end="")
            for element in row:
                print(f" {element: >2}", end=" |")
        print("\n -------------------\n")
        #print(f"Selected piece: {self.selected_piece_index}\n")

    def get_piece_charachteristics(self, index: int):
        '''
        Gets charachteristics of a piece (index-based)
        '''
        return copy.deepcopy(self.pieces[index])

    def get_board_status(self):
        '''
        Get the current board status (pieces are represented by index)
        '''
        return copy.deepcopy(self.board)

    def get_selected_piece(self):
        '''
        Get index of selected piece
        '''
        return copy.deepcopy(self.selected_piece_index)
    
    def placeable(self, x: int, y: int):
        return not (y < 0 or x < 0 or x > 3 or y > 3 or self.board[y, x] >= 0)

    def place(self, x: int, y: int):
        '''
        Place piece in coordinates (x, y). Returns true on success
        '''
        if self.placeable(x, y):
            self.board[y, x] = self.selected_piece_index
            return True
        return False
    
    def unplace(self, x: int, y: int):
        self.board[y, x] = -1
      

    def check_horizontal(self):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in self.board[i] if elem >= 0 and self.pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in self.board[i] if elem >= 0 and self.pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in self.board[i] if elem >= 0 and self.pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in self.board[i] if elem >= 0 and self.pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in self.board[i] if elem >= 0 and not self.pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in self.board[i] if elem >= 0 and not self.pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in self.board[i] if elem >= 0 and not self.pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in self.board[i] if elem >= 0 and not self.pieces[elem].SQUARE
            ]
            if len(high_values) == self.BOARD_SIDE or len(coloured_values) == self.BOARD_SIDE or len(solid_values) == self.BOARD_SIDE or len(
                    square_values) == self.BOARD_SIDE or len(low_values) == self.BOARD_SIDE or len(
                        noncolor_values) == self.BOARD_SIDE or len(
                            hollow_values) == self.BOARD_SIDE or len(
                                circle_values) == self.BOARD_SIDE:
                return self.current_player
        return -1

    def check_vertical(self):
        for i in range(self.BOARD_SIDE):
            high_values = [
                elem for elem in self.board[:, i] if elem >= 0 and self.pieces[elem].HIGH
            ]
            coloured_values = [
                elem for elem in self.board[:, i] if elem >= 0 and self.pieces[elem].COLOURED
            ]
            solid_values = [
                elem for elem in self.board[:, i] if elem >= 0 and self.pieces[elem].SOLID
            ]
            square_values = [
                elem for elem in self.board[:, i] if elem >= 0 and self.pieces[elem].SQUARE
            ]
            low_values = [
                elem for elem in self.board[:, i] if elem >= 0 and not self.pieces[elem].HIGH
            ]
            noncolor_values = [
                elem for elem in self.board[:, i] if elem >= 0 and not self.pieces[elem].COLOURED
            ]
            hollow_values = [
                elem for elem in self.board[:, i] if elem >= 0 and not self.pieces[elem].SOLID
            ]
            circle_values = [
                elem for elem in self.board[:, i] if elem >= 0 and not self.pieces[elem].SQUARE
            ]
            if len(high_values) == self.BOARD_SIDE or len(
                    coloured_values
            ) == self.BOARD_SIDE or len(solid_values) == self.BOARD_SIDE or len(
                    square_values) == self.BOARD_SIDE or len(low_values) == self.BOARD_SIDE or len(
                        noncolor_values) == self.BOARD_SIDE or len(
                            hollow_values) == self.BOARD_SIDE or len(
                                circle_values) == self.BOARD_SIDE:
                return self.current_player
        return -1

    def check_diagonal(self):
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if self.board[i, i] < 0:
                break
            if self.pieces[self.board[i, i]].HIGH:
                high_values.append(self.board[i, i])
            else:
                low_values.append(self.board[i, i])
            if self.pieces[self.board[i, i]].COLOURED:
                coloured_values.append(self.board[i, i])
            else:
                noncolor_values.append(self.board[i, i])
            if self.pieces[self.board[i, i]].SOLID:
                solid_values.append(self.board[i, i])
            else:
                hollow_values.append(self.board[i, i])
            if self.pieces[self.board[i, i]].SQUARE:
                square_values.append(self.board[i, i])
            else:
                circle_values.append(self.board[i, i])
        if len(high_values) == self.BOARD_SIDE or len(coloured_values) == self.BOARD_SIDE or len(
                solid_values) == self.BOARD_SIDE or len(square_values) == self.BOARD_SIDE or len(
                    low_values
                ) == self.BOARD_SIDE or len(noncolor_values) == self.BOARD_SIDE or len(
                    hollow_values) == self.BOARD_SIDE or len(circle_values) == self.BOARD_SIDE:
            return self.current_player
        high_values = []
        coloured_values = []
        solid_values = []
        square_values = []
        low_values = []
        noncolor_values = []
        hollow_values = []
        circle_values = []
        for i in range(self.BOARD_SIDE):
            if self.board[i, self.BOARD_SIDE - 1 - i] < 0:
                break
            if self.pieces[self.board[i, self.BOARD_SIDE - 1 - i]].HIGH:
                high_values.append(self.board[i, self.BOARD_SIDE - 1 - i])
            else:
                low_values.append(self.board[i, self.BOARD_SIDE - 1 - i])
            if self.pieces[self.board[i, self.BOARD_SIDE - 1 - i]].COLOURED:
                coloured_values.append(
                    self.board[i, self.BOARD_SIDE - 1 - i])
            else:
                noncolor_values.append(
                    self.board[i, self.BOARD_SIDE - 1 - i])
            if self.pieces[self.board[i, self.BOARD_SIDE - 1 - i]].SOLID:
                solid_values.append(self.board[i, self.BOARD_SIDE - 1 - i])
            else:
                hollow_values.append(self.board[i, self.BOARD_SIDE - 1 - i])
            if self.pieces[self.board[i, self.BOARD_SIDE - 1 - i]].SQUARE:
                square_values.append(self.board[i, self.BOARD_SIDE - 1 - i])
            else:
                circle_values.append(self.board[i, self.BOARD_SIDE - 1 - i])
        if len(high_values) == self.BOARD_SIDE or len(coloured_values) == self.BOARD_SIDE or len(
                solid_values) == self.BOARD_SIDE or len(square_values) == self.BOARD_SIDE or len(
                    low_values
                ) == self.BOARD_SIDE or len(noncolor_values) == self.BOARD_SIDE or len(
                    hollow_values) == self.BOARD_SIDE or len(circle_values) == self.BOARD_SIDE:
            return self.current_player
        return -1

    def check_winner(self):
        '''
        Check who is the winner
        '''
        l = [self.check_horizontal(), self.check_vertical(), self.check_diagonal()]
        for elem in l:
            if elem >= 0:
                return elem
        return -1

    def check_finished(self):
        '''
        Check who is the loser
        '''
        for row in self.board:
            for elem in row:
                if elem == -1:
                    return False
        return True
    
    def into_bit(self, piece: int):
        first_bit = piece % 2
        piece = math.floor(piece / 2)
        second_bit = piece % 2
        piece = math.floor(piece / 2)
        third_bit = piece % 2
        piece = math.floor(piece / 2)
        forth_bit = math.floor(piece % 2)
        return (forth_bit, third_bit, second_bit, first_bit)
        
    
    """0 = il mio avversario = random player, 1 = io = risky"""
    def run(self):
        '''
        Run the game (with output for every move)
        '''
        winner = -1
        turno = 0
        while winner < 0 and not self.check_finished():
            piece_ok = False
            while not piece_ok: 
                piece_ok = self.select(self.__players[self.current_player].choose_piece()) #scelgo il pezzo 
            piece_ok_bit = self.into_bit(piece_ok)
            #print(f"Player {self.current_player} sceglie pezzo = {piece_ok} = {piece_ok_bit}")
            piece_ok = False
            
            self.current_player = (self.current_player + 1) % self.MAX_PLAYERS #lo do all'avversario
            
            while not piece_ok:
                x, y = self.__players[self.current_player].place_piece() #scelgo dove posizionarlo
                piece_ok = self.place(x, y) #lo piazzo
            #print(f"Player {self.current_player} posiziona il pezzo in ({x},{y})")
                
            winner = self.check_winner()  
            turno = turno + 1
        return winner