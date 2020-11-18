import random

# learning param
DEFAULT_LEARNING_RATE = 0.875
DEFAULT_DISCOUNT_FACTOR = 0.9

IA_NB_TOURS = 6

#game state schema
'''    0 1 2 3
     0 | | | |
     1 | | | | 
     2 | | | |
     3 | | | |
     
     | = {2^0, ....2^11}
'''
#actions actions values
UP = 'U'
DOWN = 'D'
LEFT = 'L'
RIGHT = 'R'
ACTIONS = ['U', 'D', 'L', 'R']

#game reward
GAME_SCORE = 0
REWARD_STUCK = -GAME_SCORE
REWARD_CONTINUE = GAME_SCORE

REWARD_GOAL = 2048
REWARD1024 = 1024
REWARD512 = 512
REWARD256 = 256
REWARD128 = 128
REWARD64 = 64
REWARD32 = 32
REWARD16 = 16
REWARD8 = 8
REWARD4 = 4
REWARD2 = 2

REWARD_DEFAULT = 1
REWARD_GAMEOVER = -100000
REWARD_NO_ACTION = -1


#Generer Aleatoirement
GENERATED_VALUES = [2, 4] #TODO: Générer aléatoirement avec une fréquence plus importante pour le 2
    #Generer Aleatoirement la valeur
def randomValue():
    return random.choice(GENERATED_VALUES)
    #Generer Aleatoirement les coordonnée contenant les valeurs
def randomXY(lenght):
    return random.choice(range(lenght))

def generateDefaultAction():
    return random.choice(ACTIONS)







list_actions_examples = [UP, UP, UP, DOWN, LEFT, RIGHT, LEFT, DOWN, UP]