"""Tests de l'enregistrement des parties de l'IA dans le fichier CSV."""
import csv
import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent as agent_module  # noqa: E402
from environnement import Environment  # noqa: E402
from historique import COLONNES, SEPARATEUR, enregistrer_partie, ligne_partie  # noqa: E402


class HistoriqueTest(unittest.TestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.chemin = os.path.join(dossier.name, "parties.csv")

    def _partie_terminee(self):
        with mock.patch.object(agent_module, "MODE_APPRENTISSAGE", True):
            agent = agent_module.Agent(Environment(3))
            agent.do(init=True)
            while agent.continue_game():
                agent.do()
        return agent

    def test_ligne_contient_toutes_les_colonnes(self):
        agent = self._partie_terminee()
        ligne = ligne_partie(agent, nb_etapes=12, duree_secondes=3.14)
        self.assertEqual(["tentative"] + list(ligne), COLONNES)
        self.assertEqual(ligne["nb_etapes"], 12)
        self.assertEqual(ligne["score_total"], agent.state_score)
        self.assertIn(ligne["tuile_2048_trouvee"], ("oui", "non"))

    def test_en_tete_ecrit_une_seule_fois(self):
        agent = self._partie_terminee()
        for _ in range(3):
            enregistrer_partie(ligne_partie(agent, 5, 1.0), self.chemin)
        with open(self.chemin, encoding="utf-8") as fichier:
            lignes = list(csv.reader(fichier, delimiter=SEPARATEUR))
        self.assertEqual(lignes[0], COLONNES)
        self.assertEqual(len(lignes), 4)
        self.assertEqual([ligne[0] for ligne in lignes[1:]], ["1", "2", "3"])

    def test_tentative_reprend_apres_le_dernier_numero(self):
        agent = self._partie_terminee()
        enregistrer_partie(ligne_partie(agent, 5, 1.0), self.chemin)
        _, tentative = enregistrer_partie(ligne_partie(agent, 5, 1.0), self.chemin)
        self.assertEqual(tentative, 2)


if __name__ == "__main__":
    unittest.main()
