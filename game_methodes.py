import math

#action_left_limit
from copy import copy

from case_de_tableaux import Case


def show(states, len):
    for col in range(len):
        res = ''
        for row in range(len):
            if (row == len - 1):
                res += '| ' + str(states[(row, col)]) + ' |'
            else:
                res += '| ' + str(states[(row, col)]) + ' '

        print(res + '\n')

def left_limit_action(x,y,taille):
    return x == 0 and y in range(0, taille-1);

def right_limit_action(x,y,taille):
    return x == taille-1 and y in range(0, taille-1);

def up_limit_action(x,y,taille):
    return x in range(0, taille-1) and y == 0;

def down_limit_action(x,y,taille):
    return x in range(0, taille-1) and y == taille-1;

#get first empty state of line or column
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

def getIndice(i, len):
    calc = len - (len - (i+1))
    return calc - 1


def up_action_applied(current_states, taille_game):
    # decaler
    for x in range(0, taille_game):
        for y in range(taille_game):
            empty_state = first_state_emptyY(current_states, x, taille_game)
            if empty_state is not None and empty_state.y < y and not current_states[(x, y)] == 0:
                current_states[(empty_state.x, empty_state.y)] = current_states[(x, y)]
                current_states[(x, y)] = 0
    print(" > decaler\n")
    show(current_states, taille_game)
    # merger
    for x in range(0, taille_game):
        for y in range(0, taille_game - 1):
            if current_states[(x, y)] == current_states[(x, y + 1)] and not current_states[(x, y)] == 0:
                current_states[(x, y)] *= current_states[(x, y)]
                current_states[(x, y + 1)] = 0
    print(" > merger\n")
    show(current_states, taille_game)
    return current_states


def down_action_applied(current_states, taille_game):
    next_states = []
    # decaler
    for x in range(0, taille_game):
        for y in reversed(range(0, taille_game)):
            empty_state = first_state_emptyY(current_states, x, taille_game, True)
            if empty_state is not None and empty_state.y > y and not current_states[(x, y)] == 0:
                current_states[(empty_state.x, empty_state.y)] = current_states[(x, y)]
                current_states[(x, y)] = 0
    print(" > decaler\n")
    show(current_states, taille_game)
    # merger
    for x in range(0, taille_game):
        for y in reversed(range(1, taille_game)):
            if current_states[(x, y)] == current_states[(x, y - 1)] and not current_states[(x, y)] == 0:
                current_states[(x, y)] *= current_states[(x, y)]
                current_states[(x, y - 1)] = 0
    print(" > merger\n")
    show(current_states, taille_game)
    return current_states


def left_action_applied(current_states, taille_game):
    next_states = []
    # decaler
    for y in range(0, taille_game):
        for x in range(0, taille_game):
            empty_state = first_state_emptyX(current_states, y, taille_game)
            if empty_state is not None and empty_state.x < x and not current_states[(x, y)] == 0:
                current_states[(empty_state.x, empty_state.y)] = current_states[(x, y)]
                current_states[(x, y)] = 0
    print(" > decaler\n")
    show(current_states, taille_game)
    # merger
    for y in range(0, taille_game):
        for x in range(0, taille_game - 1):
            if current_states[(x, y)] == current_states[(x+1, y)] and not current_states[(x, y)] == 0:
                current_states[(x, y)] *= current_states[(x+1, y)]
                current_states[(x+1, y)] = 0

    print(" > merger\n")
    show(current_states, taille_game)
    return current_states

def right_action_applied(current_states, taille_game):
    # decaler
    for y in range(0, taille_game):
        for x in reversed(range(0, taille_game)):
            empty_state = first_state_emptyX(current_states, y, taille_game, True)
            if empty_state is not None and empty_state.x > x and not current_states[(x, y)] == 0:
                current_states[(empty_state.x, empty_state.y)] = current_states[(x, y)]
                current_states[(x, y)] = 0
    print(" > decaler\n")
    show(current_states, taille_game)
    # merger
    for y in range(0, taille_game):
        for x in reversed(range(1, taille_game)):
            if current_states[(x, y)] == current_states[(x - 1, y)] and not current_states[(x, y)] == 0:
                current_states[(x, y)] *= current_states[(x, y)]
                current_states[(x - 1, y)] = 0
    print(" > merger\n")
    show(current_states, taille_game)
    return current_states
