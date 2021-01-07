import random
from copy import copy

from agent import Agent
from environnement import Environment
from game_params import DEFAULT_LEARNING_RATE, REWARD_GAMEOVER, IA_NB_TOURS, GAME_LENGHT, MODE_APPRENTISSAGE
from learning_policy import LearningPolicy

class Summary:
    def __init__(self, tours):
        self.nb_tours = tours
        self.etapes = []
        self.scores = []
        self.chain_actions = []
        self.current_tours = 0
        self.current_etape = 0
    def add(self, score, chain_actions):
        # i; etape  score actions
        self.etapes.append(self.current_etape)
        self.scores.append(score)
        self.chain_actions.append(chain_actions)
    def show(self):
        res = ''
        for i in range(0, self.nb_tours):
            res += 'tours: '+ str(i+1) + '. Joué en '+ str(self.etapes[i]) + ' étapes. Score: '+ str(self.scores[i]) + '.\n'\
            'Enchainement d\'actions: '+ self.chain_actions[i] + '\n\n'

        return  res







    #TODO: resoudre bug qui s'affiche une fois de temps en temps
    #TODO: Optimisation IA => amélioré la diversité des appels d'action
    #TODO: Optimisation IA => adapter avec réseaux de neurones.

    #TODO: ADAPATER LE JEUX AVEC UNE BBTHEQUE GRAPHIQUE


if __name__ == '__main__':

    #Initialiser l'environment
    plateaux = Environment(GAME_LENGHT)
    # Initialiser l'agent
    agent = Agent(plateaux)

    nbtours = IA_NB_TOURS
    summary = Summary(nbtours)
    summary.current_tours = 0

    while (summary.current_tours < nbtours):
        #Initialiser le 1ere Etat
        summary.current_etape = 0
        agent.show(init=True)
        # Tant que l'environement n'a pas toute ses cases pleines.
        continu = True

        while(continu):
            print("Tours numero : " + str(summary.current_tours + 1))
            print('ETAPE: ', summary.current_etape + 1, '\n')
            #Calul = Enregistre l'action de l'agent
            # et Changer l'état du jeu
            agent.do()
            #Afficher du jeu en cours et le score et met a jours la table d'apprentissage
            agent.show()
            continu = agent.continue_game()
            if not continu:
                summary.add(agent.state_score, agent.getListActions())
                agent.show_last_and_best_score()
                agent.reset()
            summary.current_etape += 1

        summary.current_tours += 1

    print(summary.show())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
