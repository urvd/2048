from case_de_tableaux import Case
from game_methodes import up_action_applied, down_action_applied, left_action_applied, right_action_applied
from game_params import randomXY, ACTIONS, UP, DOWN, RIGHT, LEFT, randomValue

class Environment:
    def __init__(self, length):
        self.states = {}
        self.length = length
        self.height = length
        self.width = length
        print('2048 de taille ' + str(length))
        c1_init = Case(randomXY(length), randomXY(length), 2)
        c2_init = Case(randomXY(length), randomXY(length), 2)

        while(c1_init == c2_init):
            c1_init.set(randomXY(length), randomXY(length), 2)
            c2_init.set(randomXY(length), randomXY(length), 2)

        c1_init.set(1, 3, 2)
        c2_init.set(3, 1, 2)
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
        count = 0;
        for row in range(self.height):
            for col in range(self.width):
                if self.states[(row, col)] == 0:
                    self.empty_case_states[count] = Case(row, col, self.states[(row, col)])
                    count = count + 1
        #self.empty_case_count = count
        return count;

    # def continue_game(self):
    #     isPlein = False
    #     for row in range(self.height):
    #         for col in range(self.width):
    #             if self.states[(row, col)].value == 0:
    #                 return True;
    #     return False;
    def _generate_random_new_case(self): #TODO : a améliorer/optimizer
        newValue = randomValue()
        empty_case_indice = randomXY(len(self.empty_case_states))
        randomX = self.empty_case_states[empty_case_indice].x
        randomY = self.empty_case_states[empty_case_indice].x

        self.states[randomX, randomY] = newValue

    def apply(self, action):
        if action == UP or action == DOWN or action == RIGHT or action == LEFT:
            self.previous_states = self.states
            # apply_action
            if action == UP:
                self.states = up_action_applied(self.states, self.height)
            elif action == DOWN:
                self.states = down_action_applied(self.states, self.height)
            elif action == LEFT:
                self.states = left_action_applied(self.states, self.height)
            elif action == RIGHT:
                self.states = right_action_applied(self.states, self.height)

            # generate new case
            if self.count_empty_cases() != 0: #TODO/ IF STATE DON'T change don't generate
                self._generate_random_new_case()

    def show(self):
        for col in range(self.height):
            res = ''
            for row in range(self.width):
                if (row == self.width - 1):
                    res += '| ' + str(self.states[(row, col)]) + ' |'
                else:
                    res += '| ' + str(self.states[(row, col)]) + ' '

            print(res + '\n')


