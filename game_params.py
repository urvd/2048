import os
import random
from pathlib import Path

# Charge le fichier .env placé à côté du code, quel que soit le dossier de lancement.
# Les variables déjà définies dans le terminal restent prioritaires.
try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv absent : seules les variables du terminal sont lues
    load_dotenv = None
if load_dotenv is not None:
    load_dotenv(Path(__file__).resolve().with_name(".env"))


def env_bool(nom, defaut):
    """Lit une variable oui/non : true, True, 1, oui, yes, vrai (sans tenir compte des espaces)."""
    valeur = os.getenv(nom)
    if valeur is None or not valeur.strip():
        return defaut
    return valeur.strip().strip('"\'').casefold() in ("true", "1", "oui", "yes", "vrai")


#game parameters
GAME_SPEED = float(os.getenv("SIMU_INTERVAL_SPEED","0.01"))
GAME_LENGHT = int(os.getenv("GAME_LENGHT", "4"))
NB_TOURS_MAX =  int(os.getenv("NB_TOURS_MAX", "50"))

 # si false on peut passer on peut jouer en mode joueur
MODE_APPRENTISSAGE = env_bool("MODE_APPRENTISSAGE", False)
#ACTION_WITH_HASARD = True

#Paramètres de l'IA par renforcement
## learning param
LEARNING_RATE = float(os.getenv("DEFAULT_LEARNING_RATE", "0.01"))
DISCOUNT_FACTOR = float(os.getenv("DEFAULT_DISCOUNT_FACTOR", "0.2"))
# Exploration (epsilon-greedy) : part des coups joués au hasard pour découvrir d'autres actions
EXPLORATION = min(max(float(os.getenv("EXPLORATION", "0.1")), 0.0), 1.0)

##IA game reward
 # score state
REWARD_DEFAULT = int(os.getenv("REWARD_DEFAULT", "1"))

REWARD_GOAL = int(os.getenv("REWARD_GOAL", "2048"))
REWARD_GAMEOVER = int(os.getenv("REWARD_GAMEOVER", "-100"))
REWARD_NO_EFFECT = int(os.getenv("REWARD_NO_EFFECT", "-8"))


def recompenses_par_defaut():
    """Récompenses de l'IA définies dans le .env (ou valeurs par défaut)."""
    return {
        "default": REWARD_DEFAULT,
        "goal": REWARD_GOAL,
        "gameover": REWARD_GAMEOVER,
        "no_effect": REWARD_NO_EFFECT,
    }

#Mémoire de l'IA entre les parties
# Approche 1 : choisir learning_rate et discount_factor d'après le CSV des parties
OPTIMISER_PARAMETRES = env_bool("OPTIMISER_PARAMETRES", True)
# Approche 2 : sauvegarder la Q-table en fin de partie et la recharger au lancement
QTABLE_PERSISTANTE = env_bool("QTABLE_PERSISTANTE", True)

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




