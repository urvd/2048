# import math
# from sklearn.neural_network import MLPRegressor
# import numpy as np
import random

from game_params import generateDefaultAction, LEARNING_RATE, \
    DISCOUNT_FACTOR, EXPLORATION


class LearningPolicy: #Q-table
    def __init__(self, states_sign, actions, game_lenght, learning_rate=LEARNING_RATE,
                 discount_factor=DISCOUNT_FACTOR, exploration=EXPLORATION):
        # Q-table indexée directement par la signature de l'état : accès en O(1)
        # et aucune limite sur le nombre d'états rencontrés.
        self.qtable = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration = exploration
        self.actions = actions
        self._chosensActions = None
        self.nb_successif_overload_action = 0
        self.cas_total = 0
        self.state_cas = 0
        self._add_state(states_sign)

    def _add_state(self, state):
        """Ajoute l'état à la Q-table s'il est nouveau. Renvoie True si l'état a été ajouté."""
        if state in self.qtable:
            return False
        self.qtable[state] = dict.fromkeys(self.actions, 0)
        return True

    def __repr__(self):
        res = ''
        for state in self.qtable:
            res += f'{state}\t{self.qtable[state]}\n'
        return res

    def get_listedActions(self):
        list = self._chosensActions
        return list

    def best_action(self, state, last_reward_overload_noaction, start=False):
        if start is True:
            self._chosensActions = ''

        if state in self.qtable:
            if last_reward_overload_noaction is True:
                self.nb_successif_overload_action += 1
                c = generateDefaultAction()
                self._chosensActions += c + '(*) '
                # if self.nb_successif_overload_action == 2:
                #     return ACTIONS[self.nb_successif_overload_action-1]
                # return ACTIONS[0]'
                return c

            # Exploration : de temps en temps un coup au hasard, noté (e)
            if random.random() < self.exploration:
                c = generateDefaultAction()
                self._chosensActions += c + '(e) '
                return c

            # Meilleure action ; en cas d'égalité (ex. état jamais appris, tout à 0),
            # tirage au hasard parmi les meilleures au lieu de toujours la même direction
            q_state = self.qtable[state]
            meilleure_valeur = max(q_state.values())
            action = random.choice(sorted(a for a, q in q_state.items() if q == meilleure_valeur))

            self._chosensActions += action + '(' + str(q_state[action]) + ') '
            return action
        else:
            self._add_state(state)
            self.state_cas += 1
            c = generateDefaultAction()
            self._chosensActions += c + '(*) '
            return c

    def update(self, previous_state, state, last_action, reward):
        # Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        if self._add_state(state):
            self.state_cas += 1
        self._add_state(previous_state)
        self.cas_total += 1
        q_previous = self.qtable[previous_state]
        maxQ = max(self.qtable[state].values())
        q_previous[last_action] += self.learning_rate * (reward + self.discount_factor * maxQ - q_previous[last_action])


