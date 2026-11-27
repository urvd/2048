"""Choix de l'action par la Q-table : égalités tirées au hasard et exploration."""
import os
import random
import sys
import unittest
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from learning_policy import LearningPolicy  # noqa: E402

ACTIONS = {"U", "D", "L", "R"}


def politique(exploration):
    policy = LearningPolicy("s0", ACTIONS, 4, exploration=exploration)
    policy.best_action("s0", False, start=True)  # initialise la liste des actions choisies
    return policy


class ChoixActionTest(unittest.TestCase):
    def setUp(self):
        random.seed(0)

    def test_egalite_tiree_au_hasard(self):
        """État jamais appris (tout à 0) : les 4 directions sont jouées, pas toujours la même."""
        policy = politique(exploration=0.0)
        actions = Counter(policy.best_action("s0", False) for _ in range(2000))
        self.assertEqual(set(actions), ACTIONS)
        for nombre in actions.values():
            self.assertGreater(nombre, 400)  # environ 500 chacune

    def test_meilleure_action_sans_exploration(self):
        policy = politique(exploration=0.0)
        policy.qtable["s0"]["L"] = 5
        self.assertEqual({policy.best_action("s0", False) for _ in range(200)}, {"L"})

    def test_egalite_entre_les_meilleures_seulement(self):
        policy = politique(exploration=0.0)
        policy.qtable["s0"].update({"L": 5, "R": 5, "U": -1})
        self.assertEqual({policy.best_action("s0", False) for _ in range(200)}, {"L", "R"})

    def test_exploration(self):
        """Avec exploration=0.1, environ 10 % de coups au hasard, notés (e)."""
        policy = politique(exploration=0.1)
        policy.qtable["s0"]["L"] = 5
        actions = Counter(policy.best_action("s0", False) for _ in range(5000))
        hasard = policy.get_listedActions().count("(e)")
        self.assertTrue(400 < hasard < 600, hasard)
        self.assertGreater(actions["L"], 4500)

    def test_exploration_totale(self):
        policy = politique(exploration=1.0)
        policy.qtable["s0"]["L"] = 5
        actions = Counter(policy.best_action("s0", False) for _ in range(2000))
        self.assertTrue(all(nombre > 400 for nombre in actions.values()), actions)


if __name__ == "__main__":
    unittest.main()
