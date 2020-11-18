import math

#action_left_limit
from copy import copy

from case_de_tableaux import Case

# def show(states, len):
#     for col in range(len):
#         res = ''
#         for row in range(len):
#             if (row == len - 1):
#                 res += '| ' + str(states[(row, col)]) + ' |'
#             else:
#                 res += '| ' + str(states[(row, col)]) + ' '
#
#         print(res + '\n')
 
# def left_limit_action(x,y,taille):
#     return x == 0 and y in range(0, taille-1);
# 
# def right_limit_action(x,y,taille):
#     return x == taille-1 and y in range(0, taille-1);
# 
# def up_limit_action(x,y,taille):
#     return x in range(0, taille-1) and y == 0;
# 
# def down_limit_action(x,y,taille):
#     return x in range(0, taille-1) and y == taille-1;

    # get first empty state of line or column
def first_state_emptyY(current,indiceFixe,taille, inverse = False):
    if not inverse:
        for var in range(0, taille):
            if current[(indiceFixe, var)] == 0:
                return Case(indiceFixe, var, current[(indiceFixe, var)])
    else:
        for var in reversed(range(0, taille)):
            if current[(indiceFixe, var)] == 0:
                return Case(indiceFixe, var, current[(indiceFixe, var)])
    return None

def first_state_emptyX(current,indiceFixe,taille, inverse = False):
    if not inverse:
        for var in range(0, taille):
            if current[(var, indiceFixe)] == 0:
                return Case(var, indiceFixe, current[(var, indiceFixe)])
    else:
        for var in reversed(range(0, taille)):
            if current[(var, indiceFixe)] == 0:
                return Case(var, indiceFixe, current[(var, indiceFixe)])
    return None

# def getIndice(i, len):
#     calc = len - (len - (i+1))
#     return calc - 1

    ## Actions
class ActionImpl:
    def __init__(self, current_states, lenght):
        self.current_states = current_states
        self.lenght = lenght
        self.score = 0
        self.apply_action()
        self.no_mergable_case = True
    def get_states(self):
        return self.current_states
    def get_score(self):
        return self.score

    def _merge_states(self):
        self._merge_states()
    def _decale_states(self):
        self._decale_states()
    def apply_action(self):
        # decaler
        self._decale_states()
        # merger
        self._merge_states()
        # decaler
        self._decale_states()

class UpActionImpl(ActionImpl):

    def _merge_states(self):
        for x in range(0, self.lenght):
            for y in range(0, self.lenght - 1):
                if self.current_states[(x, y)] == self.current_states[(x, y + 1)] and not self.current_states[
                                                                                              (x, y)] == 0:
                    self.current_states[(x, y)] *= 2
                    self.current_states[(x, y + 1)] = 0
                    self.score += self.current_states[(x, y)]
                    self.no_mergable_case = False
        # print(" > merger\n")
        # show(self.current_states, self.lenght)

    def _decale_states(self):
        for x in range(0, self.lenght):
            for y in range(self.lenght):
                empty_state = first_state_emptyY(self.current_states, x, self.lenght)
                if empty_state is not None and empty_state.y < y and not self.current_states[(x, y)] == 0:
                    self.current_states[(empty_state.x, empty_state.y)] = self.current_states[(x, y)]
                    self.current_states[(x, y)] = 0
        # print(" > decaler\n")
        # show(self.current_states, self.lenght)

class DownActionImpl(ActionImpl):

    def _merge_states(self):
        for x in range(0, self.lenght):
            for y in reversed(range(1, self.lenght)):
                if self.current_states[(x, y)] == self.current_states[(x, y - 1)] \
                        and not self.current_states[(x, y)] == 0:

                    self.current_states[(x, y)] *= 2
                    self.current_states[(x, y - 1)] = 0
                    self.score += self.current_states[(x, y)]
                    self.no_mergable_case = False
        # print(" > merger\n")
        # show(self.current_states, self.lenght)

    def _decale_states(self):
        for x in range(0, self.lenght):
            for y in reversed(range(0, self.lenght)):
                empty_state = first_state_emptyY(self.current_states, x, self.lenght, True)
                if empty_state is not None and empty_state.y > y and not self.current_states[(x, y)] == 0:
                    self.current_states[(empty_state.x, empty_state.y)] = self.current_states[(x, y)]
                    self.current_states[(x, y)] = 0
        # print(" > decaler\n")
        # show(self.current_states, self.lenght)

class LeftActionImpl(ActionImpl):

    def _merge_states(self):
        for y in range(0, self.lenght):
            for x in range(0, self.lenght - 1):
                if self.current_states[(x, y)] == self.current_states[(x + 1, y)] \
                        and not self.current_states[(x, y)] == 0:
                    self.current_states[(x, y)] *= 2
                    self.current_states[(x + 1, y)] = 0
                    self.score += self.current_states[(x, y)]
                    self.no_mergable_case = False

        # print(" > merger\n")
        # show(self.current_states, self.lenght)
    def _decale_states(self):
        for y in range(0, self.lenght):
            for x in range(0, self.lenght):
                empty_state = first_state_emptyX(self.current_states, y, self.lenght)
                if empty_state is not None and empty_state.x < x and not self.current_states[(x, y)] == 0:
                    self.current_states[(empty_state.x, empty_state.y)] = self.current_states[(x, y)]
                    self.current_states[(x, y)] = 0
        # print(" > decaler\n")
        # show(self.current_states, self.lenght)

class RightActionImpl(ActionImpl):

    def _merge_states(self):
        for y in range(0, self.lenght):
            for x in reversed(range(1, self.lenght)):
                if self.current_states[(x, y)] == self.current_states[(x - 1, y)] \
                        and not self.current_states[(x, y)] == 0:
                    self.current_states[(x, y)] *= 2
                    self.current_states[(x - 1, y)] = 0
                    self.score += self.current_states[(x, y)]
                    self.no_mergable_case = False
        # print(" > merger\n")
        # show(self.current_states, self.lenght)
    def _decale_states(self):
        for y in range(0, self.lenght):
            for x in reversed(range(0, self.lenght)):
                empty_state = first_state_emptyX(self.current_states, y, self.lenght, True)
                if empty_state is not None and empty_state.x > x and not self.current_states[(x, y)] == 0:
                    self.current_states[(empty_state.x, empty_state.y)] = self.current_states[(x, y)]
                    self.current_states[(x, y)] = 0
        # print(" > decaler\n")
        # show(self.current_states, self.lenght)

