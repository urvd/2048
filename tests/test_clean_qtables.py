"""Classement des Q-tables, rechargement de la meilleure et nettoyage (clean_qtables.py)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

import agent as agent_module  # noqa: E402
import memoire_ia  # noqa: E402
from clean_qtables import nettoyer  # noqa: E402
from environnement import Environment  # noqa: E402
from historique import ligne_partie  # noqa: E402

RECOMPENSES = {"default": 1, "goal": 2048, "gameover": -100, "no_effect": -8}


def partie(tentative, tuile, nb_cases, score):
    return {"tentative": str(tentative), "meilleure_tuile": str(tuile), "nb_cases_max": str(nb_cases),
            "score_total": str(score)}


def creer_qtable(dossier, tentative, recompenses=RECOMPENSES, vision="grille"):
    os.makedirs(dossier, exist_ok=True)
    chemin = os.path.join(dossier, f"qtable_4x4_T{tentative}.json")
    with open(chemin, "w", encoding="utf-8") as fichier:
        json.dump({"taille": 4, "recompenses": recompenses, "vision": vision,
                   "qtable": {f"etat{tentative}": {"L": 1.0}}}, fichier)
    return chemin


class ClassementTest(unittest.TestCase):
    def test_exemple_des_trois_parties(self):
        """512 bat 256 ; à égalité de 256, deux cases battent une seule case."""
        p1, p2, p3 = partie(1, 256, 1, 2000), partie(2, 256, 2, 1900), partie(3, 512, 1, 1500)
        classees = sorted([p1, p2, p3], key=memoire_ia.cle_classement, reverse=True)
        self.assertEqual([p["tentative"] for p in classees], ["3", "2", "1"])

    def test_score_en_dernier_recours(self):
        self.assertGreater(memoire_ia.cle_classement(partie(1, 256, 1, 2100)),
                           memoire_ia.cle_classement(partie(2, 256, 1, 2000)))

    def test_tentative_inconnue_classee_en_dernier(self):
        self.assertLess(memoire_ia.cle_classement(None), memoire_ia.cle_classement(partie(1, 2, 1, 0)))

    def test_colonne_nb_cases_max(self):
        agent = agent_module.Agent(Environment(4))
        agent.environment.states = {k: 0 for k in agent.environment.states}
        agent.environment.states[(0, 0)] = agent.environment.states[(1, 1)] = 256
        agent.environment.states[(2, 2)] = 128
        ligne = ligne_partie(agent, 1, 1.0)
        self.assertEqual((ligne["meilleure_tuile"], ligne["nb_cases_max"]), (256, 2))


class MeilleureQTableTest(unittest.TestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.dossier = os.path.join(dossier.name, "4x4")

    def test_recharge_la_meilleure_et_non_la_plus_recente(self):
        for n in (1, 2, 3):
            creer_qtable(self.dossier, n)
        parties = [partie(1, 256, 1, 2000), partie(2, 512, 1, 3000), partie(3, 128, 1, 900)]
        self.assertEqual(memoire_ia.meilleure_qtable(4, RECOMPENSES, parties, self.dossier),
                         os.path.join(self.dossier, "qtable_4x4_T2.json"))

    def test_meilleure_parmi_les_memes_recompenses_et_vision(self):
        creer_qtable(self.dossier, 1)
        creer_qtable(self.dossier, 2, dict(RECOMPENSES, gameover=-50))
        creer_qtable(self.dossier, 3, vision="simplifiee")
        parties = [partie(1, 128, 1, 900), partie(2, 512, 1, 3000), partie(3, 1024, 1, 9000)]
        self.assertEqual(memoire_ia.meilleure_qtable(4, RECOMPENSES, parties, self.dossier, "grille"),
                         os.path.join(self.dossier, "qtable_4x4_T1.json"))

    def test_preparer_agent_charge_la_meilleure(self):
        racine = os.path.dirname(self.dossier)
        chemin_parties = os.path.join(racine, "parties.csv")
        agent = agent_module.Agent(Environment(4), vision_simplifiee=False)
        vision = "grille"
        for n in (1, 2):
            creer_qtable(self.dossier, n, vision=vision)
        parties = [partie(1, 512, 1, 3000), partie(2, 128, 1, 900)]
        with mock.patch.object(memoire_ia, "DOSSIER_QTABLE", racine), \
                mock.patch.object(memoire_ia, "lire_parties", return_value=parties):
            memoire_ia.preparer_agent(agent, optimiser=False, persistante=True, chemin_parties=chemin_parties)
        self.assertIn("etat1", agent.learning_policy.qtable)
        self.assertNotIn("etat2", agent.learning_policy.qtable)


class NettoyageTest(unittest.TestCase):
    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.dossier = os.path.join(dossier.name, "4x4")
        # 15 tentatives : la tentative n a pour score 100 * n (la 15 est la meilleure)
        self.parties = [partie(n, 256, 1, 100 * n) for n in range(1, 16)]
        for n in range(1, 16):
            creer_qtable(self.dossier, n)

    def _restants(self):
        return sorted(int(nom.split("_T")[1].split(".")[0]) for nom in os.listdir(self.dossier))

    def test_garde_les_meilleures(self):
        supprimes = nettoyer(4, garder=10, parties=self.parties, dossier=self.dossier)
        self.assertEqual(len(supprimes), 5)
        self.assertEqual(self._restants(), list(range(6, 16)))

    def test_tentatives_absentes_du_csv_supprimees_en_premier(self):
        nettoyer(4, garder=12, parties=self.parties[3:], dossier=self.dossier)  # T1 à T3 absentes du CSV
        self.assertEqual(self._restants(), list(range(4, 16)))

    def test_simulation_ne_supprime_rien(self):
        supprimes = nettoyer(4, garder=3, parties=self.parties, dossier=self.dossier, simulation=True)
        self.assertEqual(len(supprimes), 12)
        self.assertEqual(len(self._restants()), 15)

    def test_supprime_les_fichiers_temporaires(self):
        with open(os.path.join(self.dossier, "qtable_4x4_T16.json.tmp"), "w", encoding="utf-8") as f:
            f.write("{")
        nettoyer(4, garder=20, parties=self.parties, dossier=self.dossier)
        self.assertFalse(any(nom.endswith(".tmp") for nom in os.listdir(self.dossier)))

    def test_lancement_en_ligne_de_commande(self):
        racine = os.path.dirname(self.dossier)
        code = ("import memoire_ia, clean_qtables, sys; memoire_ia.DOSSIER_QTABLE = sys.argv[1];"
                "sys.argv = ['clean_qtables.py', '--taille', '4', '--garder', '4', '--simulation']; clean_qtables.main()")
        sortie = subprocess.run([sys.executable, "-c", code, racine], cwd=RACINE, capture_output=True, text=True,
                                check=True)
        self.assertIn("11 fichier(s) serait supprimé(s), 4 Q-table(s) gardée(s)", sortie.stdout)


class TailleDuJeuTest(unittest.TestCase):
    def test_game_lenght_invalide_refuse(self):
        sortie = subprocess.run([sys.executable, "-c", "import game_params"], cwd=RACINE,
                                env=dict(os.environ, GAME_LENGHT="6"), capture_output=True, text=True)
        self.assertNotEqual(sortie.returncode, 0)
        self.assertIn("doit valoir 3, 4 ou 5", sortie.stderr)


if __name__ == "__main__":
    unittest.main()
