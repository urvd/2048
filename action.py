
from game_params import UP, DOWN, LEFT, RIGHT, ACTIONS


def ActionTextValue(symbol):
    if symbol == UP:
        return 'Haut'
    elif symbol == DOWN:
        return 'Bas'
    elif symbol == LEFT:
        return 'Gauche'
    elif symbol == RIGHT:
        return 'Droite'
    else:
        return 'N/A'