#!/usr/bin/env python3
"""Nettoyage des Q-tables sauvegardées : garde les meilleures, supprime les autres.

Dans chaque dossier q-table/MxM/, seules les MAX_KEEP_BEST_QTABLES meilleures Q-tables
(qtable_MxM_Tn.json) sont gardées. Une Q-table est classée d'après la ligne de sa tentative
dans le CSV des parties :
  1. la plus grande tuile atteinte,
  2. le nombre de cases à cette valeur,
  3. le score total.
Une Q-table dont la tentative n'est pas dans le CSV est classée en dernier.

Avec RECHARGER_QTABLE=recente, la Q-table la plus récente de chaque combinaison de récompenses
et de vision est aussi gardée : c'est elle que le jeu recharge, l'apprentissage en cours n'est
donc jamais perdu.

Utilisation :
    python clean_qtables.py                 # toutes les tailles (3x3, 4x4, 5x5)
    python clean_qtables.py --taille 4      # seulement q-table/4x4
    python clean_qtables.py --garder 5      # garder 5 Q-tables au lieu de MAX_KEEP_BEST_QTABLES
    python clean_qtables.py --simulation    # afficher ce qui serait supprimé, sans rien supprimer

Le jeu l'appelle aussi automatiquement à la fin de chaque série de parties de l'IA
(NETTOYAGE_AUTO=true dans le .env).
"""
import argparse
import os

from game_params import MAX_KEEP_BEST_QTABLES, RECHARGER_QTABLE, TAILLES_POSSIBLES
from historique import FICHIER_PARTIES, lire_parties
from memoire_ia import classer_qtables, dossier_qtable, lire_contexte, qtables_sauvegardees


def _plus_recentes_par_contexte(taille, dossier):
    """Q-table la plus récente de chaque combinaison (récompenses, vision)."""
    vues, gardees = set(), set()
    for chemin in qtables_sauvegardees(taille, dossier):
        contexte = repr(lire_contexte(chemin))
        if contexte not in vues:
            vues.add(contexte)
            gardees.add(chemin)
    return gardees


def nettoyer(taille, garder=MAX_KEEP_BEST_QTABLES, parties=None, dossier=None, simulation=False,
             recharger=RECHARGER_QTABLE):
    """Garde les `garder` meilleures Q-tables d'une taille de grille (et, en mode recente,
    la plus récente de chaque combinaison récompenses/vision). Renvoie les fichiers supprimés."""
    dossier = dossier or dossier_qtable(taille)
    if not os.path.isdir(dossier):
        return []
    parties = lire_parties(FICHIER_PARTIES) if parties is None else parties
    proteges = _plus_recentes_par_contexte(taille, dossier) if recharger == "recente" else set()
    a_supprimer = [c for c in classer_qtables(taille, parties, dossier)[max(1, garder):] if c not in proteges]
    # fichiers temporaires laissés par un jeu coupé pendant une sauvegarde
    a_supprimer += [os.path.join(dossier, nom) for nom in os.listdir(dossier) if nom.endswith(".json.tmp")]
    if not simulation:
        for chemin in a_supprimer:
            os.remove(chemin)
    return a_supprimer


def main():
    parser = argparse.ArgumentParser(description="Garde les meilleures Q-tables de q-table/MxM/.")
    parser.add_argument("--taille", type=int, choices=TAILLES_POSSIBLES,
                        help="taille de grille à nettoyer (par défaut : toutes)")
    parser.add_argument("--garder", type=int, default=MAX_KEEP_BEST_QTABLES,
                        help=f"nombre de Q-tables gardées par taille (défaut : {MAX_KEEP_BEST_QTABLES})")
    parser.add_argument("--simulation", action="store_true",
                        help="afficher ce qui serait supprimé, sans rien supprimer")
    args = parser.parse_args()

    parties = lire_parties(FICHIER_PARTIES)
    for taille in ([args.taille] if args.taille else TAILLES_POSSIBLES):
        dossier = dossier_qtable(taille)
        if not os.path.isdir(dossier):
            continue
        supprimes = nettoyer(taille, args.garder, parties, dossier, args.simulation)
        verbe = "serait supprimé" if args.simulation else "supprimé"
        for chemin in supprimes:
            print(f"{verbe} : {chemin}")
        restants = len([n for n in os.listdir(dossier) if n.endswith(".json")])
        if args.simulation:
            restants -= len([c for c in supprimes if c.endswith(".json")])
        print(f"{dossier} : {len(supprimes)} fichier(s) {verbe}(s), {restants} Q-table(s) gardée(s)")


if __name__ == "__main__":
    main()
