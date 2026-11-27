#!/usr/bin/env python3

import random
from copy import copy
import time
from action import ActionTextValue
from arcade import Window, run, color, draw_point, draw_text, draw_rect_filled, XYWH, draw_line, key

from agent import Agent
from historique import enregistrer_partie, ligne_partie
from memoire_ia import memoriser_fin_de_partie, preparer_agent
from environnement import Environment
from game_params import NB_TOURS_MAX, GAME_LENGHT, MODE_APPRENTISSAGE, \
    RIGHT, DOWN, LEFT, UP, GAME_SPEED


class Summary:
    def __init__(self, tours):
        self.nb_tours = tours
        self.etapes = []
        self.scores = []
        self.chain_actions = []
        self.current_tours = 0
        self.current_etape = 0
    def add(self, score, chain_actions):
        # i; etape  score actions
        self.etapes.append(self.current_etape)
        self.scores.append(score)
        self.chain_actions.append(chain_actions)

    #TODO: Optimisé lorsque le jeux est reset
    # Affichage  du résume si affichage console   
    def show(self):
        res = ''
        # Résumé de la dernière partie enregistrée
        index = len(self.scores) - 1
        res += 'tours: '+ str(index + 1) + '. Joué en '+ str(self.etapes[index]) + ' étapes. Score: '+ str(self.scores[index]) + '.\n'\
            'Enchainement d\'actions: '+ (self.chain_actions[index] or '') + '\n\n'

        return res


# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
SCREEN_TITLE = "-- 2048 --"

# Text
TEXT_TOURS_XDIM = TEXT_ETAPE_XDIM = 50
TEXT_TOURS_YDIM = TEXT_FINAL_YDIM = 600
TEXT_ETAPE_YDIM = TEXT_CURRENT_XDIM = 570
TEXT_FINAL_XDIM = TEXT_CURRENT_YDIM = 480

class Game2048Window(Window):

    def __init__(self, agent):
        length = agent.getStateLength()
        if length < 2:
            raise ValueError(f"Taille de grille invalide : {length} (minimum 2)")
        # Mise en page calculée à partir de la taille : la grille occupe [100, grid_end]
        # en x et en y, les scores sont au-dessus et les actions à droite.
        # Pour une grille de 4, on retrouve la fenêtre d'origine de 800 x 700.
        grid_end = (length + 1) * 100
        width = max(SCREEN_WIDTH, grid_end + 300)
        height = grid_end + 200
        super().__init__(width, height, SCREEN_TITLE)
        self.grid_end = grid_end
        self.agent = agent
        self.state = self.agent.getState()
        self.length = self.agent.getStateLength()
        self.summary = Summary(NB_TOURS_MAX)
        # ,self.continu = True
        self.summary.current_etape = 0
        self.summary.current_tours = 0
        self.key_pressed = None
        # Vrai quand la partie terminée a déjà été enregistrée dans le résumé
        self.partie_enregistree = False
        # Temps écoulé depuis le dernier coup de l'IA (remplace time.sleep)
        self.temps_depuis_coup = 0.0
        # Début de la partie, pour la durée enregistrée dans le CSV
        self.debut_partie = time.monotonic()

        # Positions des textes
        self.text_top_y = height - 100
        self.text_right_x = width - 320
        self.action_x = grid_end + 50

    def setup(self):
        self._render_game_core()

    def _text(self, start_x, start_y, text):
        draw_point(start_x, start_y, color.BLUE, 5)
        draw_text(text, start_x + 15, start_y, color.BLACK, 12)

    def _render_game_core(self):
        #render text : Element resumé du jeux
        self._text(50, self.text_top_y, "Tours : " + str(self.summary.current_tours + 1))
        self._text(50, self.text_top_y - 30, "Etape : " + str(self.summary.current_etape + 1))
        self._text(self.text_right_x, self.text_top_y, "Best score : " + str(self.agent.final_score))
        self._text(self.text_right_x, self.text_top_y - 30, "Current score : " + str(self.agent.state_score))
        #render text : Action choisie par l'IA ou le joueur
        if self.agent.last_action is not None:
            action = self.agent.last_action
            actionText = ActionTextValue(action)
            actionPreviousText = ActionTextValue(self.agent.previous_action)

            draw_text("Action : " + actionText, self.action_x, self.grid_end - 50, color.BLACK, 16)
            draw_text("Previous Action : " + actionPreviousText , self.action_x, self.grid_end - 80, color.BLACK, 16)

        #render text : Aide des touches pour l'utilisateur
        aide = "Echap : quitter le jeu"
        if not MODE_APPRENTISSAGE:
            aide = "Flèches : Fusionner et décaler les cases | " + aide
        draw_text(aide, 100, 40, color.BLACK, 14)

        #render text : Dans le cas ou l'IA trouve le 2048.
        if self.agent.found2048() is True:
            draw_text("2048 trouvé !!", self.action_x, self.grid_end - 120, color.RED, 16)

        for x in range(100, (self.length + 1)*100, 100):
            for y in range(100, (self.length + 1)*100, 100):
                # if x != 500 and y != 500:
                self._render_grille_case(x, y)

        # dernier ligne vertical: | && horizontal: --
        extra_point = self.grid_end

        draw_line(extra_point, 100, extra_point, extra_point, color.WHITE, 2)
        draw_line(100, extra_point, extra_point, extra_point, color.WHITE, 2)

    def _render_grille_case(self, x, y):
        # vertical: |
        draw_line(x, y, x, y + 100, color.WHITE, 2)
        # horizontal: --
        draw_line(x, y, x + 100, y, color.WHITE, 2)
        
        # render case value if case empty or not
        if(self.state[((x/100) - 1, (y/100) - 1)] == 0):
            draw_rect_filled(
                XYWH(x + 50, y + 50, 100, 100),
                color.YELLOW
            )
        else:
            draw_rect_filled(
                XYWH(x + 50, y + 50, 100, 100),
                color.GOLD
            )
            draw_text(str(self.state[((x/100) - 1, (y/100) - 1)]), x + 50, y + 50, color.BLACK, 18,
                      anchor_x="center", anchor_y="center")

    def on_draw(self):
        self.clear(color.GRAY)
        self._render_game_core()

    def on_update(self, delta_time):
        # L'IA joue un coup toutes les GAME_SPEED secondes, sans bloquer la fenêtre
        if MODE_APPRENTISSAGE and self.agent.continue_game():
            self.temps_depuis_coup += delta_time
            if self.temps_depuis_coup < GAME_SPEED:
                return
            self.temps_depuis_coup = 0.0
            if self.summary.current_etape == 0:
                self.agent.do(init=True)
            else:
                self.agent.do(prev_keyName=self.agent.last_action)
            if not self._state_not_changed():
                self.summary.current_etape += 1

        # L'environnement remplace son dictionnaire d'états à chaque coup
        self.state = self.agent.getState()
        #Si le jeux terminé alors figer le jeux avec le résultat obtenu et attendre
        #instruction utilisateur pour quitter le jeux ou réinitialiser le jeux.
        if not self.agent.continue_game() and not self.partie_enregistree:
            self.partie_enregistree = True
            self.agent.update_best_score()
            self.summary.add(self.agent.state_score, self.agent.getListActions())
            print(self.summary.show())
            if MODE_APPRENTISSAGE:
                memoriser_fin_de_partie(self.agent)
                ligne = ligne_partie(self.agent, self.summary.current_etape,
                                     time.monotonic() - self.debut_partie)
                chemin, tentative = enregistrer_partie(ligne)
                print(f"Tentative {tentative} enregistrée dans {chemin}")

    # Event : Les touches du clavier pour jouer en mode joueur
    def on_key_press(self, k, modifiers):
        if not MODE_APPRENTISSAGE:
            if k == key.UP:
                self.key_pressed = UP
                self.agent.do(keyName=self.key_pressed, prev_keyName=self.agent.last_action)
                if not self._state_not_changed():
                    self.summary.current_etape += 1
            if k == key.DOWN:
                self.key_pressed = DOWN
                self.agent.do(keyName=self.key_pressed, prev_keyName=self.agent.last_action)
                if not self._state_not_changed():
                    self.summary.current_etape += 1
            if k == key.LEFT:
                self.key_pressed = LEFT
                self.agent.do(keyName=self.key_pressed, prev_keyName=self.agent.last_action)
                if not self._state_not_changed():
                    self.summary.current_etape += 1
            if k == key.RIGHT:
                self.key_pressed = RIGHT
                self.agent.do(keyName=self.key_pressed, prev_keyName=self.agent.last_action)
                if not self._state_not_changed():
                    self.summary.current_etape += 1
        #Quitter            
        if k == key.ESCAPE:
            #TODO : register data in a file or DB for analysis either if succes or fail
            # Une partie terminée est déjà enregistrée par on_update
            self.close()

        #Reset le jeux manuellement pour le Joueur
        if k == key.N and not MODE_APPRENTISSAGE:
            # Une partie abandonnée en cours est aussi enregistrée dans le résumé
            if not self.partie_enregistree:
                self.agent.update_best_score()
                self.summary.add(self.agent.state_score, self.agent.getListActions())
            self.summary.current_tours += 1
            self.summary.current_etape = 0
            self.agent.reset()
            self.partie_enregistree = False
            self.state = self.agent.getState()
            print(f"Jeu réinitialisé ! {self.summary.current_tours} tour(s) joué(s). Meilleur score : {self.agent.final_score}.")


    def _state_not_changed(self):
        return self.agent.environment.states_not_changed()   

if __name__ == '__main__':
    # New
    plateaux = Environment(GAME_LENGHT)
    agent = Agent(plateaux)
    if MODE_APPRENTISSAGE:
        # Paramètres choisis d'après le CSV et Q-table rechargée (voir memoire_ia.py)
        preparer_agent(agent)
    window = Game2048Window(agent)
    window.setup()
    run()
