"""Historique des parties jouées par l'IA, enregistré dans un fichier CSV local.

Étape 1 : à la fin de chaque partie en mode apprentissage, une ligne est ajoutée.
Étape 2 (à venir) : l'IA relira ce fichier pour choisir de meilleurs paramètres.
"""
import csv
import os
from datetime import datetime

import game_params

FICHIER_PARTIES = os.getenv("FICHIER_PARTIES_IA", "parties_ia.csv")
SEPARATEUR = ";"  # s'ouvre directement dans un Excel configuré en français

COLONNES = [
    # Partie
    "date",
    "heure",
    "taille_grille",
    "nb_etapes",
    "score_total",
    "meilleure_tuile",
    "tuile_2048_trouvee",
    "duree_secondes",
    # Paramètres du jeu
    "vitesse_simulation",
    # Paramètres de l'IA
    "learning_rate",
    "discount_factor",
    "reward_default",
    "reward_goal",
    "reward_gameover",
    "reward_no_effect",
    # Statistiques d'apprentissage
    "nb_etats_appris",
    "nb_mises_a_jour_qtable",
]


def ligne_partie(agent, nb_etapes, duree_secondes):
    """Construit la ligne CSV d'une partie terminée."""
    environment = agent.environment
    policy = agent.learning_policy
    maintenant = datetime.now()
    return {
        "date": maintenant.strftime("%d/%m/%Y"),
        "heure": maintenant.strftime("%H:%M:%S"),
        "taille_grille": environment.length,
        "nb_etapes": nb_etapes,
        "score_total": agent.state_score,
        "meilleure_tuile": max(environment.states.values()),
        "tuile_2048_trouvee": "oui" if environment.goal else "non",
        "duree_secondes": round(duree_secondes, 1),
        "vitesse_simulation": game_params.GAME_SPEED,
        "learning_rate": policy.learning_rate,
        "discount_factor": policy.discount_factor,
        "reward_default": game_params.REWARD_DEFAULT,
        "reward_goal": game_params.REWARD_GOAL,
        "reward_gameover": game_params.REWARD_GAMEOVER,
        "reward_no_effect": game_params.REWARD_NO_EFFECT,
        "nb_etats_appris": len(policy.qtable),
        "nb_mises_a_jour_qtable": policy.cas_total,
    }


def enregistrer_partie(ligne, chemin=None):
    """Ajoute une ligne au fichier CSV (l'en-tête est écrit à la création du fichier)."""
    chemin = chemin or FICHIER_PARTIES
    nouveau_fichier = not os.path.exists(chemin) or os.path.getsize(chemin) == 0
    with open(chemin, "a", newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=COLONNES, delimiter=SEPARATEUR)
        if nouveau_fichier:
            writer.writeheader()
        writer.writerow(ligne)
    return chemin
