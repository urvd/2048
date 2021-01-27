#librairie requis: (pip install)
    scikit-neuralnetwork-0.7
    numpy
    arcade
# Pour Lancer le jeux
Executer main.py pour lancer le jeux
# Description
    main_2048.py: impl du jeux et adaption 3D
    agent.py: Management du deroulement du jeu et Gestionnaire de l"etat, des actions et des recompense et de l"IA.
    environnement.py & case_de_tableaux & game_methodes.py: Implementation de ka Gestion de l"etat, actons et récompense du jeu
    learning_policy.py: Gestionnaire de l'apprentissage par renforcement
    game_params.py: données fixes et paramettrable.
    :::
# Monitoring
Vous pouvez manipuler les valeurs suivantes dans le fichier game_params.py :
- GAME_LENGHT pour la taille du 2048, taille 3, 4 et 5 disponibles.
- DEFAULT_LEARNING_RATE
- DEFAULT_DISCOUNT_FACTOR
- GAME_SPEED: modification de la rapidité du jeux
- MODE_APPRENTISSAGE: pour jouer en manuel ou apprentisge