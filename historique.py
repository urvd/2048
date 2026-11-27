"""Historique des parties jouées par l'IA, enregistré dans un fichier CSV local.

Étape 1 : à la fin de chaque partie en mode apprentissage, une ligne est ajoutée.
Étape 2 : l'IA relit ce fichier pour choisir de meilleurs paramètres (voir memoire_ia.py).
"""
import csv
import os

from game_params import GAME_SPEED

FICHIER_PARTIES = os.getenv("FICHIER_PARTIES_IA", "parties_ia.csv")
SEPARATEUR = ";"  # s'ouvre directement dans un Excel configuré en français

COLONNES = [
    # Partie
    "tentative",
    "taille_grille",
    "nb_etapes",
    "score_total",
    "meilleure_tuile",
    "nb_cases_max",
    "tuile_2048_trouvee",
    "duree_secondes",
    # Paramètres du jeu
    "intervalle_deplacement",
    # Paramètres de l'IA
    "learning_rate",
    "discount_factor",
    "exploration",
    "vision",
    "reward_default",
    "reward_goal",
    "reward_gameover",
    "reward_no_effect",
    "choix_parametres",
    "qtable_persistante",
    # Statistiques d'apprentissage
    "nb_etats_appris",
    "nb_mises_a_jour_qtable",
]


def ligne_partie(agent, nb_etapes, duree_secondes):
    """Construit la ligne CSV d'une partie terminée."""
    environment = agent.environment
    policy = agent.learning_policy
    recompenses = environment.recompenses
    return {
        "taille_grille": environment.length,
        "nb_etapes": nb_etapes,
        "score_total": agent.state_score,
        "meilleure_tuile": max(environment.states.values()),
        "nb_cases_max": list(environment.states.values()).count(max(environment.states.values())),
        "tuile_2048_trouvee": "oui" if environment.goal else "non",
        "duree_secondes": round(duree_secondes, 1),
        "intervalle_deplacement": GAME_SPEED,
        "learning_rate": policy.learning_rate,
        "discount_factor": policy.discount_factor,
        "exploration": policy.exploration,
        "vision": "simplifiee" if agent.vision_simplifiee else "grille",
        "reward_default": recompenses["default"],
        "reward_goal": recompenses["goal"],
        "reward_gameover": recompenses["gameover"],
        "reward_no_effect": recompenses["no_effect"],
        "choix_parametres": agent.choix_parametres,
        "qtable_persistante": "oui" if agent.fichier_qtable else "non",
        "nb_etats_appris": len(policy.qtable),
        "nb_mises_a_jour_qtable": policy.cas_total,
    }


def lire_parties(chemin=None):
    """Toutes les parties enregistrées, sous forme de dictionnaires (liste vide si pas de fichier)."""
    chemin = chemin or FICHIER_PARTIES
    if not os.path.exists(chemin):
        return []
    with open(chemin, newline="", encoding="utf-8") as fichier:
        return list(csv.DictReader(fichier, delimiter=SEPARATEUR))


def _migrer_colonnes(chemin):
    """Réécrit le fichier avec les colonnes actuelles si son en-tête est ancien.

    Les colonnes ajoutées depuis restent vides pour les anciennes lignes.
    """
    with open(chemin, newline="", encoding="utf-8") as fichier:
        en_tete = next(csv.reader(fichier, delimiter=SEPARATEUR), None)
    if en_tete is None or en_tete == COLONNES:
        return
    parties = lire_parties(chemin)
    with open(chemin, "w", newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=COLONNES, delimiter=SEPARATEUR,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(parties)


def derniere_tentative(chemin):
    """Numéro de la dernière tentative enregistrée dans le fichier (0 si aucune)."""
    numeros = [int(row["tentative"]) for row in lire_parties(chemin)
               if (row.get("tentative") or "").isdigit()]
    return max(numeros, default=0)


def enregistrer_partie(ligne, chemin=None):
    """Ajoute une ligne au fichier CSV avec le numéro de tentative suivant.

    L'en-tête est écrit à la création du fichier. Renvoie le chemin et le numéro de tentative.
    """
    chemin = chemin or FICHIER_PARTIES
    nouveau_fichier = not os.path.exists(chemin) or os.path.getsize(chemin) == 0
    if not nouveau_fichier:
        _migrer_colonnes(chemin)
    ligne = {"tentative": derniere_tentative(chemin) + 1, **ligne}
    with open(chemin, "a", newline="", encoding="utf-8") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=COLONNES, delimiter=SEPARATEUR)
        if nouveau_fichier:
            writer.writeheader()
        writer.writerow(ligne)
    return chemin, ligne["tentative"]
