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

# Mémoire de l'IA entre les parties (mode apprentissage)
Variables d'environnement, à mettre dans un fichier .env à la racine du projet (chargé automatiquement
au lancement grâce à python-dotenv ; une variable définie dans le terminal reste prioritaire).
Valeurs oui/non acceptées : true, True, 1, oui, yes, vrai.
Exemple de .env :

    MODE_APPRENTISSAGE=true
    OPTIMISER_PARAMETRES=true
    QTABLE_PERSISTANTE=true

- OPTIMISER_PARAMETRES (true par défaut) : learning_rate et discount_factor sont repris de la meilleure
  tentative du CSV (même taille de grille, mêmes récompenses), avec 1 essai de valeurs voisines sur 5.
  Les récompenses ne changent jamais : ce sont celles du .env.
- QTABLE_PERSISTANTE (true par défaut) : la Q-table est sauvegardée en fin de partie dans
  qtable_<taille>x<taille>.json et rechargée au lancement suivant.
- FICHIER_PARTIES_IA (parties_ia.csv) et FICHIER_QTABLE : chemins des fichiers, ignorés par git.
