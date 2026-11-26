from game_params import MODE_APPRENTISSAGE, DEFAULT_LEARNING_RATE, REWARD_GAMEOVER, REWARD_GOAL
from learning_policy import LearningPolicy


class Agent:
    def __init__(self, environment):
        self.environment = environment
        # self.state = environment.states
        # self.previous_state = self.environment.previous_states
        #self.last_action = 'U'
        #self.previous_action = None
        self.learning_policy = LearningPolicy(states_sign=self.environment.get_state(), \
                                              actions={'U', 'D', 'L', 'R'}, \
                                              game_lenght=self.environment.length)
        self.set()
        self.final_score = 0
    def set(self):
        self.state_score = 0
        self.last_action = None
        self.previous_action = None
        self.continu = True
        self.start = True
       
    def getState(self):
        return self.environment.states
    def getStateLength(self):
        return self.environment.length
    def found2048(self):
        return self.environment.goal

    def continue_game(self):
        return self.continu

    def reset(self):
        self.update_best_score()
        self.set()
        self.environment.reset()

    def do(self, init=False, keyName=None, prev_keyName=None):

        if prev_keyName is not None:
            self.previous_action = prev_keyName
        # TODO: CODER ET IMPL L'algo d'apprentissage du jeux
        #Calcul de la meilleur actions à réaliser selon l'état en cours du jeux de l'environnement
        action = ''
        if MODE_APPRENTISSAGE:
            action = self.learning_policy.best_action(state=self.environment.get_state(),\
                                            last_reward_overload_noaction=self.environment.is_current_reward_overloaded(),\
                                                                start=self.start)
            self.environment.apply(action)


        else:
            self.last_action = keyName
            self.environment.apply(self.last_action)

        # La partie continue tant qu'il n'y a ni victoire (2048) ni défaite
        self.continu = not self.environment.goal and not self.environment.gameOver
        # print('#Action: ', self.last_action, '\n')
        self.state_score += self.environment.score
        #self.continu = self.environment.get_current_reward() != REWARD_GAMEOVER
        #if self.environment.get_current_reward() == REWARD_GOAL:
            #self.continu = False

        if MODE_APPRENTISSAGE:
            if not init:
                self.start = False
                self.learning_policy.update(previous_state=self.environment.get_pre_state(), \
                                            state=self.environment.get_state(), last_action=self.last_action, \
                                            reward=self.environment.get_current_reward())
            self.last_action = action
    def update_best_score(self):
        if self.state_score > self.final_score:
            self.final_score = self.state_score

    def getListActions(self):
        return self.learning_policy.get_listedActions()
