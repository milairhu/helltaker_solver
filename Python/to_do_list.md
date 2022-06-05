# TODOs pour la partie python

## Partie Modélisation
### TODO
- ajouterDemoness to wall en s0
- ajouter toutes les actions possibles effectuables comme push, move, ...
    - move 4 directions
    - pushSoldat vers case vide 4 directions
    - pushSoldat vers spikes 4 directions
    - pushSoldat vers trapSafe 4 directions
    - pushSoldat vers trapUnsafe 4 directions
    - pushSoldat vers block 4 directions
    - casserSoldat contre mur (quand contre mur (et block? et soldat? et porte? A TRANCHER : a priori se casse partout))
    - casserSoldat contre block
    - casserSoldat contre soldat
    - casserSoldat contre lock
    - obtenir clé
    - Ouvrir une Porte avec la clé 
    - Taper le Block (le block ne bouge pas, le perso non plus, on a juste utilisé un coup pour perdre du temps : si bloc,mur ou soldat derrière) = PushBlockContreBlockB
    - Taper le Block vers soldat = PushBlockContreSoldatD
    - PushBlockContreMurD
    - PushBlockContrePorteD
    - De plus, le cas où un soldat se trouve sur un piege désactivé et meurt au prochain mouvement du joueur car le piège se réactive



### Done 
- déterminer les fluents/prédicats.

-  Fonction d'automatisation des entrées de carte : intialiser les valeurs s0 et map_rules. (plus précisement d'avoir des frozenset dans map_rules, s0 toute en gardant le type state pour s0 et le type Predicat pour map_rules.)

- ajouter des free pour chaque fluents/prédicats

## Partie Algorithme de recherche
Il reste tout ou presque à faire...
