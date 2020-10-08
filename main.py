import random



GAME_PROCESS = 'GAME_PROCESS' #  VERIFIER SI l\'état du jeu est en cours et Addtion du score
GAME_OVER = 'GAME_OVER' # VERIFIER SI  l'état du jeu est plein et recupère son score.
GAME_SUCCES = 'GAME_SUCCES' # VERIFIER QUAND  une case de l'etat de l'environemment  contient = 2048
                            # alors l'environnement s'arrete,  et recupère son score min

REWARD_GOAL = GAME_SUCCES #Si une case de l'etat de l'environemment est = 2048
REWARD_DEFAULT = GAME_PROCESS# Methode qui met à jours l'état avec les valeurs des cases et le score
REWARD_STUCK = GAME_OVER
#TODO: CODER et IMPL LES RECOMPENSES

GENERATED_VALUES = [2, 4] #TODO: Générer aléatoirement avec une fréquence plus importante pour le 2

def randomValue():
    return random.choice(GENERATED_VALUES)

def randomXY(lenght):
    return random.choice(range(lenght))

#learning param
DEFAULT_LEARNING_RATE = 0.9;
DEFAULT_DISCOUNT_FACTOR = 0.5;

#actions param
UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R';
ACTIONS = [UP, DOWN, LEFT, RIGHT];

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

class Case:
    def __init__(self, x, y, value = 0):
        if(x == None):
            self.x = -1
        else:
            self.x = x
        if(y == None):
            self.y = -1
        else:
            self.y = y
        self.value = value

    def __eq__(self, obj):
        return self.x == obj.x and self.y == obj.y and self.value == obj.value

    def repr(self):
        return '| ' + str(self.value) + ' |'

    def toString(self):
        return '(' + str(self.x) + ',' + str(self.y) + ')=' + str(self.value)

class Environment:
    def __init__(self, length):
        self.states = {}

        self.height = length
        self.width = length
        c1_init = Case(randomXY(length), randomXY(length), 2)
        c2_init = Case(randomXY(length), randomXY(length), 2)

        while(c1_init == c2_init):
            c1_init = Case(randomXY(length), randomXY(length), 2)
            c2_init = Case(randomXY(length), randomXY(length), 2)

        for row in range(self.height):
            for col in range(self.width):
                if c1_init.x == row and c1_init.y == col:
                    self.states[(row, col)] = c1_init
                    print('c1 generated: '+ c1_init.toString())

                elif c2_init.x == row and c2_init.y == col:
                    self.states[(row, col)] = c2_init
                    print('c2 generated '+ c2_init.toString())
                else:
                    self.states[(row, col)] = Case(row, col)

        self.starting_point = self.states

    def continue_game(self):
        isPlein = False
        for row in range(self.height):
            for col in range(self.width):
                if self.states[(row, col)].value == 0 :
                    return True
        return False

    def show(self):
        for row in range(self.height):
            res = ''
            for col in range(self.width):
                if (col == self.width - 1):
                    res += self.states[(row, col)].repr()
                else:
                    res += self.states[(row, col)].repr() + ' '

            print(res + '\n')



class Policy(object):
    def __init__(self, states, actions, learning_rate=0.1, discount_factor=0.5):
        self.table = {}
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        for s in states:
            self.table[s] = {}
            for a in actions:
                self.table[s][a] = 0

    def __repr__(self):
        res = ''
        for state in self.table:
            res += f'{state}\t{self.table[state]}\n'
        return res

    def best_action(self, state):
        action = None
        for a in self.table[state]:
            if action is None or self.table[state][a] > self.table[state][action]:
                action = a
        return action


class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.state = environment.starting_point
        self.previous_state = self.state
        ##self.policy = Policy(environment.states.keys(), ACTIONS)
        self.score = 0
        self.continu = False

    def continue_game(self):
        self.continu = self.environment.continue_game()
        if self.continu == False :
            self.state = self.environment.starting_point
            self.previous_state = self.state
            self.score = 0
        return  self.continu

    def getBestAction(self):
        # TODO: CODER ET IMPL L'algo d'apprentissage du jeux
        #Calcul de la meilleur actions à réaliser selon l'état en cours du jeux de l'environnement
        return ACTIONS.UP

    def show(self):
        self.environment.show();

    #TODO: IMPL A CHAQUE ETAT de l'environnement, generer une case aléatoirement parmis ceux qui sont vide.

    #TODO: ADAPATER LE JEUX AVEC UNE BBTHEQUE GRAPHIQUE

if __name__ == '__main__':

    #Initialiser l'environment
    plateaux = Environment(4);
    # Initialiser l'agent
    agent = Agent(plateaux)

    #Initialiser le 1ere Etat
    agent.show()

    # Tant que l'environement n'est pas toute c'est case pleine.
    while(agent.continue_game()):
        #Calul = Enregistre l'action de l'agent
        action = agent.getBestAction();
        # et Changer l'état du jeu

        #Afficher du jeu en cours
        agent.show();

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
