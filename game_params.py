import os
import random

#game parameters
GAME_SPEED = float(os.getenv("SIMU_INTERVAL_SPEED","0.01"))
GAME_LENGHT = 4
IA_NB_TOURS = 5

 # si false on peut passer on peut jouer en mode joueur
MODE_APPRENTISSAGE = os.getenv("MODE_APPRENTISSAGE", "false").casefold() == "true"
#ACTION_WITH_HASARD = True

#Paramètres de l'IA par renforcement
## learning param
DEFAULT_LEARNING_RATE = 0.01
DEFAULT_DISCOUNT_FACTOR = 0.2



##IA game reward
 # score state
REWARD_DEFAULT = int(os.getenv("REWARD_DEFAULT", "1"))

REWARD_GOAL = int(os.getenv("REWARD_GOAL", "2048"))
REWARD_GAMEOVER = int(os.getenv("REWARD_GAMEOVER", "-100"))
REWARD_NO_EFFECT = int(os.getenv("REWARD_NO_EFFECT", "-8"))

# Game state schema
'''    0 1 2 3
     0 | | | |
     1 | | | | 
     2 | | | |
     3 | | | |
     
     | = {2^0, ....2^11}
'''
# Actions values
UP = 'U'
DOWN = 'D'
LEFT = 'L'
RIGHT = 'R'
ACTIONS = ['U', 'D', 'L', 'R']
#OTHER_ACTIONS = ['Y'N'] # N = no action



# LIST_ACTIONS_EXEMPLE = [UP, UP, UP, DOWN, LEFT, RIGHT, LEFT, DOWN, UP]

# Game generated  values
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




