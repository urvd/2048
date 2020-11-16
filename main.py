import random
from copy import copy

from environnement import Environment
from game_params import list_actions_examples, ACTIONS, DOWN, RIGHT, LEFT, UP, DEFAULT_LEARNING_RATE
from learning import LearningPolicy

class Summary:
    def __init__(self, tours):
        self.nb_tours = tours
        self.etapes = []
        self.scores = []
        self.chain_actions = []
    def add(self, etape, score, chain_actions):
        # i; etape  score actions
        self.etapes.append(etape)
        self.scores.append(score)
        self.chain_actions.append(chain_actions)
    def show(self):
        res = ''
        for i in range(self.nb_tours):
            res = 'tours: '+ str(i+1) + '. Joué en '+ str(self.etapes[i]) + '. Score: '+ str(self.scores[i]) + '.\n'\
            'Enchainement d\'actions: '+ self.chain_actions[i] + '\n'


class Agent:
    def __init__(self, environment):
        self.environment = environment
        # self.state = environment.states
        # self.previous_state = self.environment.previous_states
        self.last_action = None
        self.learning_policy = LearningPolicy(states_sign=self.environment.get_state(), \
                                              actions={'U', 'D', 'L', 'R'}, \
                                              game_lenght=self.environment.length, \
                                              learning_rate=DEFAULT_LEARNING_RATE)
        self.list_action = ''
        self.state_score = 0
        self.final_score = 0
        self.continu = False

    def continue_game(self):
        return self.continu

    def show_last_and_best_score(self):
        if self.state_score > self.final_score:
            self.final_score = self.state_score
        if self.final_score != 0:
            print('\n #Meilleur score: ', self.final_score)
        print('\n #Dernier score atteint: ', self.state_score)

        self.state_score = 0
        self.last_action = None
    def reset(self):
         self.environment.reset()

    def do(self):
        # TODO: CODER ET IMPL L'algo d'apprentissage du jeux
        #Calcul de la meilleur actions à réaliser selon l'état en cours du jeux de l'environnement
        if self.last_action == None:
            self.last_action = self.learning_policy.best_action(self.environment.get_state(),\
                                        last_reward_overload_noaction=False,\
                                                            start=True)
        self.last_action = self.learning_policy.best_action(self.environment.get_state(),\
                                        last_reward_overload_noaction=self.environment.is_current_reward_overloaded())

        list_action = ' '+ self.last_action
        print('#Action: ', self.last_action, '\n')
        self.environment.apply(self.last_action)
        self.previous_state = self.environment.previous_states
        self.state = self.environment.states
        self.state_score += self.environment.score

    def getListActions(self):
        return self.learning_policy.get_listedActions()

    def show(self, init=False):
        print(' #Score: ' + str(self.state_score) + '\n')
        self.environment.show()
        self.continu = self.environment.count_empty_cases() != 0
        last_score = self.environment.score
        if not init:
            self.learning_policy.update(previous_state=self.environment.get_pre_state(), \
                                        state=self.environment.get_state(), last_action=self.last_action,\
                                        reward=self.environment.get_current_reward())

    #TODO: ADAPATER LE JEUX AVEC UNE BBTHEQUE GRAPHIQUE

if __name__ == '__main__':

    #Initialiser l'environment
    plateaux = Environment(4)
    # Initialiser l'agent
    agent = Agent(plateaux)

    nbtours = 6
    summary = Summary(nbtours)
    rejouer = 0

    while (rejouer < nbtours):
        #Initialiser le 1ere Etat
        i = 0
        agent.show(init=True)
        # Tant que l'environement n'a pas toute ses cases pleines.
        continu = True

        """or continu"""
        while(continu):
            print('ETAPE: ', i+1, '\n')
            #Calul = Enregistre l'action de l'agent
            agent.do()
            # et Changer l'état du jeu

            #Afficher du jeu en cours et le score et met a jours la table d'apprentissage
            agent.show()
            continu = agent.continue_game()
            if not continu:
                summary.add(i, agent.state_score, agent.getListActions())
                agent.show_last_and_best_score()
                agent.reset()
            i += 1

        rejouer += 1

    summary.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
