"""Mémoire de l'IA d'une partie à l'autre (option B).

Approche 1 (OPTIMISER_PARAMETRES) : learning_rate, discount_factor ET les récompenses
sont choisis d'après le CSV des parties. On reprend ceux de la meilleure tentative et,
de temps en temps, on essaie des valeurs voisines pour découvrir de meilleurs réglages.
Sans historique, les récompenses sont celles du .env.

Approche 2 (QTABLE_PERSISTANTE) : la Q-table est sauvegardée en fin de partie dans un
fichier JSON local et rechargée au lancement suivant, SAUF si les récompenses ont changé :
ses valeurs n'auraient plus la même échelle, l'IA repart alors d'une Q-table vide.
"""
import json
import os
import random

from game_params import (DEFAULT_DISCOUNT_FACTOR, DEFAULT_LEARNING_RATE, OPTIMISER_PARAMETRES,
                         QTABLE_PERSISTANTE)
from historique import lire_parties

# Probabilité d'essayer des paramètres voisins au lieu des meilleurs
TAUX_ESSAI = 0.2
LEARNING_RATE_MIN, LEARNING_RATE_MAX = 0.001, 1.0
DISCOUNT_FACTOR_MIN, DISCOUNT_FACTOR_MAX = 0.0, 0.99
# Récompenses que l'optimisation peut modifier (reward_default n'est pas utilisée par le jeu)
RECOMPENSES_OPTIMISEES = ("goal", "gameover", "no_effect")


def fichier_qtable(taille):
    """Une Q-table par taille de grille (les états d'une grille 3x3 et 4x4 n'ont rien en commun)."""
    return os.getenv("FICHIER_QTABLE") or f"qtable_{taille}x{taille}.json"


# --- Approche 2 : Q-table persistante -------------------------------------------------

def sauvegarder_qtable(policy, chemin, taille, recompenses):
    """Écrit la Q-table et le contexte dans lequel elle a été apprise."""
    donnees = {"taille": taille, "recompenses": recompenses, "qtable": policy.qtable}
    temporaire = chemin + ".tmp"
    with open(temporaire, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier)
    os.replace(temporaire, chemin)  # pas de fichier à moitié écrit si le jeu est coupé


def charger_qtable(policy, chemin, recompenses):
    """Recharge la Q-table sauvegardée. Renvoie le nombre d'états chargés.

    Si elle a été apprise avec d'autres récompenses, elle n'est pas rechargée (option B) :
    l'IA repart d'une Q-table vide, qui remplacera l'ancienne en fin de partie.
    """
    if not os.path.exists(chemin):
        return 0
    with open(chemin, encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    if donnees.get("recompenses") != recompenses:
        print(f"Récompenses changées depuis la dernière sauvegarde ({donnees.get('recompenses')}) : "
              f"la Q-table de {chemin} est remise à zéro.")
        return 0
    for etat, valeurs in donnees.get("qtable", {}).items():
        policy.qtable[etat] = {action: float(q) for action, q in valeurs.items()}
    return len(donnees.get("qtable", {}))


# --- Approche 1 : paramètres choisis d'après le CSV ------------------------------------

def _recompenses_de(partie):
    return {cle: int(partie["reward_" + cle]) for cle in ("default", "goal", "gameover", "no_effect")}


def _comparable(partie, taille):
    """Partie jouée sur la même taille de grille, avec des colonnes lisibles ?"""
    try:
        float(partie["score_total"]), float(partie["learning_rate"]), float(partie["discount_factor"])
        _recompenses_de(partie)
        return int(partie["taille_grille"]) == taille
    except (KeyError, TypeError, ValueError):
        return False


def meilleure_partie(parties, taille):
    """Partie au meilleur score sur la même taille de grille (None s'il n'y en a pas).

    Le score du jeu ne dépend pas des récompenses : on compare donc toutes les parties.
    """
    comparables = [p for p in parties if _comparable(p, taille)]
    return max(comparables, key=lambda p: float(p["score_total"]), default=None)


def _borner(valeur, minimum, maximum):
    return round(min(max(valeur, minimum), maximum), 4)


def choisir_parametres(parties, taille, recompenses_env, rng=random):
    """Renvoie (learning_rate, discount_factor, recompenses, choix).

    choix vaut defaut (pas d'historique : valeurs du .env), meilleurs ou essai.
    """
    meilleure = meilleure_partie(parties, taille)
    if meilleure is None:
        return DEFAULT_LEARNING_RATE, DEFAULT_DISCOUNT_FACTOR, dict(recompenses_env), "defaut"
    learning_rate = float(meilleure["learning_rate"])
    discount_factor = float(meilleure["discount_factor"])
    recompenses = _recompenses_de(meilleure)
    if rng.random() >= TAUX_ESSAI:
        return learning_rate, discount_factor, recompenses, "meilleurs"
    # Essai : paramètres voisins et une récompense modifiée pour explorer d'autres réglages
    learning_rate = _borner(learning_rate * rng.choice([0.5, 2.0]), LEARNING_RATE_MIN, LEARNING_RATE_MAX)
    discount_factor = _borner(discount_factor + rng.choice([-0.1, 0.1]), DISCOUNT_FACTOR_MIN,
                              DISCOUNT_FACTOR_MAX)
    cle = rng.choice(RECOMPENSES_OPTIMISEES)
    recompenses[cle] = int(recompenses[cle] * rng.choice([0.5, 2.0])) or recompenses[cle]
    return learning_rate, discount_factor, recompenses, "essai"


# --- Points d'entrée utilisés par le jeu ------------------------------------------------

def preparer_agent(agent, optimiser=OPTIMISER_PARAMETRES, persistante=QTABLE_PERSISTANTE,
                   chemin_parties=None, rng=random):
    """À appeler une fois au lancement, avant la première partie de l'IA."""
    environment = agent.environment
    policy = agent.learning_policy
    if optimiser:
        (policy.learning_rate, policy.discount_factor, environment.recompenses,
         agent.choix_parametres) = choisir_parametres(lire_parties(chemin_parties), environment.length,
                                                      environment.recompenses, rng)
    print(f"Paramètres de l'IA ({agent.choix_parametres}) : learning_rate={policy.learning_rate}, "
          f"discount_factor={policy.discount_factor}, récompenses={environment.recompenses}")
    if persistante:
        agent.fichier_qtable = fichier_qtable(environment.length)
        nb_etats = charger_qtable(policy, agent.fichier_qtable, environment.recompenses)
        print(f"Q-table : {nb_etats} états chargés depuis {agent.fichier_qtable}")


def memoriser_fin_de_partie(agent):
    """À appeler à la fin d'une partie de l'IA : sauvegarde la Q-table si elle est persistante."""
    if agent.fichier_qtable:
        environment = agent.environment
        sauvegarder_qtable(agent.learning_policy, agent.fichier_qtable, environment.length,
                           environment.recompenses)
        print(f"Q-table sauvegardée : {len(agent.learning_policy.qtable)} états dans {agent.fichier_qtable}")
