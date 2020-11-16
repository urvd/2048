import random
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

REWARD_GOAL = 60
REWARD_DEFAULT = 1
REWARD_GAMEOVER = -60
REWARD_NO_ACTION = -5


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

#learning param
DEFAULT_LEARNING_RATE = 0.875;
DEFAULT_DISCOUNT_FACTOR = 0.5;





list_actions_examples = [UP, UP, UP, DOWN, LEFT, RIGHT, LEFT, DOWN, UP]