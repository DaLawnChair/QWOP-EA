import numpy as np 
import random

MAX_DURATION = 1000
RESOLUTION = 0.1 
INPUT_LENGTH = int(MAX_DURATION*RESOLUTION)

TOURNAMENT_SIZE = 3

OPTIONS = set(["Q","W","O","P"])


individuals = [] 

for i in range(TOURNAMENT_SIZE):
    individual = []
    for j in range(INPUT_LENGTH):
        item = ""
        item += "Q" if random.random() > 0.5 else ""
        item += "W" if random.random() > 0.5 else ""
        item += "O" if random.random() > 0.5 else ""
        item += "P" if random.random() > 0.5 else ""
        individual.append(item)


    individuals.append(individual)

print(individuals)
print(individuals[0])

results = {}
# from play_scripted_sequence import main
from game_class import Game

for i,input_sequence in enumerate(individuals):
    input_script = [ (i*0.1, item) for i,item in enumerate(input_sequence)]

    game = Game(input_sequence)
    result = game.run()

    results[i] = result
    print(results)
    import time
    time.sleep(2)
    






