"""Lecture des variables d'environnement et chargement automatique du .env."""
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from game_params import env_bool  # noqa: E402


class EnvBoolTest(unittest.TestCase):
    def test_valeurs_vraies(self):
        for valeur in ("true", "True", "TRUE", " true ", "1", "oui", "yes", "vrai", '"true"'):
            with self.subTest(valeur=valeur), mock.patch.dict(os.environ, {"VAR_TEST": valeur}):
                self.assertTrue(env_bool("VAR_TEST", False))

    def test_valeurs_fausses_et_defaut(self):
        for valeur in ("false", "False", "0", "non", "no"):
            with self.subTest(valeur=valeur), mock.patch.dict(os.environ, {"VAR_TEST": valeur}):
                self.assertFalse(env_bool("VAR_TEST", True))
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertTrue(env_bool("VAR_TEST", True))


class ChargementEnvTest(unittest.TestCase):
    def test_env_charge_sans_le_sourcer(self):
        """Lancé depuis un autre dossier, game_params lit le .env placé à côté du code."""
        with tempfile.TemporaryDirectory() as dossier:
            # copie de game_params avec un .env voisin
            with open(os.path.join(RACINE, "game_params.py"), encoding="utf-8") as source:
                code = source.read()
            with open(os.path.join(dossier, "game_params.py"), "w", encoding="utf-8") as copie:
                copie.write(code)
            with open(os.path.join(dossier, ".env"), "w", encoding="utf-8") as env:
                env.write("MODE_APPRENTISSAGE=True\nQTABLE_PERSISTANTE=false\n")
            environnement = {k: v for k, v in os.environ.items()
                             if k not in ("MODE_APPRENTISSAGE", "QTABLE_PERSISTANTE")}
            sortie = subprocess.run(
                [sys.executable, "-c", "import game_params as g; print(g.MODE_APPRENTISSAGE, g.QTABLE_PERSISTANTE)"],
                cwd=tempfile.gettempdir(), env=dict(environnement, PYTHONPATH=dossier),
                capture_output=True, text=True, check=True)
        self.assertEqual(sortie.stdout.split(), ["True", "False"])


if __name__ == "__main__":
    unittest.main()
