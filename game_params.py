import random
#game_schema
'''    0 1 2 3
     0 | | | |
     1 | | | | 
     2 | | | |
     3 | | | |
'''
#Generer Aleatoirement
GENERATED_VALUES = [2, 4] #TODO: Générer aléatoirement avec une fréquence plus importante pour le 2
    #Generer Aleatoirement la valeur
def randomValue():
    return random.choice(GENERATED_VALUES)
    #Generer Aleatoirement les coordonnée contenant les valeurs
def randomXY(lenght):
    return random.choice(range(lenght))

#learning param
DEFAULT_LEARNING_RATE = 0.9;
DEFAULT_DISCOUNT_FACTOR = 0.5;

#actions param
UP = 'U'
DOWN = 'D'
LEFT = 'L'
RIGHT = 'R'
ACTIONS = [UP, DOWN, LEFT, RIGHT];



list_actions_examples = [UP, DOWN, DOWN, RIGHT, LEFT, UP, LEFT];