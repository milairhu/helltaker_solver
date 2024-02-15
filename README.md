# Solveur Helltaker

Projet final du cours **IA02 - Logique et Résolution de problèmes** par la recherche dispensé par M. Sylvain Lagrue à l'Université de Technologie de Compiègne (UTC).

Par Mohamed Adnane Errazine, Hugo Milair et Calliste Vergnol, en Printemps 2022.

Le répo orignal est disponible sur [GitLab](https://gitlab.utc.fr/milairhu/ia02-projet-helltaker). Ce répo ne contient que mon travail personnel. Il manque notamment un solveur utilisant A* réalisé en Python.

## Description de Helltaker

L’objectif de ce projet est de créer différentes « IA » capables de jouer à la partie puzzle du jeu [Helltaker](https://store.steampowered.com/app/1289310/Helltaker). Ce jeu, de la famille de Sokoban, est gratuit et disponible sous MacOS, Linux et Windows. Il introduit en plus de Sokoban des éléments sur la carte (pièges, clés, portes) et un nombre de coups maximal pour finir le niveau.

On implémente différentes méthodes, de les décrire et de les comparer expérimentalement dans un petit rapport final.

## Travail demandé

### Écriture du problème en STRIPS et en Prolog

"Vous devrez donner une représentation en STRIPS (ou l’un de ses dérivés) du problème. Mettre en exergue les principales différences avec Sokoban.

Bonus : reprendre le code Prolog de Sokoban vu en cours et l’adapter pour Helltaker."

### Implémentation

"Vous devrez implémenter 2 méthodes différentes parmi les 3 suivantes.

1) Recherche dans un espace d’état (Python)
2) SATPLAN (réécriture en SAT du problème de planification)
3) ASPPLAN (réécriture en ASP du problème de planification) "

Nous avons réalisé une implémentation de la première et troisième méthodes. La première n'est pas présente dans ce répo. Néanmoins, une version non fonctionnelle de la deuxième méthode est disponible dans le dossier [SAT](SAT). La version **ASP** est disponibledans le dossier [ASP](ASP). Une autre version utilisant le langage **Prolog** est disponible dans le dossier [Prolog](Prolog).

La sortie attende du programme sur la sortie standard est de type: *hhbgdbbgh*
Ceci correspond à une simplification des actions à réaliser pour réussir le labyrinthe (h = haut, b = bas, d = droite, g = gauche).

## Utilisation

### Grilles

Les solveurs résolvent des niveaux représentés en grilles dans des fichiers textes. Quelques exemples sont disponibles dans le dossier [grids](grids).

Une grille doit satisfaire les conditions suivantes:

- la *map* est entourée de **murs** représentés par des `#`
- le *point de départ* est représenté par un `H`
- un *bloc* pouvant être déplacé est représenté par un `B`. Le personnage peut les pousser.
- un *mob* est représenté par un `M`
- la *sortie* ou la *démone* est représentée par un `D`
- une *clé* est représentée par un `K`
- une *porte* est représentée par un `L`. Elle doit être ouverte par une clé
- un *trap* est représenté par un `T` ou un `U` si. Un trap enlève un coup possible au joueur. Il n'apparait qu'un tour sur deux.
- des pics sont représentés par des `P`. Ils enlèvent un coup possible au joueur.
  
### ASP et SAT

Après avoir installé les dépendances nécessaires, l'utilisateur peut lancer le solveur ASP ou SAT (ce dernier n'est pas fonctionnel) en utilisant la commande suivante:

 ```python
python3 ./ASP/ASP_helltaker.py <grille>
```

Où la grille peut être une grille du répo ou par une grille personnalisée.

### Prolog

Dans le dossier [Prolog](Prolog), l'utilisateur peut trouver le solveur d'un niveau Helltaker en Prolog. Pour le tester, il peut copier le code et le coller dans un interpréteur Prolog, par exemple celui de [SWICH.SWI-Prolog](https://swish.swi-prolog.org/).
