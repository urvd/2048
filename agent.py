from game_params import MODE_APPRENTISSAGE, DEFAULT_LEARNING_RATE, REWARD_GAMEOVER
from learning_policy import LearningPolicy


class Agent:
    def __init__(self, environment):
        self.environment = environment
        # self.state = environment.states
        # self.previous_state = self.environment.previous_states
        self.last_action = None
        self.learning_policy = LearningPolicy(states_sign=self.environment.get_state(), \
                                              actions={'U', 'D', 'L', 'R'}, \
                                              game_lenght=self.environment.length, \
                                              learning_rate=DEFAULT_LEARNING_RATE)
        self.start = True
        self.list_action = ''
        self.state_score = 0
        self.final_score = 0
        self.continu = True
    def getState(self):
        return self.environment.states
    def continue_game(self):
        return self.continu and self.environment.get_current_reward() != REWARD_GAMEOVER

    def reset(self):
        if self.state_score > self.final_score:
            self.final_score = self.state_score
        self.state_score = 0
        self.last_action = None
        self.environment.reset()

    def do(self, init=False, keyName=None):
        # TODO: CODER ET IMPL L'algo d'apprentissage du jeux
        #Calcul de la meilleur actions à réaliser selon l'état en cours du jeux de l'environnement
        if MODE_APPRENTISSAGE:
            self.last_action = self.learning_policy.best_action(state=self.environment.get_state(),\
                                            last_reward_overload_noaction=self.environment.is_current_reward_overloaded(),\
                                                                start=self.start)

            print('#Action: ', self.last_action, '\n')
            self.environment.apply(self.last_action)
        else:
            self.last_action = keyName
            self.environment.apply(self.last_action)
        # self.previous_state = self.environment.previous_states
        # self.state = self.environment.states
        self.state_score += self.environment.score
        self.continu = self.environment.get_current_reward != REWARD_GAMEOVER

        if MODE_APPRENTISSAGE:
            if not init:
                self.start = False
                self.learning_policy.update(previous_state=self.environment.get_pre_state(), \
                                            state=self.environment.get_state(), last_action=self.last_action, \
                                            reward=self.environment.get_current_reward())
    def getListActions(self):
        return self.learning_policy.get_listedActions()
