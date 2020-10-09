import arcade

# Q-table
#        U  D    L   R
# (0, 0) 6  -7   10  20
# (0, 1) 15 -100  5
#    :
# (5, 10)

# Q(s, a) <- Q(s, a) + alpha * (rt * max(...))

MAZE = """
##.########
#       # #
# # # #   #
# ### # # #
#     ### #
#     #   #
########*##
"""

SPRITE_SIZE = 64

REWARD_GOAL = 60
REWARD_DEFAULT = -1
REWARD_STUCK = -6
REWARD_IMPOSSIBLE = -60

DEFAULT_LEARNING_RATE = 1
DEFAULT_DISCOUNT_FACTOR = 0.5

UP, DOWN, LEFT, RIGHT = 'U', 'D', 'L', 'R'
ACTIONS = [UP, DOWN, LEFT, RIGHT]


class Environment:
    def __init__(self, text):
        self.states = {}
        lines = text.strip().split('\n')

        self.height = len(lines)
        self.width = len(lines[0])

        for row in range(self.height):
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
            # calculer la récompense
            if self.states[new_state] in ['#', '.']:
                reward = REWARD_STUCK
            elif self.states[new_state] in ['*']:  # Sortie du labyrinthe : grosse récompense
                reward = REWARD_GOAL
            else:
                reward = REWARD_DEFAULT
        else:
            # Etat impossible: grosse pénalité
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


class Policy:  # Q-table
    def __init__(self, states, actions,
                 learning_rate=DEFAULT_LEARNING_RATE,
                 discount_factor=DEFAULT_DISCOUNT_FACTOR):
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
        # Q(st, at) = Q(st, at) + learning_rate * (reward + discount_factor * max(Q(state)) - Q(st, at))
        maxQ = max(self.table[state].values())
        self.table[previous_state][last_action] += self.learning_rate * \
                                                   (reward + self.discount_factor * maxQ - self.table[previous_state][
                                                       last_action])


class MazeWindow(arcade.Window):
    def __init__(self, agent):
        super().__init__(agent.environment.width * SPRITE_SIZE,
                         agent.environment.height * SPRITE_SIZE,
                         'Escape from ESGI')
        self.agent = agent
        arcade.set_background_color(arcade.csscolor.DARK_BLUE)

    def setup(self):
        self.walls = arcade.SpriteList()
        for state in self.agent.environment.states:
            if self.agent.environment.states[state] == '#':
                sprite = arcade.Sprite(":resources:images/tiles/grassCenter.png", 0.5)
                sprite.center_x = state[1] * sprite.width + sprite.width * 0.5
                sprite.center_y = self.height - (state[0] * sprite.width + sprite.width * 0.5)
                self.walls.append(sprite)

        self.goal = arcade.Sprite(":resources:images/items/flagGreen1.png", 0.5)
        self.goal.center_x = self.agent.environment.goal[1] * self.goal.width + self.goal.width * 0.5
        self.goal.center_y = self.height - (self.agent.environment.goal[0] * self.goal.width + self.goal.width * 0.5)

        self.player = arcade.Sprite(":resources:images/enemies/mouse.png", 0.5)
        self.update_player()

    def update_player(self):
        self.player.center_x = self.agent.state[1] * self.player.width + self.player.width * 0.5
        self.player.center_y = self.height - (self.agent.state[0] * self.player.width + self.player.width * 0.5)

    def on_update(self, delta_time):
        if agent.state != environment.goal:
            action = self.agent.best_action()
            self.agent.do(action)
            self.agent.update_policy()
            self.update_player()

    def on_draw(self):
        arcade.start_render()
        self.walls.draw()
        self.goal.draw()
        self.player.draw()

        arcade.draw_text(f"Score: {self.agent.score}", 10, 10, arcade.csscolor.WHITE, 20)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.R:
            self.agent.reset()


if __name__ == "__main__":
    environment = Environment(MAZE)
    agent = Agent(environment)

    window = MazeWindow(agent)
    window.setup()
    arcade.run()
