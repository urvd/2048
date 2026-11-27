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
from game_params import DISCOUNT_FACTOR, LEARNING_RATE  # noqa: E402
from historique import COLONNES, SEPARATEUR, enregistrer_partie, ligne_partie, lire_parties  # noqa: E402

RECOMPENSES = {"default": 1, "goal": 2048, "gameover": -100, "no_effect": -8}
# Vision par défaut des agents créés dans les tests (VISION_SIMPLIFIEE du .env)
VISION = "simplifiee" if agent_module.VISION_SIMPLIFIEE else "grille"


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
                         (LEARNING_RATE, DISCOUNT_FACTOR, RECOMPENSES, "defaut"))

    def test_reprend_la_meilleure_tentative(self):
        parties = [partie(500, 0.01, 0.2), partie(1800, 0.05, 0.5, gameover=-50), partie(900, 0.1, 0.3)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9), True, True),
                         (0.05, 0.5, dict(RECOMPENSES, gameover=-50), "meilleurs"))

    def test_essai_de_parametres_voisins(self):
        parties = [partie(1800, 0.05, 0.5)]
        # RngFixe.choice prend le 1er élément : learning_rate x0.5, discount -0.1, goal x0.5
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.1), True, True),
                         (0.025, 0.4, dict(RECOMPENSES, goal=1024), "essai"))

    def test_ignore_les_parties_d_une_autre_taille(self):
        parties = [partie(9999, 0.9, 0.9, taille=3), partie(100, 0.02, 0.3)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9), True, True),
                         (0.02, 0.3, RECOMPENSES, "meilleurs"))

    def test_approche_a_recompenses_du_env(self):
        """OPTIMISER_RECOMPENSES=false : seules les parties jouées avec les récompenses du .env comptent."""
        parties = [partie(9999, 0.9, 0.9, gameover=-50), partie(100, 0.02, 0.3)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9), True, False),
                         (0.02, 0.3, RECOMPENSES, "meilleurs"))
        # un essai ne touche pas aux récompenses
        lr, df, recompenses, choix = memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.1),
                                                                   True, False)
        self.assertEqual((recompenses, choix), (RECOMPENSES, "essai"))

    def test_recompenses_seules(self):
        """OPTIMISER_PARAMETRES=false, OPTIMISER_RECOMPENSES=true : learning_rate du .env, récompenses du CSV."""
        parties = [partie(1800, 0.05, 0.5, gameover=-50)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9), False, True),
                         (LEARNING_RATE, DISCOUNT_FACTOR, dict(RECOMPENSES, gameover=-50), "meilleurs"))

    def test_rien_a_optimiser(self):
        parties = [partie(1800, 0.05, 0.5, gameover=-50)]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9), False, False),
                         (LEARNING_RATE, DISCOUNT_FACTOR, RECOMPENSES, "defaut"))

    def test_ne_compare_que_la_meme_vision(self):
        parties = [dict(partie(9999, 0.9, 0.9), vision="simplifiee"), dict(partie(100, 0.02, 0.3), vision="grille")]
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9), True, False,
                                                       "grille")[:2], (0.02, 0.3))
        self.assertEqual(memoire_ia.choisir_parametres(parties, 4, RECOMPENSES, RngFixe(0.9), True, False,
                                                       "simplifiee")[:2], (0.9, 0.9))

    def test_essai_reste_dans_les_bornes(self):
        lr, df, _, _ = memoire_ia.choisir_parametres([partie(10, 0.001, 0.0)], 4, RECOMPENSES, RngFixe(0.1), True, True)
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

    def _fin_de_partie(self, agent, chemin_parties):
        """Comme le jeu : Q-table sauvegardée, puis ligne ajoutée au CSV."""
        memoire_ia.memoriser_fin_de_partie(agent, chemin_parties)
        enregistrer_partie(ligne_partie(agent, 10, 1.0), chemin_parties)

    def test_un_fichier_par_tentative_dans_le_dossier(self):
        chemin_parties = os.path.join(self.dossier, "parties.csv")
        dossier_q = os.path.join(self.dossier, "q-table")
        with mock.patch.dict(os.environ, {"DOSSIER_QTABLE": dossier_q}):
            for _ in range(3):
                agent = agent_module.Agent(Environment(3))
                memoire_ia.preparer_agent(agent, False, True, chemin_parties)
                self._agent_prepare(agent)
                self._fin_de_partie(agent, chemin_parties)
        self.assertEqual(sorted(os.listdir(dossier_q)),
                         ["qtable_3x3_T1.json", "qtable_3x3_T2.json", "qtable_3x3_T3.json"])
        self.assertEqual(memoire_ia.qtables_sauvegardees(3, dossier_q)[0],
                         os.path.join(dossier_q, "qtable_3x3_T3.json"))

    def test_recharge_la_derniere_tentative_avec_les_memes_recompenses(self):
        chemin_parties = os.path.join(self.dossier, "parties.csv")
        dossier_q = os.path.join(self.dossier, "q-table")
        autres = dict(RECOMPENSES, gameover=-50)
        with mock.patch.dict(os.environ, {"DOSSIER_QTABLE": dossier_q}):
            # T1 avec les récompenses du .env, puis T2 : essai avec d'autres récompenses
            for recompenses in (RECOMPENSES, autres):
                agent = agent_module.Agent(Environment(3))
                agent.environment.recompenses = dict(recompenses)
                memoire_ia.preparer_agent(agent, optimiser=False, persistante=True,
                                          chemin_parties=chemin_parties)
                self._agent_prepare(agent)
                self._fin_de_partie(agent, chemin_parties)
                if recompenses == RECOMPENSES:
                    etats_env = set(agent.learning_policy.qtable)
            self.assertEqual(memoire_ia.derniere_qtable(3, autres, dossier_q, VISION),
                             os.path.join(dossier_q, "qtable_3x3_T2.json"))
            # retour aux récompenses du .env : c'est T1 qui est rechargée, pas T2
            self.assertEqual(memoire_ia.derniere_qtable(3, RECOMPENSES, dossier_q, VISION),
                             os.path.join(dossier_q, "qtable_3x3_T1.json"))
            agent = agent_module.Agent(Environment(3))
            memoire_ia.preparer_agent(agent, optimiser=False, persistante=True,
                                      chemin_parties=chemin_parties)
        # tous les états appris avec ces récompenses sont retrouvés (+ la grille de départ du nouvel agent)
        self.assertTrue(etats_env <= set(agent.learning_policy.qtable))
        self.assertLessEqual(len(agent.learning_policy.qtable), len(etats_env) + 1)

    def test_dossier_absent_ou_vide(self):
        dossier_q = os.path.join(self.dossier, "q-table")
        self.assertEqual(memoire_ia.qtables_sauvegardees(4, dossier_q), [])
        self.assertIsNone(memoire_ia.derniere_qtable(4, RECOMPENSES, dossier_q))

    def test_recompenses_changees_qtable_remise_a_zero(self):
        chemin = os.path.join(self.dossier, "qtable.json")
        agent = self._agent()
        memoire_ia.sauvegarder_qtable(agent.learning_policy, chemin, 3, RECOMPENSES)
        nouvel_agent = agent_module.Agent(Environment(3))
        nb_etats = memoire_ia.charger_qtable(nouvel_agent.learning_policy, chemin,
                                             dict(RECOMPENSES, gameover=-50))
        self.assertEqual(nb_etats, 0)
        self.assertEqual(len(nouvel_agent.learning_policy.qtable), 1)  # seulement l'état initial

    def test_preparer_applique_les_recompenses_choisies(self):
        chemin_parties = os.path.join(self.dossier, "parties.csv")
        agent = self._agent()
        agent.environment.recompenses = dict(RECOMPENSES, gameover=-50)
        enregistrer_partie(ligne_partie(agent, 10, 1.0), chemin_parties)
        nouvel_agent = agent_module.Agent(Environment(3))
        memoire_ia.preparer_agent(nouvel_agent, True, False, chemin_parties, RngFixe(0.9),
                                  optimiser_recompenses=True)
        self.assertEqual(nouvel_agent.environment.recompenses["gameover"], -50)

    def test_preparer_puis_memoriser(self):
        chemin_parties = os.path.join(self.dossier, "parties.csv")
        with mock.patch.dict(os.environ, {"DOSSIER_QTABLE": os.path.join(self.dossier, "q-table")}):
            # 1re partie : aucun historique, Q-table vide
            agent = agent_module.Agent(Environment(3))
            memoire_ia.preparer_agent(agent, True, True, chemin_parties, RngFixe(0.9))
            self.assertEqual(agent.choix_parametres, "defaut")
            agent = self._agent_prepare(agent)
            self._fin_de_partie(agent, chemin_parties)
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
        dossier_q = os.path.join(self.dossier, "q-table")
        with mock.patch.dict(os.environ, {"DOSSIER_QTABLE": dossier_q}):
            agent = self._agent()
            memoire_ia.preparer_agent(agent, optimiser=False, persistante=False)
            memoire_ia.memoriser_fin_de_partie(agent, os.path.join(self.dossier, "parties.csv"))
        self.assertFalse(os.path.exists(dossier_q))
        self.assertEqual(agent.choix_parametres, "defaut")


class NouvellePartieTest(unittest.TestCase):
    """Enchaînement de plusieurs parties dans le même lancement (NB_TOURS_MAX)."""

    def setUp(self):
        dossier = tempfile.TemporaryDirectory()
        self.addCleanup(dossier.cleanup)
        self.dossier = dossier.name

    def _jouer(self, agent):
        with mock.patch.object(agent_module, "MODE_APPRENTISSAGE", True):
            agent.do(init=True)
            while agent.continue_game():
                agent.do()

    def test_sans_persistance_l_apprentissage_reste_en_memoire(self):
        agent = agent_module.Agent(Environment(3))
        self._jouer(agent)
        etats = set(agent.learning_policy.qtable)
        agent.reset()
        memoire_ia.nouvelle_partie(agent, optimiser=False, persistante=False)
        self.assertTrue(agent.continue_game())
        self.assertEqual(set(agent.learning_policy.qtable), etats)

    def test_approche_b_recompenses_changees_qtable_en_memoire_videe(self):
        chemin_parties = os.path.join(self.dossier, "parties.csv")
        agent = agent_module.Agent(Environment(3))
        self._jouer(agent)
        # la meilleure partie du CSV a été jouée avec d'autres récompenses
        agent.environment.recompenses = dict(RECOMPENSES, gameover=-50)
        enregistrer_partie(ligne_partie(agent, 10, 1.0), chemin_parties)
        agent.environment.recompenses = dict(RECOMPENSES)
        agent.reset()
        memoire_ia.nouvelle_partie(agent, True, False, chemin_parties, RngFixe(0.9),
                                   optimiser_recompenses=True)
        self.assertEqual(agent.environment.recompenses["gameover"], -50)
        self.assertEqual(agent.learning_policy.qtable, {})

    def test_avec_persistance_qtable_rechargee_et_parametres_choisis(self):
        chemin_parties = os.path.join(self.dossier, "parties.csv")
        with mock.patch.dict(os.environ, {"DOSSIER_QTABLE": os.path.join(self.dossier, "q-table")}):
            agent = agent_module.Agent(Environment(3))
            memoire_ia.preparer_agent(agent, True, True, chemin_parties, RngFixe(0.9))
            self._jouer(agent)
            memoire_ia.memoriser_fin_de_partie(agent, chemin_parties)
            enregistrer_partie(ligne_partie(agent, 10, 1.0), chemin_parties)
            etats = set(agent.learning_policy.qtable)
            agent.reset()
            memoire_ia.nouvelle_partie(agent, True, True, chemin_parties, RngFixe(0.9))
        self.assertEqual(agent.choix_parametres, "meilleurs")
        self.assertTrue(etats <= set(agent.learning_policy.qtable))


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
