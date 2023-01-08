import logging
from collections import namedtuple
import random
from copy import deepcopy
import quarto
import math

Individual = namedtuple("Individual", ["genome", "fitness"])
# Genome -> array of 8 elements (4 figures + 4 positions)

BOARD_SIZE = 4
GENOME_SIZE = BOARD_SIZE * 2
POPULATION_SIZE = 100
NUM_GENERATIONS = 20
OFFSPRING_SIZE = 50
TOURNAMENT_SIZE = 5
GENETIC_OPERATOR_RANDOMNESS = 0.5
CROSSOVER_THRESHOLD = 0.2
MUTATION_THRESHOLD = 0.2


class GeneticAlgorithm():

    def __init__(self, current_game: quarto.Quarto):
        self.current_game = current_game
        
    def unplace(self, x: int, y: int):
        self.current_game._Quarto__board[y, x] = -1
    
    def coordinate_tuple_to_index(self, row, col):
        return 4 * row + col

    def coordinate_index_to_tuple(self, index):
        col = index % BOARD_SIZE
        row = math.floor(index / BOARD_SIZE)
        return (row,col)
    
    def available_positions(self, genome: list = None):
        list_available_positions = []

        for row in range(self.current_game.BOARD_SIDE):
            for col in range(self.current_game.BOARD_SIDE):
                if self.current_game._Quarto__board[col,row] == -1:
                    coord = self.coordinate_tuple_to_index(row, col)
                    list_available_positions.append(coord)
        #print(list_available_positions)

        if genome is not None:
            for i in range(GENOME_SIZE//2, GENOME_SIZE):
                if (genome[i] in list_available_positions) and len(list_available_positions) > 0:
                    list_available_positions.remove(genome[i])
        
        return list_available_positions
    
    
    def available_pieces(self, genome: list = None):
        list_available_pieces = list(range(16))
        #list_available_pieces.remove(self.current_game.selected_piece_index)
        
        if genome is not None:
            for i in range(0, GENOME_SIZE//2):
                if (genome[i] in list_available_pieces):
                    list_available_pieces.remove(genome[i])

        for row in range(self.current_game.BOARD_SIDE):
            for col in range(self.current_game.BOARD_SIDE):
                current_piece = self.current_game._Quarto__board[col,row]
                if current_piece != -1 and len(list_available_pieces) > 0:
                    list_available_pieces.remove(current_piece)

                    
        return list_available_pieces
    
    
    """parent selection"""
    def tournament(self, population, tournament_size=TOURNAMENT_SIZE):          
        return max(random.choices(population, k=tournament_size), key=lambda i: i.fitness) 
    
    """generate our initial population"""
    def init_population(self):
        population = []
        for p in range(POPULATION_SIZE):
            for g in range(GENOME_SIZE):
                genome = [-1]*GENOME_SIZE
                genome[0] = self.current_game._Quarto__selected_piece_index
                
                for i in range(1,GENOME_SIZE//2):
                    list_available_pieces = self.available_pieces(genome)
                    if (len(list_available_pieces) > 0):
                        genome[i] = random.choice(list_available_pieces)
                    
                for i in range(GENOME_SIZE//2,GENOME_SIZE):
                    list_available_positions = self.available_positions(genome)
                    if (len(list_available_positions) > 0):
                        genome[i] = random.choice(list_available_positions)
                
                population.append(Individual(genome, self.compute_fitness(genome)))
        
        return population

    """take 3 genomes and swap pieces / positions"""
    def cross_over(self, genome_1, genome_2):
        new_genome = []
        for i in range(0, GENOME_SIZE):
            if (random.randint(0,1) > CROSSOVER_THRESHOLD):
                new_genome.append(genome_1[i])
            else:
                new_genome.append(genome_2[i])
        return new_genome

    """change pieces and positions according to a certain threshold"""
    def mutation(self, genome): 
        new_genome = deepcopy(genome)
        for i in range(1, GENOME_SIZE//2): # mutate pieces
            if (random.randint(0,1) > MUTATION_THRESHOLD):
                available_pieces = self.available_pieces(new_genome)
                if (len(available_pieces) > 0):
                    new_genome[i] = (random.choice(available_pieces))

        for i in range(GENOME_SIZE//2, GENOME_SIZE): # mutate positions
            if (random.randint(0,1) > MUTATION_THRESHOLD):
                available_positions = self.available_positions(new_genome)
                if (len(available_positions) > 0):
                    new_genome[i] = (random.choice(available_positions))
                
        return new_genome

    def my_move(self):
        population = self.init_population()
        for g in range(NUM_GENERATIONS):
            #print(g)
            offspring = list()
            for i in range(OFFSPRING_SIZE):
                if random.random() < GENETIC_OPERATOR_RANDOMNESS:                         
                    p = self.tournament(population)                  
                    o = self.mutation(p.genome)                    
                else:                                          
                    p1 = self.tournament(population)                 
                    p2 = self.tournament(population)
                    o = self.cross_over(p1.genome, p2.genome)            
                f = self.compute_fitness(o)                                                          
                offspring.append(Individual(o, f))  
           
            population += offspring

            #population = set(population)  #remove duplicate
            #population = list(population) 

            population = sorted(population, key=lambda i: i[1], reverse = True)[:POPULATION_SIZE]
            
            best_genome = population[0][0]
        
        #print(*population, sep="\n")
        piece_to_give = best_genome[1]
        position_to_play = self.coordinate_index_to_tuple(best_genome[4])
        #print((piece_to_give, position_to_play))
        return (piece_to_give, position_to_play)
    
    
    def check_winning_move(self, game):
        cwmh = game._Quarto__check_horizontal()
        cwmv = game._Quarto__check_vertical()
        cwmd = game._Quarto__check_diagonal()
        if cwmh != -1 or cwmv != -1 or cwmd != -1:
            return 1
        else:
            return 0
    
    def winning_pos(self, current_piece):
        old_piece_index = self.current_game._Quarto__selected_piece_index
        self.current_game._Quarto__selected_piece_index = current_piece
        
        list_winning_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                game_copy = deepcopy(self.current_game)
                game_copy.place(row, col)

                if self.check_winning_move(game_copy):
                    coord = self.coordinate_tuple_to_index(row,col)
                    list_winning_moves.append(coord)
                #self.unplace(col,row)
        
        self.current_game._Quarto__selected_piece_index = old_piece_index
        return list_winning_moves
    
    def compute_fitness (self,genome):
        winning_reward = 10
        losing_reward = 10
        noCombo = 1
        tot_reward = 0
                
        for index in range(GENOME_SIZE//2):
            piece = genome[index]
            coordinates = genome[GENOME_SIZE//2-index]
            myTurn = True
            
            list = self.winning_pos(piece)
            gameOver = True if len(list) > 0 else False
            
            if gameOver:
                if myTurn:
                    if list.count(coordinates) > 0:
                        tot_reward += winning_reward * (GENOME_SIZE//2-index)
                    #else: tot_reward -= 5 
                else:
                    if list.count(coordinates) > 0:
                        tot_reward -= losing_reward * (GENOME_SIZE//2-index)
                    #else: tot_reward += 5  
            else:
                tot_reward -= noCombo

            myTurn = not myTurn
            
        return tot_reward
