"""Mémoire de l'IA d'une partie à l'autre (option C).

Approche 1 (OPTIMISER_PARAMETRES) : learning_rate, discount_factor ET les récompenses
sont choisis d'après le CSV des parties. On reprend ceux de la meilleure tentative et,
de temps en temps, on essaie des valeurs voisines pour découvrir de meilleurs réglages.
Sans historique, les récompenses sont celles du .env.

Approche 2 (QTABLE_PERSISTANTE) : à la fin de chaque partie, la Q-table est sauvegardée
dans le dossier q-table/, dans un fichier numéroté comme la tentative du CSV
(q-table/qtable_4x4_T12.json), avec les récompenses avec lesquelles elle a été apprise.
Au lancement, l'IA recharge la Q-table de la tentative la plus récente jouée avec les
mêmes récompenses : un essai de récompenses n'efface donc jamais ce qui a été appris
avec les autres.
"""
import json
import os
import random
import re

from game_params import (DISCOUNT_FACTOR, LEARNING_RATE, OPTIMISER_PARAMETRES,
                         QTABLE_PERSISTANTE)
from historique import FICHIER_PARTIES, derniere_tentative, lire_parties

# Probabilité d'essayer des paramètres voisins au lieu des meilleurs
TAUX_ESSAI = 0.2
LEARNING_RATE_MIN, LEARNING_RATE_MAX = 0.001, 1.0
DISCOUNT_FACTOR_MIN, DISCOUNT_FACTOR_MAX = 0.0, 0.99
# Récompenses que l'optimisation peut modifier (reward_default n'est pas utilisée par le jeu)
RECOMPENSES_OPTIMISEES = ("goal", "gameover", "no_effect")


def dossier_qtable():
    """Dossier des Q-tables sauvegardées (DOSSIER_QTABLE, q-table par défaut)."""
    return os.getenv("DOSSIER_QTABLE") or "q-table"


def fichier_qtable(taille, tentative, dossier=None):
    """Fichier de la Q-table sauvegardée à la fin d'une tentative : q-table/qtable_4x4_T12.json."""
    return os.path.join(dossier or dossier_qtable(), f"qtable_{taille}x{taille}_T{tentative}.json")


def qtables_sauvegardees(taille, dossier=None):
    """Q-tables sauvegardées pour cette taille de grille, de la plus récente à la plus ancienne."""
    dossier = dossier or dossier_qtable()
    if not os.path.isdir(dossier):
        return []
    motif = re.compile(rf"^qtable_{taille}x{taille}_T(\d+)\.json$")
    trouvees = [(int(m.group(1)), os.path.join(dossier, nom))
                for nom in os.listdir(dossier) if (m := motif.match(nom))]
    return [chemin for _, chemin in sorted(trouvees, reverse=True)]


def derniere_qtable(taille, recompenses, dossier=None):
    """Q-table de la tentative la plus récente jouée avec ces récompenses (None s'il n'y en a pas)."""
    for chemin in qtables_sauvegardees(taille, dossier):
        try:
            with open(chemin, encoding="utf-8") as fichier:
                if json.load(fichier).get("recompenses") == recompenses:
                    return chemin
        except (OSError, ValueError):
            continue  # fichier illisible : on passe au précédent
    return None


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

    Par sécurité, une Q-table apprise avec d'autres récompenses n'est pas rechargée.
    """
    if not os.path.exists(chemin):
        return 0
    with open(chemin, encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    if donnees.get("recompenses") != recompenses:
        print(f"Attention : {chemin} contient une Q-table apprise avec d'autres récompenses "
              f"({donnees.get('recompenses')}) : elle n'est pas rechargée.")
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
        return LEARNING_RATE, DISCOUNT_FACTOR, dict(recompenses_env), "defaut"
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
        # agent.fichier_qtable contient le dossier des Q-tables (None : non persistante)
        agent.fichier_qtable = dossier_qtable()
        chemin = derniere_qtable(environment.length, environment.recompenses, agent.fichier_qtable)
        if chemin is None:
            print(f"Q-table : aucune sauvegarde avec ces récompenses dans {agent.fichier_qtable}, "
                  f"l'IA part de zéro")
        else:
            nb_etats = charger_qtable(policy, chemin, environment.recompenses)
            print(f"Q-table : {nb_etats} états chargés depuis {chemin}")


def memoriser_fin_de_partie(agent, chemin_parties=None):
    """À appeler à la fin d'une partie de l'IA, avant d'écrire la ligne du CSV.

    Sauvegarde la Q-table (si elle est persistante) dans q-table/qtable_<taille>_T<n>.json,
    n étant le numéro que la partie va recevoir dans le CSV.
    """
    if agent.fichier_qtable:
        environment = agent.environment
        tentative = derniere_tentative(chemin_parties or FICHIER_PARTIES) + 1
        chemin = fichier_qtable(environment.length, tentative, agent.fichier_qtable)
        os.makedirs(agent.fichier_qtable, exist_ok=True)
        sauvegarder_qtable(agent.learning_policy, chemin, environment.length, environment.recompenses)
        print(f"Q-table sauvegardée : {len(agent.learning_policy.qtable)} états dans {chemin}")


def nouvelle_partie(agent, optimiser=OPTIMISER_PARAMETRES, persistante=QTABLE_PERSISTANTE,
                    chemin_parties=None, rng=random):
    """Prépare la partie suivante quand l'IA enchaîne plusieurs parties (NB_TOURS_MAX).

    À appeler après agent.reset() : les paramètres sont choisis à nouveau d'après le CSV,
    qui contient maintenant la partie qui vient de se terminer. Avec une Q-table persistante,
    elle est rechargée depuis le fichier sauvegardé en fin de partie ; sinon l'IA garde en
    mémoire ce qu'elle a appris depuis le lancement (tant que les récompenses ne changent pas).
    """
    policy = agent.learning_policy
    recompenses_avant = dict(agent.environment.recompenses)
    qtable_en_memoire = policy.qtable
    policy.qtable = {}
    preparer_agent(agent, optimiser, persistante, chemin_parties, rng)
    if not persistante and agent.environment.recompenses == recompenses_avant:
        policy.qtable = qtable_en_memoire
