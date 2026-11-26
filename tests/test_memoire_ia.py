"""Tests de la mémoire de l'IA : paramètres choisis d'après le CSV et Q-table persistante."""
import csv
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent as agent_module  # noqa: E402
import memoire_ia  # noqa: E402
from environnement import Environment  # noqa: E402
from game_params import DEFAULT_DISCOUNT_FACTOR, DEFAULT_LEARNING_RATE  # noqa: E402
from historique import COLONNES, SEPARATEUR, enregistrer_partie, ligne_partie, lire_parties  # noqa: E402

RECOMPENSES = {"default": 1, "goal": 2048, "gameover": -100, "no_effect": -8}


class RngFixe:
    """Remplace random : valeur de random() imposée, choice() prend le premier élément."""

    def __init__(self, valeur):
        self.valeur = valeur

    def random(self):
        return self.valeur

    def choice(self, valeurs):
        return valeurs[0]


def partie(score, learning_rate, discount_factor, taille=4, gameover=-100):
    return {"taille_grille": str(taille), "score_total": str(score), "learning_rate": str(learning_rate),
            "discount_factor": str(discount_factor), "reward_default": "1", "reward_goal": "2048",
            "reward_gameover": str(gameover), "reward_no_effect": "-8"}


class ChoixParametresTest(unittest.TestCase):
    def test_sans_historique_valeurs_par_defaut(self):
        self.assertEqual(memoire_ia.choisir_parametres([], 4, RECOMPENSES, RngFixe(0.9)),
                         (DEFAULT_LEARNING_RATE, DEFAULT_DISCOUNT_FACTOR, "defaut"))

    def test_reprend_la_meilleure_tentative(self):
        parties = [partie(500, 0.01, 0.2), partie(1800, 0.05, 0.5), partie(900, 0.1, 0.3)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9)),
                         (0.05, 0.5, "meilleurs"))

    def test_essai_de_parametres_voisins(self):
        parties = [partie(1800, 0.05, 0.5)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.1)),
                         (0.025, 0.4, "essai"))

    def test_ignore_les_parties_d_un_autre_contexte(self):
        parties = [partie(9999, 0.9, 0.9, taille=3), partie(9999, 0.8, 0.8, gameover=-50),
                   partie(100, 0.02, 0.3)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9)),
                         (0.02, 0.3, "meilleurs"))

    def test_essai_reste_dans_les_bornes(self):
        lr, df, _ = memoire_ia.choisir_parametres([partie(10, 0.001, 0.0)], 4, RECOMPENSES, RngFixe(0.1))
        self.assertGreaterEqual(lr, memoire_ia.LEARNING_RATE_MIN)
        self.assertGreaterEqual(df, memoire_ia.DISCOUNT_FACTOR_MIN)


class QTablePersistanteTest(unittest.TestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.dossier = dossier.name

    def _agent(self):
        with mock.patch.object(agent_module, "MODE_APPRENTISSAGE", True):
            agent = agent_module.Agent(Environment(3))
            agent.do(init=True)
            while agent.continue_game():
                agent.do()
        return agent

    def test_sauvegarde_puis_rechargement(self):
        chemin = os.path.join(self.dossier, "qtable.json")
        agent = self._agent()
        memoire_ia.sauvegarder_qtable(agent.learning_policy, chemin, 3, RECOMPENSES)
        nouvel_agent = agent_module.Agent(Environment(3))
        nb_etats = memoire_ia.charger_qtable(nouvel_agent.learning_policy, chemin, RECOMPENSES)
        self.assertEqual(nb_etats, len(agent.learning_policy.qtable))
        for etat, valeurs in agent.learning_policy.qtable.items():
            self.assertEqual(nouvel_agent.learning_policy.qtable[etat], valeurs)

    def test_preparer_puis_memoriser(self):
        chemin_qtable = os.path.join(self.dossier, "qtable.json")
        chemin_parties = os.path.join(self.dossier, "parties.csv")
        with mock.patch.dict(os.environ, {"FICHIER_QTABLE": chemin_qtable}):
            # 1re partie : aucun historique, Q-table vide
            agent = agent_module.Agent(Environment(3))
            memoire_ia.preparer_agent(agent, True, True, chemin_parties, RngFixe(0.9))
            self.assertEqual(agent.choix_parametres, "defaut")
            agent = self._agent_prepare(agent)
            memoire_ia.memoriser_fin_de_partie(agent)
            enregistrer_partie(ligne_partie(agent, 10, 1.0), chemin_parties)
            # 2e partie : paramètres de la 1re et Q-table rechargée
            agent2 = agent_module.Agent(Environment(3))
            memoire_ia.preparer_agent(agent2, True, True, chemin_parties, RngFixe(0.9))
        self.assertEqual(agent2.choix_parametres, "meilleurs")
        self.assertGreaterEqual(len(agent2.learning_policy.qtable), len(agent.learning_policy.qtable))
        self.assertEqual(lire_parties(chemin_parties)[0]["qtable_persistante"], "oui")

    def _agent_prepare(self, agent):
        with mock.patch.object(agent_module, "MODE_APPRENTISSAGE", True):
            agent.do(init=True)
            while agent.continue_game():
                agent.do()
        return agent

    def test_desactivee_aucun_fichier(self):
        chemin_qtable = os.path.join(self.dossier, "qtable.json")
        with mock.patch.dict(os.environ, {"FICHIER_QTABLE": chemin_qtable}):
            agent = self._agent()
            memoire_ia.preparer_agent(agent, optimiser=False, persistante=False)
            memoire_ia.memoriser_fin_de_partie(agent)
        self.assertFalse(os.path.exists(chemin_qtable))
        self.assertEqual(agent.choix_parametres, "defaut")


class MigrationCsvTest(unittest.TestCase):
    def test_ancien_en_tete_mis_a_jour(self):
        with tempfile.TemporaryDirectory() as dossier:
            chemin = os.path.join(dossier, "parties.csv")
            anciennes = [c for c in COLONNES if c not in ("choix_parametres", "qtable_persistante")]
            with open(chemin, "w", newline="", encoding="utf-8") as fichier:
                writer = csv.DictWriter(fichier, fieldnames=anciennes, delimiter=SEPARATEUR)
                writer.writeheader()
                writer.writerow({c: "1" for c in anciennes})
            agent = agent_module.Agent(Environment(3))
            _, tentative = enregistrer_partie(ligne_partie(agent, 3, 1.0), chemin)
            parties = lire_parties(chemin)
        self.assertEqual(tentative, 2)
        self.assertEqual(list(parties[0]), COLONNES)
        self.assertEqual(parties[0]["choix_parametres"], "")
        self.assertEqual(parties[1]["choix_parametres"], "defaut")


if __name__ == "__main__":
    unittest.main()
