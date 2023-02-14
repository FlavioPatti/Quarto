from collections import namedtuple
import random
from copy import deepcopy
import quarto
import math

Individual = namedtuple("Individual", ["genome", "fitness"])
# Genome -> array of 8 elements (4 figures + 4 positions)

BOARD_SIZE = 4
GENOME_SIZE = BOARD_SIZE * 2
POPULATION_SIZE = 50
NUM_GENERATIONS = 5
OFFSPRING_SIZE = 25
TOURNAMENT_SIZE = 4
CROSSOVER_THRESHOLD = 0.4
MUTATION_THRESHOLD = 0.1


class GeneticAlgorithm():

    def __init__(self, current_game: quarto.Quarto):
        self.current_game = current_game
    
    def coordinate_tuple_to_index(self, row, col):
        return 4 * row + col

    def coordinate_index_to_tuple(self, index):
        col = index % BOARD_SIZE
        row = math.floor(index / BOARD_SIZE)
        return (row,col)
    
    """Lists available positions on the board, considering also the positions potentially taken by the genome"""
    def available_positions(self, genome: list = None):
        list_available_positions = []

        for row in range(self.current_game.BOARD_SIDE):
            for col in range(self.current_game.BOARD_SIDE):
                if self.current_game._board[col,row] == -1:
                    coord = self.coordinate_tuple_to_index(row, col)
                    list_available_positions.append(coord)

        if genome is not None:
            for i in range(GENOME_SIZE//2, GENOME_SIZE):
                if (genome[i] in list_available_positions) and len(list_available_positions) > 0:
                    list_available_positions.remove(genome[i])
        
        return list_available_positions
    
    """Lists available pieces, considering also the pieces potentially taken by the genome"""
    def available_pieces(self, genome: list = None):
        list_available_pieces = list(range(16))
        
        if genome is not None:
            for i in range(0, GENOME_SIZE//2):
                if (genome[i] in list_available_pieces):
                    list_available_pieces.remove(genome[i])

        for row in range(self.current_game.BOARD_SIDE):
            for col in range(self.current_game.BOARD_SIDE):
                current_piece = self.current_game._board[col,row]
                if current_piece != -1 and len(list_available_pieces) > 0 and current_piece in list_available_pieces:
                    list_available_pieces.remove(current_piece)

                    
        return list_available_pieces
    
    
    """Parent selection - TOURNAMENT version"""
    def tournament(self, population, tournament_size=TOURNAMENT_SIZE):          
        return max(random.choices(population, k=tournament_size), key=lambda i: i.fitness) 
    
    """Parent selection - ROULETTE WHEEL version"""
    def roulette_wheel_selection(self, population):
    
        fitness_sum = sum(individual.fitness for individual in population)
    
        if fitness_sum == 0:
            return self.tournament(population, TOURNAMENT_SIZE)
    
        normalized_fitness = [individual.fitness/fitness_sum for individual in population]
            
        cumulative_probabilities = [sum(normalized_fitness[:i+1])
                                    for i in range(len(normalized_fitness))]
        
        random_num = random.random()
        for i, prob in enumerate(cumulative_probabilities):
            if random_num <= prob:
                return population[i]
    
    """Generate our initial population"""
    def init_population(self):
        population = []
        for p in range(POPULATION_SIZE):
            for g in range(GENOME_SIZE):
                genome = [-1]*GENOME_SIZE
                
                if self.current_game._Quarto__selected_piece_index == -1:
                    genome[0] = random.randint(0,15)
                else:
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

    """Crossover between genomes. The new genome will have some genes from first parent, and other genes from second one"""
    def cross_over(self, genome_1, genome_2):
        new_genome = []
        for i in range(0, GENOME_SIZE):
            if (random.randint(0,1) > CROSSOVER_THRESHOLD):
                new_genome.append(genome_1[i])
            else:
                new_genome.append(genome_2[i])
        return new_genome

    """ Mutation of the genome. "pieces" and "position" genes are swapped among each other"""
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
        
        """implementation of segregation with 3 subsets to promove diversity"""
        num_subset = 3
        list_of_subset_1 = []
        list_of_subset_2 = []
        list_of_subset_3 = []
        individual_for_subset = len(population)/num_subset
        for individual in population:
            if len(list_of_subset_1) < individual_for_subset:
                list_of_subset_1.append(individual)
            elif len(list_of_subset_2) < individual_for_subset:
                list_of_subset_2.append(individual)
            elif len(list_of_subset_3) < individual_for_subset:
                list_of_subset_3.append(individual)
            
        """generate offspring for subset 1"""
        for g in range(NUM_GENERATIONS):
            offspring = list()
            for i in range(OFFSPRING_SIZE):
                if random.random() > MUTATION_THRESHOLD: #mutation
                    p = self.roulette_wheel_selection(list_of_subset_1)                  
                    o = self.mutation(p.genome)

                    f = self.compute_fitness(o)

                    if (f > p.fitness):
                        offspring.append(Individual(o, f)) 
                    else:
                        offspring.append(p) 

                if random.random() > CROSSOVER_THRESHOLD: #crossover                                     
                    p1 = self.roulette_wheel_selection(list_of_subset_1)                 
                    p2 = self.roulette_wheel_selection(list_of_subset_1)

                    o = self.cross_over(p1.genome, p2.genome)            
                    f = self.compute_fitness(o)

                    offspring.append(Individual(o,f))  
                                                           
            list_of_subset_1 += offspring
            
        """generate offspring for subset 2"""
        for g in range(NUM_GENERATIONS):
            offspring = list()
            for i in range(OFFSPRING_SIZE):
                if random.random() > MUTATION_THRESHOLD: #mutation
                    p = self.roulette_wheel_selection(list_of_subset_2)                  
                    o = self.mutation(p.genome)

                    f = self.compute_fitness(o)

                    if (f > p.fitness):
                        offspring.append(Individual(o, f)) 
                    else:
                        offspring.append(p) 

                if random.random() > CROSSOVER_THRESHOLD: #crossover                                     
                    p1 = self.roulette_wheel_selection(list_of_subset_2)                 
                    p2 = self.roulette_wheel_selection(list_of_subset_2)

                    o = self.cross_over(p1.genome, p2.genome)            
                    f = self.compute_fitness(o)

                    offspring.append(Individual(o,f))  
                                                           
            list_of_subset_2 += offspring
        
        """generate offspring for subset 3"""
        for g in range(NUM_GENERATIONS):
            offspring = list()
            for i in range(OFFSPRING_SIZE):
                if random.random() > MUTATION_THRESHOLD: #mutation
                    p = self.roulette_wheel_selection(list_of_subset_3)                  
                    o = self.mutation(p.genome)

                    f = self.compute_fitness(o)

                    if (f > p.fitness):
                        offspring.append(Individual(o, f)) 
                    else:
                        offspring.append(p) 

                if random.random() > CROSSOVER_THRESHOLD: #crossover                                     
                    p1 = self.roulette_wheel_selection(list_of_subset_3)                 
                    p2 = self.roulette_wheel_selection(list_of_subset_3)

                    o = self.cross_over(p1.genome, p2.genome)            
                    f = self.compute_fitness(o)

                    offspring.append(Individual(o,f))  
                                                           
            list_of_subset_3 += offspring
                
        tot = int(POPULATION_SIZE/num_subset)
        population_1 = sorted(list_of_subset_1, key=lambda i: i[1], reverse = True)[:tot]
        for individual in population_1:
            if len(list_of_subset_2) < individual_for_subset+tot/2:
                    list_of_subset_2.append(individual)
            elif len(list_of_subset_3) < individual_for_subset+tot/2:
                list_of_subset_3.append(individual)
                
        """generate offspring for subset 2"""
        for g in range(NUM_GENERATIONS):
            offspring = list()
            for i in range(OFFSPRING_SIZE):
                if random.random() > MUTATION_THRESHOLD: #mutation
                    p = self.roulette_wheel_selection(list_of_subset_2)                  
                    o = self.mutation(p.genome)

                    f = self.compute_fitness(o)

                    if (f > p.fitness):
                        offspring.append(Individual(o, f)) 
                    else:
                        offspring.append(p) 

                if random.random() > CROSSOVER_THRESHOLD: #crossover                                     
                    p1 = self.roulette_wheel_selection(list_of_subset_2)                 
                    p2 = self.roulette_wheel_selection(list_of_subset_2)

                    o = self.cross_over(p1.genome, p2.genome)            
                    f = self.compute_fitness(o)

                    offspring.append(Individual(o,f))  
                                                           
            list_of_subset_2 += offspring
        
        """generate offspring for subset 3"""
        for g in range(NUM_GENERATIONS):
            offspring = list()
            for i in range(OFFSPRING_SIZE):
                if random.random() > MUTATION_THRESHOLD: #mutation
                    p = self.roulette_wheel_selection(list_of_subset_3)                  
                    o = self.mutation(p.genome)

                    f = self.compute_fitness(o)

                    if (f > p.fitness):
                        offspring.append(Individual(o, f)) 
                    else:
                        offspring.append(p) 

                if random.random() > CROSSOVER_THRESHOLD: #crossover                                     
                    p1 = self.roulette_wheel_selection(list_of_subset_3)                 
                    p2 = self.roulette_wheel_selection(list_of_subset_3)

                    o = self.cross_over(p1.genome, p2.genome)            
                    f = self.compute_fitness(o)

                    offspring.append(Individual(o,f))  
                                                           
            list_of_subset_3 += offspring
        
        tot = int(POPULATION_SIZE/num_subset)
        population_2 = sorted(list_of_subset_2, key=lambda i: i[1], reverse = True)[:tot]
        for individual in population_2:
            if len(list_of_subset_3) < individual_for_subset+tot:
                list_of_subset_3.append(individual)
                
        """remove duplicate from the population"""
        unique_population = []
        unique_genomes = []
        for individual in list_of_subset_3:
            if individual.genome not in unique_genomes:
                unique_genomes.append(individual.genome)
                unique_population.append(individual)       
    
        population = sorted(unique_population, key=lambda i: i[1], reverse = True)[:POPULATION_SIZE]
        best_genome = population[0][0]
        
        piece_to_give = best_genome[1]
        position_to_play = self.coordinate_index_to_tuple(best_genome[4])
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
        self.current_game.__selected_piece_index = current_piece
        
        list_winning_moves = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                game_copy = deepcopy(self.current_game)
                game_copy.place(row, col)

                if self.check_winning_move(game_copy):
                    coord = self.coordinate_tuple_to_index(row,col)
                    list_winning_moves.append(coord)
        
        self.current_game._Quarto__selected_piece_index = old_piece_index
        return list_winning_moves
    
    def compute_fitness (self,genome):
        winning_reward = 10
        losing_reward = 10
        tot_reward = 0
                
        for index in range(GENOME_SIZE//2):
            piece = genome[index]
            coordinates = genome[GENOME_SIZE//2-index]
            myTurn = True
            
            list = self.winning_pos(piece)
            
            if myTurn:
                if list.count(coordinates) > 0:
                    tot_reward += winning_reward * (GENOME_SIZE//2-index)
                #else: tot_reward -= 5 
            else:
                if list.count(coordinates) > 0:
                    tot_reward -= losing_reward * (GENOME_SIZE//2-index)
                #else: tot_reward += 5  

            myTurn = not myTurn
            
        return tot_reward
