# IA02 Projet Helltaker : https://hackmd.io/@ia02/BJ6eDYUI5

## Description
L’objectif de ce projet est de créer différentes « IA » capables de jouer à la partie puzzle du jeu Helltaker. Ce jeu, de la famille de Sokoban, est gratuit et disponible sous MacOS, Linux et Windows. L’objectif est d’implémenter différentes méthodes, de les décrire et de les comparer expérimentalement dans un petit rapport final.

## Travail demandé

### Écriture du problème en STRIPS et en Prolog

Vous devrez donner une représentation en STRIPS (ou l’un de ses dérivés) du problème. Mettre en exergue les principales différences avec Sokoban.

Bonus : reprendre le code Prolog de Sokoban vu en cours et l’adapter pour Helltaker.

### Implémentation

Vous devrez implémenter 2 méthodes différentes parmi les 3 suivantes.

1) Recherche dans un espace d’état (Python)
2) SATPLAN (réécriture en SAT du problème de planification)
3) ASPPLAN (réécriture en ASP du problème de planification)

### Rapport

Le rapport, de 10 pages maximum, suivra le plan suivant. Vous pouvez néanmoins l’enrichir à votre guise.

Introduction
Préliminaires
    Présentation des règles du jeu
    Le problème en STRIPS
Méthode 1
    Représentation du problème
    Choix d’implémentation et structures de données
    Expérimentations pratiques
Méthode 2
    Représentation du problème
    Choix d’implémentation et structures de données
    Expérimentations pratiques
Comparaison expérimentale des 2 méthodes

### Rendu attendu

- 1 programme Prolog de modélisation
- 2 programmes implémentant les méthodes choisies et respectant les formats d’entrée/sortie imposés
- 1 rapport
*Date limite de rendu (code + rapport) : mercredi 15 juin (23h59)*

Vos programmes seront testés de façon automatique sur une machine dédiée. Les fichiers seront automatiquement donnés à votre programme et le plan généré sera testé. L’outil de lecture de fichiers et la fonction main de votre programme vous seront donnés en python.

Réponse attendue du programme sur la sortie standard (fin de ligne \n) : hhbgdbbgh
Ceci correspond à une simplification des actions (h = haut, b = bas, d = droite, g = gauche)

### Évaluation

Les points suivants seront pris en compte pour l’évaluation :

- Solutions choisies et élégance de celles-ci
- Qualité du code et utilisation des outils dédiés (black, mypy, pylint, etc.)
- Efficacité du code (les programmes seront lancés automatiquement sur une machine dédiée)

## Ressources 
### Nos liens utiles

Path finding avec A* : https://qiao.github.io/PathFinding.js/visual/?fbclid=IwAR3vkBO_nDFXb86Goq_GLt2m1WqAEZwjeUCo3qioAqWGhqhaQ7ASPBZjlHk
où best first seach = glouton et breadth-first-seach = recherche par largeur

### Quelques liens

Helltaker sur wikipedia : https://fr.wikipedia.org/wiki/Helltaker
Helltaker sur steam: https://store.steampowered.com/app/1289310/Helltaker/
Télécharger Helltaker sur le site du développeur sans avoir à installer steam : https://vanripper.itch.io/helltaker
Helltaker sur fandom : https://helltaker.fandom.com/wiki/Helltaker_Wiki
Description SATPLAN : https://en.wikipedia.org/wiki/Satplan
Description ASPPLAN : tba

### Code fourni tba
