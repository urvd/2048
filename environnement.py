from copy import copy

from case_de_tableaux import Case
from game_methodes import UpActionImpl, DownActionImpl, LeftActionImpl, RightActionImpl
from game_params import randomXY, UP, DOWN, RIGHT, LEFT, randomValue, REWARD_NO_ACTION, REWARD_GAMEOVER

class Environment:
    def __init__(self, length):
        self.states = {}
        self.length = length
        self.height = length
        self.width = length
        self.score = 0
        self._reward = 0
        self._reward_noaction_overload = 0
        print('2048 de taille ' + str(length))
        c1_init = Case(randomXY(length), randomXY(length), 2)
        c2_init = Case(randomXY(length), randomXY(length), 2)

        while(c1_init == c2_init):
            c1_init.set(randomXY(length), randomXY(length), 2)
            c2_init.set(randomXY(length), randomXY(length), 2)
        c1_init.set(0, 0, 2)
        c2_init.set(3, 0, 2)
        for row in range(self.height):
            for col in range(self.width):
                if c1_init.x == row and c1_init.y == col:
                    self.states[(row, col)] = c1_init.value
                    print('c1 generated: ' + c1_init.toString())

                elif c2_init.x == row and c2_init.y == col:
                    self.states[(row, col)] = c2_init.value
                    print('c2 generated ' + c2_init.toString())
                else:
                    self.states[(row, col)] = 0

        #self.starting_point = self.states
        #self.new_states = None
        self.previous_states = {}

        self.empty_case_count = 0;
        self.empty_case_states = {};

    def count_empty_cases(self):
        count = 0
        for row in range(self.height):
            for col in range(self.width):
                if self.states[(row, col)] == 0:
                    self.empty_case_states[count] = Case(row, col, self.states[(row, col)])
                    count = count + 1
        #self.empty_case_count = count
        return count

    def _generate_random_new_case(self):
        newValue = randomValue()
        empty_case_indice = randomXY(len(self.empty_case_states))
        randomX = self.empty_case_states[empty_case_indice].x
        randomY = self.empty_case_states[empty_case_indice].x

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

        return self._reward_noaction_overload < REWARD_NO_ACTION

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
                self._reward = self.score # reward default
                # generate new case
                if self.count_empty_cases() != 0:
                    self._generate_random_new_case()
                else:
                    self._reward = REWARD_GAMEOVER
            else:
                self._reward = REWARD_NO_ACTION

    def get_state(self):
        res = ''
        for col in range(self.length):
            for row in range(self.length):
                    res += '(' + str(row) + ',' + str(col) + ')=>' + str(self.states[(row, col)]) + '/\t'
            res += "\n"
        return res

    def get_pre_state(self):
        res = ''
        for col in range(self.length):
            for row in range(self.length):
                res += '(' + str(row) + ',' + str(col) + ')=>' + str(self.previous_states[(row, col)]) + '/\t'
            res += "\n"
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


