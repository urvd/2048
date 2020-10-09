import arcade
#L'objectif de ce code est de code l'apprentissage par renforcement du
#parcours d'un petit labyrinthe jouet

#Q-table
#        U  D    L   R
# (0, 0) 6  -7   10  20
# (0, 1) 15 -100  5
#    :
# (5, 10)

# Q(s, a) <- Q(s, a) + alpha * (rt * max(...))

MAZE = """
##.########
#     #   #
#     #   #
#         #
#         #
########*##
"""

REWARD_GOAL = 60
REWARD_DEFAULT = -1
REWARD_STUCK = -6
REWARD_IMPOSSIBLE = -60

UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'
ACTIONS = [UP, DOWN, LEFT, RIGHT]

class Environment:
    def __init__(self, text):
        self.states = {}
        lines = text.strip().split('\n')
        for row in range(len(lines)):
            for col in range(len(lines[row])):
                self.states[(row, col)] = lines[row][col]
                if lines[row][col] == '.':
                    self.starting_point = (row, col)
                elif lines[row][col] == '*':
                    self.goal = (row, col)

    def apply(self, state, action):
        if action == UP:
            new_state = (state[0] - 1, state[1])
        elif action == DOWN:
            new_state = (state[0] + 1, state[1])
        elif action == LEFT:
            new_state = (state[0], state[1] - 1)
        elif action == RIGHT:
            new_state = (state[0], state[1] + 1)

        if new_state in self.states:
            #calculer la récompense
            if self.states[new_state] in ['#', '.']:
                reward = REWARD_STUCK
            elif self.states[new_state] in ['*']: #Sortie du labyrinthe : grosse récompense
                reward = REWARD_GOAL
            else:
                reward = REWARD_DEFAULT
        else:
            #Etat impossible: grosse pénalité
            new_state = state
            reward = REWARD_IMPOSSIBLE
            
        return new_state, reward          

class Agent:
    def __init__(self, environment):
        self.environment = environment
        self.policy = Policy(environment.states.keys(), ACTIONS)
        self.reset()

    def reset(self):
        self.state = environment.starting_point
        self.previous_state = self.state
        self.score = 0

    def best_action(self):
        return self.policy.best_action(self.state)

    def do(self, action):
        self.previous_state = self.state
        self.state, self.reward = self.environment.apply(self.state, action)
        self.score += self.reward
        self.last_action = action

    def update_policy(self):
        self.policy.update(agent.previous_state, agent.state, self.last_action, self.reward)

class Policy: #Q-table
    def __init__(self, states, actions, learning_rate = 0.9, discount_factor = 0.5):
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

    def update(self, previous_state, state, last_action, reward):
        #Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        maxQ = max(self.table[state].values())
        self.table[previous_state][last_action] += self.learning_rate * \
            (reward + self.discount_factor * maxQ - self.table[previous_state][last_action])

if __name__ == "__main__":
    #Initialiser l'environment
    environment = Environment(MAZE)

    #Initialiser l'agent
    agent = Agent(environment)

    #Boucle principale
    for i in range(2):
        agent.reset()
        
        #Tant que l'agent n'est pas sorti du labyrinthe
        step = 1
        while agent.state != environment.goal:
            #Choisir la meilleure action de l'agent
            action = agent.best_action()

            #Obtenir le nouvel état de l'agent et sa récompense
            agent.do(action)
            print('#', step, 'ACTION:', action, 'STATE:', agent.previous_state, '->', agent.state, 'SCORE:', agent.score)
            step += 1
            
            #A partir de St, St+1, at, rt+1, on met à jour la politique (policy, q-table, etc.)
            agent.update_policy()
            #print(agent.policy)
        print('----')
