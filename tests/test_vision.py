"""Vision simplifiée de la grille (4e approche)."""
import os
import random
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent as agent_module  # noqa: E402
from environnement import Environment  # noqa: E402
from historique import ligne_partie  # noqa: E402
from vision import etat_simplifie  # noqa: E402


def grille(lignes):
    """Grille à partir de lignes écrites de haut en bas : states[(x, y)] = lignes[y][x]."""
    return {(x, y): valeur for y, ligne in enumerate(lignes) for x, valeur in enumerate(ligne)}


class EtatSimplifieTest(unittest.TestCase):
    def test_grille_bien_rangee_dans_un_coin(self):
        etat = etat_simplifie(grille([[64, 32, 16, 8],
                                      [32, 16, 8, 4],
                                      [0, 0, 0, 0],
                                      [0, 0, 0, 0]]), 4)
        self.assertEqual(etat, "v8+|cHG|fh0|fv0|oh>|ov>")

    def test_fusions_et_cases_vides(self):
        etat = etat_simplifie(grille([[2, 2, 0, 0],
                                      [4, 0, 0, 4],
                                      [8, 0, 0, 0],
                                      [8, 16, 2, 4]]), 4)
        # vides : 7 ; fusions en ligne : 2/2 et 4/4 (vide entre les deux) ;
        # en colonne : 8/8 et 4/4 ; lignes sans sens dominant, colonnes plutôt croissantes
        self.assertEqual(etat, "v4-7|cB|fh2+|fv2+|oh~|ov<")

    def test_grille_pleine_sans_fusion(self):
        etat = etat_simplifie(grille([[2, 4, 2], [4, 2, 4], [2, 4, 2]]), 3)
        self.assertTrue(etat.startswith("v0-1|"))
        self.assertIn("|fh0|fv0|", etat)

    def test_beaucoup_moins_d_etats_que_la_grille(self):
        """Sur 30 parties au hasard, les états simplifiés se répètent, pas les grilles exactes."""
        random.seed(0)
        simplifies, grilles, coups = set(), set(), 0
        for _ in range(30):
            env = Environment(4)
            while not env.gameOver and not env.goal:
                env.apply(random.choice("UDLR"))
                simplifies.add(etat_simplifie(env.states, 4))
                grilles.add(env.get_state())
                coups += 1
        self.assertLess(len(simplifies), coups / 4)
        self.assertLess(len(simplifies), len(grilles) / 3)


class AgentVisionTest(unittest.TestCase):
    def _partie(self, vision_simplifiee):
        with mock.patch.object(agent_module, "MODE_APPRENTISSAGE", True):
            agent = agent_module.Agent(Environment(4), vision_simplifiee=vision_simplifiee)
            agent.do(init=True)
            while agent.continue_game():
                agent.do()
        return agent

    def test_qtable_indexee_par_l_etat_simplifie(self):
        agent = self._partie(True)
        self.assertTrue(all(etat.startswith("v") and "|c" in etat for etat in agent.learning_policy.qtable))
        self.assertEqual(ligne_partie(agent, 1, 1.0)["vision"], "simplifiee")

    def test_vision_grille_desactivee(self):
        agent = self._partie(False)
        self.assertTrue(all(etat.startswith("(0,0)") for etat in agent.learning_policy.qtable))
        self.assertEqual(ligne_partie(agent, 1, 1.0)["vision"], "grille")


if __name__ == "__main__":
    unittest.main()
