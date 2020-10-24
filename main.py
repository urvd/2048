import random

from environnement import Environment
from game_params import ACTIONS, list_actions_examples

GAME_PROCESS = 'GAME_PROCESS' #  VERIFIER SI l\'état du jeu est en cours et Addtion du score
GAME_OVER = 'GAME_OVER' # VERIFIER SI  toutes les case sont remplit et recupère son score.
GAME_SUCCES = 'GAME_SUCCES' # VERIFIER QUAND  une case de l'etat de l'environemment  contient = 2048
                            # alors l'environnement s'arrete,  et recupère son score min

REWARD_GOAL = GAME_SUCCES #Si une case de l'etat de l'environemment est = 2048
REWARD_DEFAULT = GAME_PROCESS# Methode qui met à jours l'état avec les valeurs des cases et le score
REWARD_STUCK = GAME_OVER
#TODO: CODER et IMPL LES RECOMPENSES


class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.state = environment.states
        #
        self.previous_state = self.environment.previous_states
        ##self.policy = Policy(environment.states.keys(), ACTIONS)
        self.final_score = 0
        self.continu = False

    def continue_game(self):
        self.continu = self.environment.count_empty_cases() != 0
        if self.continu == False :
            #TODO : reinitialiser le jeu
            1+1
        else:
            self.previous_state = self.environment.previous_states
            self.state = self.environment.states
        return self.continu

    def show_last_and_best_score(self):
        if self.environment.current_score > self.final_score:
            self.final_score = self.environment.current_score
        if self.final_score != 0:
            print('\n #Meilleur score: ', self.final_score)
        print('\n #Dernier score atteint: ', self.environment.current_score)

    def getBestAction(self, action):
        # TODO: CODER ET IMPL L'algo d'apprentissage du jeux
        #Calcul de la meilleur actions à réaliser selon l'état en cours du jeux de l'environnement
        print('#Action: ', action, '\n')
        self.environment.apply(action)

    def show(self):
        print(' #Score: ' + str(self.environment.current_score) + '\n')
        self.environment.show()

    #TODO: IMPL A CHAQUE ETAT de l'environnement, generer une case aléatoirement parmis ceux qui sont vide.

    #TODO: ADAPATER LE JEUX AVEC UNE BBTHEQUE GRAPHIQUE

if __name__ == '__main__':

    #Initialiser l'environment
    plateaux = Environment(4)
    # Initialiser l'agent
    agent = Agent(plateaux)

    #Initialiser le 1ere Etat

    i = 0
    print('Etape: ', i, 'avec ', str(len(list_actions_examples)) ,' actions dispo\n')
    agent.show()
    # Tant que l'environement n'a pas toute ses cases pleines.
    continu = True;

    """or continu"""
    while(i <= len(list_actions_examples)-1 ):
        print('ETAPE: ',i+1,'\n')
        #Calul = Enregistre l'action de l'agent
        agent.getBestAction(list_actions_examples[i]);
        # et Changer l'état du jeu

        #Afficher du jeu en cours et le score
        agent.show()
        continu = agent.continue_game()
        i += 1
        if not continu or i == len(list_actions_examples):
            agent.show_last_and_best_score()


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
