"""Vision simplifiée de la grille pour l'IA (4e approche).

Au lieu de la grille exacte (qui ne se répète presque jamais d'une partie à l'autre),
l'IA voit quelques caractéristiques qui, elles, reviennent souvent :

- vides    : nombre de cases vides, par tranches (0-1, 2-3, 4-7, 8+)
- coin     : position de la plus grande tuile (un des 4 coins, un bord ou le centre)
- fusions  : fusions possibles en ligne (horizontal) et en colonne (vertical) : 0, 1 ou 2+
- ordre    : sens dans lequel les lignes et les colonnes sont rangées
             (croissant, décroissant ou mélangé) pour chaque axe

Exemple d'état : "v4-7|cHG|fh1|fv2+|oh>|ov~". Sur 30 parties au hasard (3 000 coups), on
rencontre environ 670 états simplifiés, contre 2 500 grilles exactes toutes différentes.
"""

TRANCHES_VIDES = ((1, "0-1"), (3, "2-3"), (7, "4-7"))


def _tranche_vides(nb_vides):
    for maximum, libelle in TRANCHES_VIDES:
        if nb_vides <= maximum:
            return libelle
    return "8+"


def _position_max(states, length):
    """Coin de la plus grande tuile : HG, HD, BG, BD (coins), B (bord) ou C (centre)."""
    x, y = max(states, key=lambda pos: (states[pos], -pos[0], -pos[1]))
    dernier = length - 1
    coins = {(0, 0): "HG", (dernier, 0): "HD", (0, dernier): "BG", (dernier, dernier): "BD"}
    if (x, y) in coins:
        return coins[(x, y)]
    if x in (0, dernier) or y in (0, dernier):
        return "B"
    return "C"


def _lignes(states, length):
    """Valeurs non nulles de chaque ligne (horizontal) et de chaque colonne (vertical)."""
    horizontal = [[states[(x, y)] for x in range(length) if states[(x, y)]] for y in range(length)]
    vertical = [[states[(x, y)] for y in range(length) if states[(x, y)]] for x in range(length)]
    return horizontal, vertical


def _fusions(lignes):
    """Nombre de paires de tuiles voisines égales (une fois les cases vides retirées) : 0, 1 ou 2+."""
    nombre = sum(1 for ligne in lignes for a, b in zip(ligne, ligne[1:]) if a == b)
    return str(min(nombre, 2)).replace("2", "2+")


def _ordre(lignes):
    """Sens de rangement dominant des lignes : < croissant, > décroissant, ~ sans sens dominant.

    On compte les lignes rangées dans chaque sens (une ligne de 0 ou 1 tuile ne compte pas).
    """
    croissantes = decroissantes = 0
    for ligne in lignes:
        paires = list(zip(ligne, ligne[1:]))
        if not paires:
            continue
        if all(a <= b for a, b in paires) and any(a < b for a, b in paires):
            croissantes += 1
        elif all(a >= b for a, b in paires) and any(a > b for a, b in paires):
            decroissantes += 1
    if croissantes > decroissantes:
        return "<"
    if decroissantes > croissantes:
        return ">"
    return "~"


def etat_simplifie(states, length):
    """Signature courte de la grille, utilisée comme clé de la Q-table."""
    if not states:
        return ""
    horizontal, vertical = _lignes(states, length)
    nb_vides = sum(1 for valeur in states.values() if valeur == 0)
    return (f"v{_tranche_vides(nb_vides)}|c{_position_max(states, length)}"
            f"|fh{_fusions(horizontal)}|fv{_fusions(vertical)}"
            f"|oh{_ordre(horizontal)}|ov{_ordre(vertical)}")
