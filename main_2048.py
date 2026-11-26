#!/usr/bin/env python3

import random
from copy import copy
import time
from action import ActionTextValue
from arcade import Window, run, color, draw_point, draw_text, draw_rect_filled, XYWH, draw_line, key

from agent import Agent
from environnement import Environment
from game_params import DEFAULT_LEARNING_RATE, REWARD_GAMEOVER, IA_NB_TOURS, GAME_LENGHT, MODE_APPRENTISSAGE, \
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

    # Affichage  du résume si affichage console   
    def show(self):
        res = ''
        #for i in range(0, self.nb_tours):
        index = self.current_tours - 1
        res += 'tours: '+ str(self.current_tours) + '. Joué en '+ str(self.etapes[index]) + ' étapes. Score: '+ str(self.scores[index]) + '.\n'\
            'Enchainement d\'actions: '+ self.chain_actions[index] + '\n\n'

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
        if agent.getStateLength() == 4:
            width = SCREEN_WIDTH
            height = SCREEN_HEIGHT
        if agent.getStateLength() == 5:
            width = SCREEN_WIDTH + 100
            height = SCREEN_HEIGHT + 100
        elif agent.getStateLength() == 3:
            width = SCREEN_WIDTH
            height = SCREEN_HEIGHT
        super().__init__(width, height, SCREEN_TITLE)
        self.agent = agent
        self.state = self.agent.getState()
        self.length = self.agent.getStateLength()
        self.summary = Summary(IA_NB_TOURS)
        # ,self.continu = True
        self.summary.current_etape = 0
        self.summary.current_tours = 0
        self.key_pressed = None

        self.extra_xpoint = 0
        self.extra_ypoint = 0
        if self.length == 5:
           self.extra_xpoint = 100
        elif self.length == 3:
            self.extra_ypoint = 100
            self.extra_xpoint = 100

    def setup(self):
        self._render_game_core()

    def _text(self, start_x, start_y, text):
        draw_point(start_x, start_y, color.BLUE, 5)
        draw_text(text, start_x + 15, start_y, color.BLACK, 12)

    def _render_game_core(self):
        #render text : Element resumé du jeux
        self._text(50 + self.extra_xpoint, 600 + self.extra_ypoint, "Tours : " + str(self.summary.current_tours + 1))
        self._text(50 + self.extra_xpoint, 570 +  self.extra_ypoint, "Etape : " + str(self.summary.current_etape + 1))
        self._text(480 + self.extra_xpoint, 600 + self.extra_ypoint, "Best score : " + str(self.agent.final_score))
        self._text(480 + self.extra_xpoint, 570 + self.extra_ypoint, "Current score : " + str(self.agent.state_score))
        #render text : Action choisie par l'IA ou le joueur
        if self.agent.last_action is not None:
            action = self.agent.last_action
            actionText = ActionTextValue(action)
            actionPreviousText = ActionTextValue(self.agent.previous_action)

            draw_text("Action : " + actionText, 550 + self.extra_xpoint, 450 + self.extra_ypoint, color.BLACK, 16)
            draw_text("Previous Action : " + actionPreviousText , 550 + self.extra_xpoint, 420 + self.extra_ypoint, color.BLACK, 16)

        #render text : Aide des touches pour l'utilisateur
        aide = "Echap : quitter le jeu"
        if not MODE_APPRENTISSAGE:
            aide = "Flèches : jouer   |   " + aide
        draw_text(aide, 100, 40, color.BLACK, 14)

        #render text : Dans le cas ou l'IA trouve le 2048.
        if self.agent.found2048() is True:
            draw_text("2048 trouvé !!", 550 + self.extra_xpoint, 550 - self.extra_ypoint, color.RED, 16)

        for x in range(100, (self.length + 1)*100, 100):
            for y in range(100, (self.length + 1)*100, 100):
                # if x != 500 and y != 500:
                self._render_grille_case(x, y)

        # dernier ligne vertical: | && horizontal: --
        extra_point = 500
        if self.length == 5:
           extra_point = 600
        elif self.length == 3:
            extra_point = 400

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
            draw_text(str(self.state[((x/100) - 1, (y/100) - 1)]), x + 48, y + 48, color.BLACK, 18)

    def on_draw(self):
        self.clear(color.GRAY)
        self._render_game_core()

    def on_update(self, delta_time):
        if MODE_APPRENTISSAGE:
            if self.summary.current_etape == 0:
                self.agent.do(init=True)
            else:
                self.agent.do(prev_keyName=self.agent.last_action)
            time.sleep(GAME_SPEED)

        self.state = self.agent.getState()

        if not self.agent.continue_game():
            self.summary.add(self.agent.state_score, self.agent.getListActions())
            self.summary.current_etape = 0
            self.summary.current_tours += 1
            print(self.summary.show())
            time.sleep(3.0)
            self.agent.reset()
        else:
            if MODE_APPRENTISSAGE:
                if not self._state_not_changed():
                    self.summary.current_etape += 1

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
                states_changed = self.agent.environment.states_not_changed();
                if not self._state_not_changed():
                    self.summary.current_etape += 1
            if k == key.LEFT:
                self.key_pressed = LEFT
                self.agent.do(keyName=self.key_pressed, prev_keyName=self.agent.last_action)
                states_changed = self.agent.environment.states_not_changed();
                if not self._state_not_changed():
                    self.summary.current_etape += 1
            if k == key.RIGHT:
                self.key_pressed = RIGHT
                self.agent.do(keyName=self.key_pressed, prev_keyName=self.agent.last_action)
                if not self._state_not_changed():
                    self.summary.current_etape += 1
        if k == key.ESCAPE:
            #TODO : register data in a file or DB for analysis either if succes or fail
            if not self.agent.continue_game():
                self.summary.add(self.agent.state_score, self.agent.getListActions())
                print(self.summary.show())
            self.close()

    def _state_not_changed(self):
        return self.agent.environment.states_not_changed()   

if __name__ == '__main__':
    # New
    plateaux = Environment(GAME_LENGHT)
    agent = Agent(plateaux)
    window = Game2048Window(agent)
    window.setup()
    run()
