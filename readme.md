# Installation
    pip install -r requirements.txt   # arcade 3.x

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

# Mémoire de l'IA entre les parties (mode apprentissage)
Variables d'environnement (fichier .env local, chargé avec `set -a; . ./.env; set +a`) :
- OPTIMISER_PARAMETRES (true par défaut) : learning_rate, discount_factor et les récompenses sont
  repris de la meilleure tentative du CSV (même taille de grille). Une fois sur 5, l'IA essaie des
  valeurs voisines et modifie une récompense (goal, gameover ou no_effect, x0.5 ou x2).
  Sans historique, ce sont les valeurs du .env.
- QTABLE_PERSISTANTE (true par défaut) : la Q-table est sauvegardée en fin de partie dans
  qtable_<taille>x<taille>_d<default>_g<goal>_o<gameover>_n<no_effect>.json (une Q-table par
  jeu de récompenses) et rechargée au lancement suivant.
- FICHIER_PARTIES_IA (parties_ia.csv) et FICHIER_QTABLE : chemins des fichiers, ignorés par git.
