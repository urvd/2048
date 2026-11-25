import random

# si false on peut passer on peut jouer en mode joueur
MODE_APPRENTISSAGE = True
ACTION_WITH_HASARD = True
#Paramètres de l'IA par renforcement
# learning param
DEFAULT_LEARNING_RATE = 0.01
DEFAULT_DISCOUNT_FACTOR = 0.2

GAME_SPEED = 1.05
GAME_LENGHT = 4
IA_NB_TOURS = 5


#game state schema
'''    0 1 2 3
     0 | | | |
     1 | | | | 
     2 | | | |
     3 | | | |
     
     | = {2^0, ....2^11}
'''
# actions values
UP = 'U'
DOWN = 'D'
LEFT = 'L'
RIGHT = 'R'
ACTIONS = ['U', 'D', 'L', 'R']
#OTHER_ACTIONS = ['Y'N'] # N = no action

#game reward

REWARD_GOAL = 2048

REWARD_DEFAULT = 1 # score state
REWARD_GAMEOVER = -100
REWARD_NO_EFFECT = -8

# LIST_ACTIONS_EXEMPLE = [UP, UP, UP, DOWN, LEFT, RIGHT, LEFT, DOWN, UP]

#Generer Aleatoirement
GENERATED_VALUES = [2, 4] 
#TODO: Générer aléatoirement avec une fréquence plus importante pour le 2 ?

    #Generer Aleatoirement la valeur entre les nombres de la liste GENERATED_VALUES
def randomValue():
    return random.choice(GENERATED_VALUES)
    #Generer Aleatoirement pour les coordonnées de la case contenant les valeurs
def randomXY(lenght):
    return random.choice(range(lenght))

    #Generer Aleatoirement pour le Action à effectuer par l'IA 
    # / pour simuler des acyions à la place du joueur
def generateDefaultAction():
    return random.choice(ACTIONS)




