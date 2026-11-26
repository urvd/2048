"""Tests de non-régression des corrections de la section A (sans affichage)."""
import os
import random
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent as agent_module  # noqa: E402
from environnement import Environment  # noqa: E402
from game_deplacement import ActionImpl  # noqa: E402
from learning_policy import LearningPolicy  # noqa: E402
from main_2048 import Summary  # noqa: E402


def grille_bloquee(length):
    """Grille pleine en damier 2/4 : aucun coup possible."""
    return {(r, c): 2 if (r + c) % 2 == 0 else 4 for r in range(length) for c in range(length)}


def grille_presque_2048(length):
    states = {(r, c): 0 for r in range(length) for c in range(length)}
    states[(0, 0)] = states[(1, 0)] = 1024
    return states


class FinDePartieTest(unittest.TestCase):
    def _agent(self, mode_ia):
        patcher = mock.patch.object(agent_module, "MODE_APPRENTISSAGE", mode_ia)
        patcher.start()
        self.addCleanup(patcher.stop)
        return agent_module.Agent(Environment(3))

    def test_defaite_termine_la_partie(self):
        for mode_ia in (False, True):
            with self.subTest(mode_ia=mode_ia):
                agent = self._agent(mode_ia)
                agent.environment.states = grille_bloquee(3)
                agent.do(keyName="U", init=True)
                self.assertTrue(agent.environment.gameOver)
                self.assertFalse(agent.continue_game())

    def test_victoire_termine_la_partie(self):
        agent = self._agent(False)
        agent.environment.states = grille_presque_2048(3)
        agent.do(keyName="L")
        self.assertTrue(agent.found2048())
        self.assertFalse(agent.continue_game())

    def test_reset_relance_la_partie(self):
        agent = self._agent(False)
        agent.environment.states = grille_bloquee(3)
        agent.do(keyName="U")
        agent.reset()
        self.assertTrue(agent.continue_game())
        self.assertFalse(agent.environment.gameOver)


class EnvironnementTest(unittest.TestCase):
    def test_grille_initiale_a_deux_tuiles_dans_la_grille(self):
        for size in (3, 4, 5):
            for seed in range(50):
                with self.subTest(size=size, seed=seed):
                    random.seed(seed)
                    env = Environment(size)
                    self.assertEqual(len(env.states), size * size)
                    self.assertEqual(sum(1 for v in env.states.values() if v), 2)

    def test_nouvelle_tuile_sur_une_case_vide(self):
        random.seed(0)
        env = Environment(4)
        for _ in range(300):
            before = dict(env.states)
            env.apply(random.choice("UDLR"))
            if env.states != before and 0 in env.states.values():
                # les fusions conservent la somme : seule la nouvelle tuile (2 ou 4) l'augmente
                self.assertIn(sum(env.states.values()) - sum(before.values()), (2, 4))
            if env.gameOver:
                break


class QLearningTest(unittest.TestCase):
    def test_mise_a_jour_sur_l_action_jouee(self):
        with mock.patch.object(agent_module, "MODE_APPRENTISSAGE", True):
            agent = agent_module.Agent(Environment(4))
            actions = iter(["L", "R"])
            with mock.patch.object(agent.learning_policy, "best_action", side_effect=lambda **_: next(actions)), \
                    mock.patch.object(agent.learning_policy, "update") as update:
                agent.do(init=True)   # joue L, pas d'apprentissage au premier coup
                agent.do()            # joue R : la mise à jour doit porter sur R
            self.assertEqual(update.call_args.kwargs["last_action"], "R")

    def test_qtable_sans_limite_d_etats(self):
        policy = LearningPolicy("s0", {"U", "D", "L", "R"}, 4)
        for i in range(40000):
            policy.update(f"s{i}", f"s{i + 1}", "U", 1)
        self.assertEqual(len(policy.qtable), 40001)

    def test_formule_de_mise_a_jour(self):
        policy = LearningPolicy("s0", {"U", "D", "L", "R"}, 4, learning_rate=0.5, discount_factor=0.0)
        policy.update("s0", "s1", "L", 10)
        self.assertEqual(policy.qtable["s0"]["L"], 5)


class DiversTest(unittest.TestCase):
    def test_classe_de_base_abstraite(self):
        with self.assertRaises(NotImplementedError):
            ActionImpl({(0, 0): 0}, 1)

    def test_resume_sans_liste_d_actions(self):
        summary = Summary(5)
        summary.add(128, None)  # mode manuel : pas de liste d'actions IA
        self.assertIn("Score: 128", summary.show())


if __name__ == "__main__":
    unittest.main()
