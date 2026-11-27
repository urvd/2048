"""Mémoire de l'IA d'une partie à l'autre : les approches A, B, C et D réunies.

Quatre réglages indépendants (fichier .env) :

- OPTIMISER_PARAMETRES  : learning_rate et discount_factor sont repris de la meilleure tentative
  du CSV ; une fois sur 5, l'IA essaie des valeurs voisines.
- OPTIMISER_RECOMPENSES : les récompenses (goal, gameover, no_effect) sont aussi reprises de la
  meilleure tentative et modifiées lors des essais. Sinon, ce sont toujours celles du .env et
  l'IA ne compare que des parties jouées avec ces récompenses.
- QTABLE_PERSISTANTE    : à la fin de chaque partie, la Q-table est sauvegardée dans q-table/MxM/,
  dans un fichier numéroté comme la tentative du CSV (q-table/4x4/qtable_4x4_T12.json). Au lancement,
  l'IA recharge la Q-table de la MEILLEURE tentative jouée avec les mêmes récompenses et la même
  vision (plus grande tuile, puis nombre de cases à cette valeur, puis score).
  Sinon, la Q-table reste en mémoire pendant la série de parties (NB_TOURS_MAX) et repart de
  zéro si les récompenses changent.
- VISION_SIMPLIFIEE     : l'IA voit un résumé de la grille (vision.py) au lieu de la grille exacte.

Correspondance avec les approches étudiées :
  A = OPTIMISER_PARAMETRES (récompenses du .env)
  B = OPTIMISER_PARAMETRES + OPTIMISER_RECOMPENSES
  C = B + QTABLE_PERSISTANTE
  D = C + VISION_SIMPLIFIEE
"""
import json
import os
import random
import re

from game_params import (DISCOUNT_FACTOR, DOSSIER_QTABLE, LEARNING_RATE, OPTIMISER_PARAMETRES,
                         OPTIMISER_RECOMPENSES, QTABLE_PERSISTANTE)
from historique import FICHIER_PARTIES, derniere_tentative, lire_parties

# Probabilité d'essayer des paramètres voisins au lieu des meilleurs
TAUX_ESSAI = 0.2
LEARNING_RATE_MIN, LEARNING_RATE_MAX = 0.001, 1.0
DISCOUNT_FACTOR_MIN, DISCOUNT_FACTOR_MAX = 0.0, 0.99
# Récompenses que l'optimisation peut modifier (reward_default n'est pas utilisée par le jeu)
RECOMPENSES_OPTIMISEES = ("goal", "gameover", "no_effect")


def _vision(agent):
    return "simplifiee" if agent.vision_simplifiee else "grille"


# --- Q-table persistante : q-table/<M>x<M>/, un fichier par tentative -----------------

def dossier_qtable(taille):
    """Dossier des Q-tables d'une taille de grille : q-table/4x4."""
    return os.path.join(DOSSIER_QTABLE, f"{taille}x{taille}")


def fichier_qtable(taille, tentative, dossier=None):
    """Fichier de la Q-table sauvegardée à la fin d'une tentative : q-table/4x4/qtable_4x4_T12.json."""
    return os.path.join(dossier or dossier_qtable(taille), f"qtable_{taille}x{taille}_T{tentative}.json")


def _motif(taille):
    return re.compile(rf"^qtable_{taille}x{taille}_T(\d+)\.json$")


def numero_tentative(chemin, taille):
    """Numéro de tentative d'un fichier de Q-table (None si le nom ne correspond pas)."""
    m = _motif(taille).match(os.path.basename(chemin))
    return int(m.group(1)) if m else None


def qtables_sauvegardees(taille, dossier=None):
    """Q-tables sauvegardées pour cette taille de grille, de la plus récente à la plus ancienne."""
    dossier = dossier or dossier_qtable(taille)
    if not os.path.isdir(dossier):
        return []
    trouvees = [(numero_tentative(nom, taille), os.path.join(dossier, nom)) for nom in os.listdir(dossier)]
    return [chemin for numero, chemin in sorted((t for t in trouvees if t[0] is not None), reverse=True)]


def cle_classement(partie):
    """Qualité d'une tentative, d'après sa ligne du CSV (plus grand = meilleur) :
    1. la plus grande tuile atteinte, 2. le nombre de cases à cette valeur, 3. le score.
    Une tentative absente du CSV (ou illisible) est classée en dernier.
    """
    try:
        return (int(partie["meilleure_tuile"]), int(partie.get("nb_cases_max") or 0),
                int(float(partie["score_total"])))
    except (KeyError, TypeError, ValueError):
        return (-1, -1, -1)


def classer_qtables(taille, parties, dossier=None):
    """Q-tables sauvegardées, de la meilleure à la moins bonne (à égalité : la plus récente d'abord)."""
    par_tentative = {}
    for partie in parties:
        if (partie.get("tentative") or "").isdigit():
            par_tentative[int(partie["tentative"])] = partie
    chemins = qtables_sauvegardees(taille, dossier)
    return sorted(chemins, reverse=True,
                  key=lambda c: (cle_classement(par_tentative.get(numero_tentative(c, taille))),
                                 numero_tentative(c, taille)))


def _meme_apprentissage(donnees, recompenses, vision):
    """La Q-table a-t-elle été apprise avec ces récompenses et cette vision ?"""
    return (donnees.get("recompenses") == recompenses
            and (donnees.get("vision") or "grille") == vision)


def meilleure_qtable(taille, recompenses, parties, dossier=None, vision="grille"):
    """Q-table de la meilleure tentative jouée avec ces récompenses et cette vision (ou None)."""
    for chemin in classer_qtables(taille, parties, dossier):
        try:
            with open(chemin, encoding="utf-8") as fichier:
                if _meme_apprentissage(json.load(fichier), recompenses, vision):
                    return chemin
        except (OSError, ValueError):
            continue  # fichier illisible : on passe au suivant
    return None


def sauvegarder_qtable(policy, chemin, taille, recompenses, vision="grille"):
    """Écrit la Q-table et le contexte dans lequel elle a été apprise."""
    donnees = {"taille": taille, "recompenses": recompenses, "vision": vision, "qtable": policy.qtable}
    temporaire = chemin + ".tmp"
    with open(temporaire, "w", encoding="utf-8") as fichier:
        json.dump(donnees, fichier)
    os.replace(temporaire, chemin)  # pas de fichier à moitié écrit si le jeu est coupé


def charger_qtable(policy, chemin, recompenses, vision="grille"):
    """Recharge la Q-table sauvegardée. Renvoie le nombre d'états chargés.

    Par sécurité, une Q-table apprise avec d'autres récompenses ou une autre vision
    n'est pas rechargée.
    """
    if not os.path.exists(chemin):
        return 0
    with open(chemin, encoding="utf-8") as fichier:
        donnees = json.load(fichier)
    if not _meme_apprentissage(donnees, recompenses, vision):
        print(f"Attention : {chemin} a été appris avec d'autres récompenses ou une autre vision "
              f"({donnees.get('recompenses')}, {donnees.get('vision') or 'grille'}) : il n'est pas rechargé.")
        return 0
    for etat, valeurs in donnees.get("qtable", {}).items():
        policy.qtable[etat] = {action: float(q) for action, q in valeurs.items()}
    return len(donnees.get("qtable", {}))


# --- Paramètres choisis d'après le CSV --------------------------------------------------

def _recompenses_de(partie):
    return {cle: int(partie["reward_" + cle]) for cle in ("default", "goal", "gameover", "no_effect")}


def _comparable(partie, taille, vision, recompenses=None):
    """Partie lisible, jouée sur la même taille de grille avec la même vision.

    Si recompenses est donné (récompenses non optimisées), elles doivent aussi être identiques.
    """
    try:
        float(partie["score_total"]), float(partie["learning_rate"]), float(partie["discount_factor"])
        recompenses_partie = _recompenses_de(partie)
        return (int(partie["taille_grille"]) == taille
                and (partie.get("vision") or "grille") == vision
                and (recompenses is None or recompenses_partie == recompenses))
    except (KeyError, TypeError, ValueError):
        return False


def meilleure_partie(parties, taille, vision="grille", recompenses=None):
    """Partie au meilleur score parmi les parties comparables (None s'il n'y en a pas)."""
    comparables = [p for p in parties if _comparable(p, taille, vision, recompenses)]
    return max(comparables, key=lambda p: float(p["score_total"]), default=None)


def _borner(valeur, minimum, maximum):
    return round(min(max(valeur, minimum), maximum), 4)


def choisir_parametres(parties, taille, recompenses_env, rng=random, optimiser_parametres=True,
                       optimiser_recompenses=False, vision="grille"):
    """Renvoie (learning_rate, discount_factor, recompenses, choix).

    choix vaut defaut (rien à optimiser ou pas d'historique : valeurs du .env), meilleurs ou essai.
    """
    defaut = (LEARNING_RATE, DISCOUNT_FACTOR, dict(recompenses_env), "defaut")
    if not (optimiser_parametres or optimiser_recompenses):
        return defaut
    meilleure = meilleure_partie(parties, taille, vision,
                                 None if optimiser_recompenses else dict(recompenses_env))
    if meilleure is None:
        return defaut
    learning_rate, discount_factor = LEARNING_RATE, DISCOUNT_FACTOR
    if optimiser_parametres:
        learning_rate = float(meilleure["learning_rate"])
        discount_factor = float(meilleure["discount_factor"])
    recompenses = _recompenses_de(meilleure) if optimiser_recompenses else dict(recompenses_env)
    if rng.random() >= TAUX_ESSAI:
        return learning_rate, discount_factor, recompenses, "meilleurs"
    # Essai : valeurs voisines pour explorer d'autres réglages
    if optimiser_parametres:
        learning_rate = _borner(learning_rate * rng.choice([0.5, 2.0]), LEARNING_RATE_MIN,
                                LEARNING_RATE_MAX)
        discount_factor = _borner(discount_factor + rng.choice([-0.1, 0.1]), DISCOUNT_FACTOR_MIN,
                                  DISCOUNT_FACTOR_MAX)
    if optimiser_recompenses:
        cle = rng.choice(RECOMPENSES_OPTIMISEES)
        recompenses[cle] = int(recompenses[cle] * rng.choice([0.5, 2.0])) or recompenses[cle]
    return learning_rate, discount_factor, recompenses, "essai"


# --- Points d'entrée utilisés par le jeu ------------------------------------------------

def preparer_agent(agent, optimiser=OPTIMISER_PARAMETRES, persistante=QTABLE_PERSISTANTE,
                   chemin_parties=None, rng=random, optimiser_recompenses=OPTIMISER_RECOMPENSES):
    """À appeler au lancement, avant la première partie de l'IA."""
    environment = agent.environment
    policy = agent.learning_policy
    agent.choix_parametres = "defaut"
    if optimiser or optimiser_recompenses:
        (policy.learning_rate, policy.discount_factor, environment.recompenses,
         agent.choix_parametres) = choisir_parametres(
            lire_parties(chemin_parties), environment.length, environment.recompenses, rng,
            optimiser, optimiser_recompenses, _vision(agent))
    print(f"Paramètres de l'IA ({agent.choix_parametres}) : learning_rate={policy.learning_rate}, "
          f"discount_factor={policy.discount_factor}, récompenses={environment.recompenses}, "
          f"vision={_vision(agent)}")
    if persistante:
        # agent.fichier_qtable contient le dossier des Q-tables (None : non persistante)
        agent.fichier_qtable = dossier_qtable(environment.length)
        chemin = meilleure_qtable(environment.length, environment.recompenses, lire_parties(chemin_parties),
                                  agent.fichier_qtable, _vision(agent))
        if chemin is None:
            print(f"Q-table : aucune sauvegarde avec ces récompenses et cette vision dans "
                  f"{agent.fichier_qtable}, l'IA part de zéro")
        else:
            nb_etats = charger_qtable(policy, chemin, environment.recompenses, _vision(agent))
            print(f"Q-table de la meilleure tentative : {nb_etats} états chargés depuis {chemin}")


def memoriser_fin_de_partie(agent, chemin_parties=None):
    """À appeler à la fin d'une partie de l'IA, avant d'écrire la ligne du CSV.

    Sauvegarde la Q-table (si elle est persistante) dans q-table/MxM/qtable_MxM_T<n>.json,
    n étant le numéro que la partie va recevoir dans le CSV.
    """
    if agent.fichier_qtable:
        environment = agent.environment
        tentative = derniere_tentative(chemin_parties or FICHIER_PARTIES) + 1
        chemin = fichier_qtable(environment.length, tentative, agent.fichier_qtable)
        os.makedirs(agent.fichier_qtable, exist_ok=True)
        sauvegarder_qtable(agent.learning_policy, chemin, environment.length, environment.recompenses,
                           _vision(agent))
        print(f"Q-table sauvegardée : {len(agent.learning_policy.qtable)} états dans {chemin}")


def nouvelle_partie(agent, optimiser=OPTIMISER_PARAMETRES, persistante=QTABLE_PERSISTANTE,
                    chemin_parties=None, rng=random, optimiser_recompenses=OPTIMISER_RECOMPENSES):
    """Prépare la partie suivante quand l'IA enchaîne plusieurs parties (NB_TOURS_MAX).

    À appeler après agent.reset() : les paramètres sont choisis à nouveau d'après le CSV,
    qui contient maintenant la partie qui vient de se terminer. Avec une Q-table persistante,
    elle est rechargée depuis le fichier sauvegardé en fin de partie ; sinon l'IA garde en
    mémoire ce qu'elle a appris depuis le lancement, tant que les récompenses ne changent pas
    (approche B : leurs valeurs n'auraient plus la même échelle).
    """
    policy = agent.learning_policy
    recompenses_avant = dict(agent.environment.recompenses)
    qtable_en_memoire = policy.qtable
    policy.qtable = {}
    preparer_agent(agent, optimiser, persistante, chemin_parties, rng, optimiser_recompenses)
    if not persistante:
        if agent.environment.recompenses == recompenses_avant:
            policy.qtable = qtable_en_memoire
        else:
            print("Récompenses changées : la Q-table en mémoire repart de zéro")
