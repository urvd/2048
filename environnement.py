from copy import copy

from case_de_tableaux import Case
from game_methodes import UpActionImpl, DownActionImpl, LeftActionImpl, RightActionImpl
from game_params import *


class Environment:
    def __init__(self, length):
        self.length = length
        self.set()

    def reset(self):
        self.set(self.length)

    def set(self, length=4):
        self.states = {}
        self.score = 0
        self._reward = 0
        self._reward_noaction_overload = 0
        print('2048 de taille ' + str(length))
        c1_init = Case(randomXY(length), randomXY(length), 2)
        c2_init = Case(randomXY(length), randomXY(length), 2)

        while (c1_init == c2_init):
            c1_init.set(randomXY(length), randomXY(length), 2)
            c2_init.set(randomXY(length), randomXY(length), 2)
        # c1_init.set(0, 0, 2)
        # c2_init.set(3, 0, 2)
        for row in range(self.length):
            for col in range(self.length):
                if c1_init.x == row and c1_init.y == col:
                    self.states[(row, col)] = c1_init.value

                elif c2_init.x == row and c2_init.y == col:
                    self.states[(row, col)] = c2_init.value
                else:
                    self.states[(row, col)] = 0

        print('c1 generated: ' + c1_init.toString())
        print('c2 generated ' + c2_init.toString())

        self.previous_states = {}

        self.empty_case_count = 0
        self.empty_case_states = {}

    def count_empty_cases(self):
        count = 0
        for row in range(self.length):
            for col in range(self.length):
                if self.states[(row, col)] == 0:
                    self.empty_case_states[count] = Case(row, col, self.states[(row, col)])
                    count = count + 1
        #self.empty_case_count = count
        return count

    def count_empty_casesOf(self, state):
        count = 0
        for row in range(self.length):
            for col in range(self.length):
                if state[(row, col)] == 0:
                    count = count + 1
        return count

    def _generate_random_new_case(self, bncase = 2):
        newValue = randomValue()
        empty_case_indice = randomXY(len(self.empty_case_states))
        randomX = self.empty_case_states[empty_case_indice].x
        randomY = self.empty_case_states[empty_case_indice].y

        self.states[randomX, randomY] = newValue
    def is_same_as(self, otherstates):
        for row in range(0,self.length):
            for col in range(0, self.length):
                if not self.states[(row, col)] == otherstates[(row, col)]:
                    return False
        return True
    def get_current_reward(self):
        return  self._reward

    def is_current_reward_overloaded(self):
        if self._reward == REWARD_NO_ACTION:
            self._reward_noaction_overload += self._reward
        else:
            self._reward_noaction_overload = 0

        return self._reward_noaction_overload <= REWARD_NO_ACTION

    def calcul_reward_attribution(self):
        max = 0
        fixedmax = max
        count = 0
        for row in range(0, self.length):
            for col in range(0, self.length):

                if self.states[(row, col)] == REWARD_GOAL and max < REWARD_GOAL:
                    max = REWARD_GOAL
                if self.states[(row, col)] == REWARD1024 and max < REWARD1024:
                    max = REWARD1024
                if self.states[(row, col)] == REWARD512 and max < REWARD512:
                    max = REWARD512
                if self.states[(row, col)] == REWARD256 and max < REWARD256:
                    max = REWARD256
                if self.states[(row, col)] == REWARD128 and max < REWARD128:
                    max = REWARD128
                if self.states[(row, col)] == REWARD64 and max < REWARD64:
                    max = REWARD64
                if self.states[(row, col)] == REWARD32 and max < REWARD32:
                    max = REWARD32
                if self.states[(row, col)] == REWARD16 and max < REWARD16:
                    max = REWARD16
                if self.states[(row, col)] == REWARD8 and max < REWARD8:
                    max = REWARD8
                if self.states[(row, col)] == REWARD4 and max < REWARD4:
                    max = REWARD4
                if self.states[(row, col)] == REWARD2 and max < REWARD2:
                    max = REWARD2

                if max is not fixedmax:
                    fixedmax = max
                    count = 1
                else:
                    count += 1

        return [max, count]


    def apply(self, action):
        if action == UP or action == DOWN or action == RIGHT or action == LEFT:
            action_applied = None
            # apply_action
            if action == UP:
                action_applied = UpActionImpl(current_states=copy(self.states), lenght=self.length)
            elif action == DOWN:
                action_applied = DownActionImpl(current_states=copy(self.states), lenght=self.length)
            elif action == LEFT:
                action_applied = LeftActionImpl(current_states=copy(self.states), lenght=self.length)
            elif action == RIGHT:
                action_applied = RightActionImpl(current_states=copy(self.states), lenght=self.length)



            if self.is_same_as(action_applied.get_states()) is False:
                self.previous_states = self.states
                self.states = action_applied.get_states()
                self.score = action_applied.get_score()
                # generate new case
                if self.count_empty_cases() != 0:
                    self._generate_random_new_case()
                    if self.count_empty_cases() == 0:
                        self._reward = REWARD_GAMEOVER

                if (self._reward != REWARD_GAMEOVER):
                    calcul = self.calcul_reward_attribution()
                    # reward default = score de case merger + case la plus grande * nb de apparition de la case max
                    self._reward = self.score + calcul[0] * calcul[1]
            else:
                self._reward = REWARD_NO_ACTION




    def get_state(self):
        res = ''
        for col in range(self.length):
            for row in range(self.length):
                    res += '(' + str(row) + ',' + str(col) + ')=>' + str(self.states[(row, col)])
        return res

    def get_pre_state(self):
        res = ''
        for col in range(self.length):
            for row in range(self.length):
                res += '(' + str(row) + ',' + str(col) + ')=>' + str(self.previous_states[(row, col)])
        return res

    def show(self):
        for col in range(self.length):
            res = ''
            for row in range(self.length):
                if (row == self.length - 1):
                    res += '| ' + str(self.states[(row, col)]) + ' |'
                else:
                    res += '| ' + str(self.states[(row, col)]) + ' '

            print(res + '\n')


