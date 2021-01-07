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
        self.continu = False

    def continue_game(self):
        return self.continu and self.environment.get_current_reward() != REWARD_GAMEOVER

    def show_last_and_best_score(self):
        if self.state_score > self.final_score:
            self.final_score = self.state_score
        if self.final_score != 0:
            print('\n #Meilleur score: ', self.final_score)
        print('\n #Dernier score atteint: ', self.state_score)

        self.state_score = 0
        self.last_action = None
    def reset(self):
         self.environment.reset()

    def do(self):
        # TODO: CODER ET IMPL L'algo d'apprentissage du jeux
        #Calcul de la meilleur actions à réaliser selon l'état en cours du jeux de l'environnement
        if MODE_APPRENTISSAGE:
            self.last_action = self.learning_policy.best_action(state=self.environment.get_state(),\
                                            last_reward_overload_noaction=self.environment.is_current_reward_overloaded(),\
                                                                start=self.start)

            print('#Action: ', self.last_action, '\n')
            self.environment.apply(self.last_action)
        else:
            action = input("#Action: RENSEIGNER UNE DIRECTION: \t")
            self.environment.apply(action)
        self.previous_state = self.environment.previous_states
        self.state = self.environment.states
        self.state_score += self.environment.score

    def getListActions(self):
        return self.learning_policy.get_listedActions()

    def show(self, init=False):
        print(' #Score: ' + str(self.state_score) + '\n')
        self.environment.show()
        self.continu = self.environment.get_current_reward != REWARD_GAMEOVER
        if MODE_APPRENTISSAGE:
            if not init:
                self.start = False
                self.learning_policy.update(previous_state=self.environment.get_pre_state(), \
                                            state=self.environment.get_state(), last_action=self.last_action, \
                                            reward=self.environment.get_current_reward())