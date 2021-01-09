# import math
# from sklearn.neural_network import MLPRegressor
# import numpy as np
from copy import copy
from game_params import generateDefaultAction, UP, DOWN, LEFT, RIGHT, ACTIONS


class LearningPolicy: #Q-table
    def __init__(self, states_sign, actions, game_lenght, learning_rate=0.9, discount_factor=0.5):
        self.listOfStates = []
        self.qtable = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.state_lenght = (game_lenght * game_lenght) * (2**11)
        self.actions = actions
        self._chosensActions = None
        self.nb_successif_overload_action = 0
        self.listOfStates.append(states_sign)

        #creer la Qtable de base || recuperer d'un fichier
        for sid in range(self.state_lenght):
            self.qtable[sid] = {}
            for a in self.actions:

                self.qtable[sid][a] = 0

        self.state_cas = 0

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

        action = None

        if state in self.listOfStates:
            if last_reward_overload_noaction is True:
                self.nb_successif_overload_action += 1
                c = generateDefaultAction()
                self._chosensActions += c + '(*) '
                # if self.nb_successif_overload_action == 2:
                #     return ACTIONS[self.nb_successif_overload_action-1]
                # return ACTIONS[0]'
                return c

            index = self.listOfStates.index(state)
            for a in self.qtable[index]:
                if action is None or self.qtable[index][a] >= self.qtable[index][action]:
                    action = a

            self._chosensActions += action + '(' + str(copy(self.qtable[index][action])) + ') '
            return action
        else:
            self.listOfStates.append(state)
            self.state_cas += 1
            c = generateDefaultAction()
            self._chosensActions += c + '(*) '
            return c

    def update(self, previous_state, state, last_action, reward):
        # Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        if state not in self.listOfStates:
            self.listOfStates.append(state)
            self.state_cas += 1
        # a = previous_state == self.listOfStates[0]
        # b = previous_state == self.listOfStates[1]
        index = self.listOfStates.index(previous_state)
        maxQ = max(self.qtable[self.listOfStates.index(state)].values())
        self.qtable[index][last_action] += self.learning_rate * \
            (reward + self.discount_factor * maxQ - self.qtable[index][last_action])


