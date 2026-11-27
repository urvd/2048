from game_params import MODE_APPRENTISSAGE, VISION_SIMPLIFIEE
from learning_policy import LearningPolicy
from vision import etat_simplifie


class Agent:
    def __init__(self, environment, vision_simplifiee=VISION_SIMPLIFIEE):
        self.environment = environment
        # 4e approche : la Q-table utilise une vision simplifiée de la grille (vision.py)
        self.vision_simplifiee = vision_simplifiee
        # self.state = environment.states
        # self.previous_state = self.environment.previous_states
        #self.last_action = 'U'
        #self.previous_action = None
        self.learning_policy = LearningPolicy(states_sign=self.etat_courant(), \
                                              actions={'U', 'D', 'L', 'R'}, \
                                              game_lenght=self.environment.length)
        self.set()
        self.final_score = 0
        # Mémoire entre les parties (voir memoire_ia.preparer_agent)
        self.fichier_qtable = None        # None : Q-table non sauvegardée
        self.choix_parametres = "defaut"  # defaut, meilleurs ou essai
    def set(self):
        self.state_score = 0
        self.last_action = None
        self.previous_action = None
        self.continu = True
        self.start = True
       
    def _etat(self, states, signature_grille):
        """Clé de la Q-table : grille simplifiée, ou grille exacte si la vision simplifiée est désactivée."""
        if self.vision_simplifiee:
            return etat_simplifie(states, self.environment.length)
        return signature_grille()

    def etat_courant(self):
        return self._etat(self.environment.states, self.environment.get_state)

    def etat_precedent(self):
        return self._etat(self.environment.previous_states, self.environment.get_pre_state)

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
            action = self.learning_policy.best_action(state=self.etat_courant(),\
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
                self.learning_policy.update(previous_state=self.etat_precedent(), \
                                            state=self.etat_courant(), last_action=action, \
                                            reward=self.environment.get_current_reward())
            self.last_action = action
    def update_best_score(self):
        if self.state_score > self.final_score:
            self.final_score = self.state_score

    def getListActions(self):
        return self.learning_policy.get_listedActions()
