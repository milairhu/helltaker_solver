# TODOs pour la partie python

## Partie Modélisation
### TODO
- rédaction rapport en prenant en considération le temps d'execution de chaque niveau dans la partie statistique
* factory pas obligatoire mais je pense que le prof peut insister sur ce point(l'élégance et la pertinance du code)
- factory(patron de conception) pour is_free_xxx
- de meme pour map_rules
- de meme pour goals(pas necessaire je crois) 
###




- ajouterDemoness to wall en s0
- ajouter toutes les actions possibles effectuables comme push, move, ...
    
    
    - Taper le Block (le block ne bouge pas, le perso non plus, on a juste utilisé un coup pour perdre du temps : si bloc,mur ou soldat derrière) = PushBlockContreBlockB
    - Taper le Block vers soldat = PushBlockContreSoldatD
    - PushBlockContreMurD
    - PushBlockContrePorteD



### Done 
- déterminer les fluents/prédicats.

-  Fonction d'automatisation des entrées de carte : intialiser les valeurs s0 et map_rules. (plus précisement d'avoir des frozenset dans map_rules, s0 toute en gardant le type state pour s0 et le type Predicat pour map_rules.)

- ajouter des free pour chaque fluents/prédicats

- move hero 4 directions
- pushSoldat vers case vide 4 directions 

- casserSoldat contre block
- casserSoldat contre soldat
- casserSoldat contre lock
- casserSoldat vers spikes
- casserSoldat vers trapSafe
- casserSoldat vers trapUnsafe

- obtenir clé
- Ouvrir une Porte avec la clé 

- De plus, le cas où un soldat se trouve sur un piege désactivé et meurt au prochain mouvement du joueur car le piège se réactive

## Partie Algorithme de recherche
Il reste tout ou presque à faire...