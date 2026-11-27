# Installation
    pip install -r requirements.txt   # arcade 3.x, python-dotenv

# Pour Lancer le jeux
    python main_2048.py

# Tests
    python tests/smoke_logic.py
    python -m unittest discover -s tests

# Description
    main_2048.py: impl du jeux et adaption 3D
    agent.py: Management du deroulement du jeu et Gestionnaire de l"etat, des actions et des recompense et de l"IA.
    environnement.py & case_de_tableaux & game_methodes.py: Implementation de ka Gestion de l"etat, actons et récompense du jeu
    learning_policy.py: Gestionnaire de l'apprentissage par renforcement
    game_params.py: données fixes et paramettrable.
    historique.py: enregistrement des parties de l'IA dans parties_ia.csv
    memoire_ia.py: mémoire de l'IA entre les parties (paramètres choisis d'après le CSV, Q-table sauvegardée)
    :::
# Monitoring
Vous pouvez manipuler les valeurs suivantes dans le fichier game_params.py :
- GAME_LENGHT pour la taille du 2048, taille 3, 4 et 5 disponibles.
- DEFAULT_LEARNING_RATE
- DEFAULT_DISCOUNT_FACTOR
- GAME_SPEED: modification de la rapidité du jeux
- MODE_APPRENTISSAGE: pour jouer en manuel ou apprentisge

Ces valeurs se règlent aussi dans le fichier .env :
- GAME_LENGHT (4) : taille de la grille
- NB_TOURS_MAX (50) : en mode apprentissage, nombre de parties que l'IA enchaîne dans un même
  lancement (1 seconde de pause entre deux parties). Chaque partie est enregistrée dans le CSV
  (et la Q-table sauvegardée) avant la suivante, qui reprend les paramètres choisis d'après le CSV.
- DEFAULT_LEARNING_RATE (0.01) et DEFAULT_DISCOUNT_FACTOR (0.2) : paramètres de l'IA sans historique
- EXPLORATION (0.1) : part des coups que l'IA joue au hasard pour découvrir d'autres actions
  (0 = jamais, 1 = toujours). En cas d'égalité entre actions, l'IA tire au hasard parmi les meilleures.
- SIMU_INTERVAL_SPEED (0.01) : intervalle en secondes entre deux déplacements de l'IA

# Mémoire de l'IA entre les parties (mode apprentissage)
Variables d'environnement, à mettre dans un fichier .env à la racine du projet (chargé automatiquement
au lancement grâce à python-dotenv ; une variable définie dans le terminal reste prioritaire).
Valeurs oui/non acceptées : true, True, 1, oui, yes, vrai.
Exemple de .env :

    MODE_APPRENTISSAGE=true
    NB_TOURS_MAX=50
    OPTIMISER_PARAMETRES=true
    QTABLE_PERSISTANTE=true

- OPTIMISER_PARAMETRES (true par défaut) : learning_rate et discount_factor sont repris de la meilleure
  tentative du CSV (même taille de grille, mêmes récompenses), avec 1 essai de valeurs voisines sur 5.
  Les récompenses ne changent jamais : ce sont celles du .env.
- QTABLE_PERSISTANTE (true par défaut) : la Q-table est sauvegardée en fin de partie dans
  qtable_<taille>x<taille>.json et rechargée au lancement suivant.
- FICHIER_PARTIES_IA (parties_ia.csv) et FICHIER_QTABLE : chemins des fichiers, ignorés par git.

# 4e approche : vision simplifiée de la grille (branche dev-optimize4)
Avec la grille exacte, l'IA ne retombe presque jamais sur une situation déjà vue : sa Q-table ne
sert pas. Ici, l'IA voit un résumé de la grille (vision.py) qui se répète d'une partie à l'autre :
cases vides (0-1, 2-3, 4-7, 8+), position de la plus grande tuile (coin, bord, centre), fusions
possibles en ligne et en colonne (0, 1, 2+) et sens de rangement des lignes et des colonnes.
- VISION_SIMPLIFIEE (true par défaut) : false pour revenir à la grille exacte et comparer.
- La Q-table de la vision simplifiée est sauvegardée à part : qtable_<taille>x<taille>_simplifie.json.
- Le CSV indique la vision utilisée (colonne vision) ; les paramètres ne sont repris que de parties
  jouées avec la même vision.

