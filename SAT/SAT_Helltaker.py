"""
[IA02] Projet SAT/Helltaker python
author:  Hugo Milair
version: 1.0
"""
from typing import List, Tuple
import itertools
import pprint
import subprocess

Variable = int
Literal = int
Clause = List[Literal]
Model = List[Literal]
Clause_Base = List[Clause]
Grid = List[List[int]]


# Mettre des vraies grilles
empty_grid: Grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]

fluents= {'perso': (2, 2) ,'soldat': [(4, 4), (3, 4), (6, 5), (6, 1), (6, 4), (2, 3), (6, 3)],
      'piegePasFixeActive':[(1,1),(2,1)],'piegePasFixeAttente':[],'porte':(5,5),'block':[(1,2),(2,1)],'cle':(7,4)}  #fluents

chrono=32
largeur=10
hauteur=9
#constantes
map_constantes = {'sortie': [(7, 4), (2, 1)],'murs': [(4, 0),(5, 7),(8, 0)],'piegesFixe': []}


#Données dans Sudoku
def write_dimacs_file(dimacs: str, filename: str):  #écrit dans le DIMACS : write_dimacs_file(dimacsex1,"sudoku1.cnf")
    with open(filename, "w", newline="") as cnf:
        cnf.write(dimacs)

def exec_gophersat(  #execute gophersat) : modelex1=exec_gophersat("sudoku1.cnf","../gophersat")
    filename: str, cmd: str = "gophersat", encoding: str = "utf8"
) -> Tuple[bool, List[int]]:
    result = subprocess.run(
        [cmd, filename], capture_output=True, check=True, encoding=encoding
    )
    string = str(result.stdout)
    lines = string.splitlines()

    if lines[1] != "s SATISFIABLE":
        return False, []

    model = lines[2][2:].split(" ")

    return True, [int(x) for x in model]


#Faites dans Sudoku


"""Code des cellules :
 0 : Sortie 
 1 : Mur
 2 : Perso
 3 : Porte
 4 : Block
 5 : Soldat
 6 : PiegeFixe
 7 : PiegePasFixeActif
 8 : PiegePasFixeAttente
 9 : Clé
 
 cas bizarre : 
 10 : aCle : on va dire qu'il y en a un par coup et par case, alors que 1 par coup suffit?
 
Si différent de 0,1,6 (Sortie, Mur, PiegeFixe) : une seule variable propositionnelle
Sinon : 1 variable propositionnelle par coup possible (par nombre d'actions possibles affichées par le chrono en début de partie).

->NON on fait plutot une par coup quand même. On pourra chercher à optimiser plus tard

"""

## Cellules en var :
def cell_to_variable(i: int, j: int, val: int, nbCoupsCherche : int, nbCoupsInit : int, largeur:int) -> int: #verifier, mais me parait corrrect
    #les nb*4 premieres variables sont pour donner la direction choisie par coup : nbG, nbD, nbH, nbB
    res = 4*nbCoupsInit
    for a in range(0, i): #pour chaque ligne
        for b in range(0, largeur): #pour chaque colonne
            for z in range(0, 9+1+1): #pour chaque valeur possible (cf code)
                for c in range(0,nbCoupsInit+1):
                    res = res + 1
    # on est mtn à la bonne ligne
    for b in range(0, j):
        for z in range(0, 9+1+1):
            for c in range(0,nbCoupsInit+1):
                res = res + 1

    # on est bonne ligne + bonne colonne = bonne case
    for z in range(0, val):
        for c in range(0,nbCoupsInit+1):
            res = res + 1
    # on est maintenant à la bonne valeur de la case. On prend le numero de coup cherché correspondant
    for c in range(0,nbCoupsCherche+1):
        res=res+1

    return res

def variable_to_cell(var: int,largeur:int, hauteur:int, nbCoupsInit : int) -> Tuple[ int, int, int, int]: #(i,j,CodeCase,NbCoups)
    v=4*nbCoupsInit
    for i in range (0,hauteur):
        for j in range (0,largeur):
            for z in range (0,9+1+1):
                for c in range(0, nbCoupsInit + 1):
                    v=v+1
                    if (v==var):
                        return (i,j,z,c)
    return (-1,-1,-1,-1)
##################################################

##Actions en var
def action_to_variable(nbCoupsCherche : int,a : str )-> int:
    res=0

    for nb in range(1,nbCoupsCherche):
        res=res+4

    #on est au coup cherché
    if a=="H":
        res=res+1
    elif a=="D":
        res=res+2
    elif a=="B":
        res=res+3
    elif a=="G":
        res=res+4

    return res


def variable_to_action( var : int) -> Tuple[int,str] :

    nb=var//4 +1
    a=var-4*(nb-1)
    if a == 1 :
        return (nb,"H")
    elif a == 2 :
        return (nb,"D")
    elif a == 3 :
        return (nb,"B")
    elif a == 4 :
        return (nb,"G")
####################################################

i=action_to_variable(24,"H")
print(i)
j=variable_to_action(i)
print(j)
#################################################################################

##Créer contraintes et problème

def create_regles_constantes(largeur : int, hauteur:int, nbCoupsInit : int) -> List[List[int]]:
    liste = []

    ### Regles faciles

    #un mur reste un mur, une sortie reste une sortie, un piege fixe reste un piege fixe
    for i in range(0,hauteur):
        for j in range (0,largeur):
            for nb in range(1,nbCoupsInit+1): #attention au cas 0
                for type in [0,1,6]:
                    clause = []
                    clause.append(-1*(cell_to_variable(i, j, type, nb, nbCoupsInit, largeur)))
                    clause.append((cell_to_variable(i, j, type, nb-1, nbCoupsInit, largeur)))
                    liste.append(clause)


    #un piege pas fixe actif reste pas fixe actif si le perso est sur un tel piège lors de la continuité de dégat.
    #   Voir les actions de déplacement


    #un piege pas fixe actif devient un piege pas fixe en attente. : fais dans actions de deplacement
    #A MODIFIER /SUPPRIMER : FAIRE A CHAQUE FOIS DANS CONTINUITE
    #for i in range(0,hauteur):
    #    for j in range (0,largeur):
    #       for nb in range(1,nbCoupsInit+1): #attention au cas 0
    #            clause = []
    #            clause.append(-1*(cell_to_variable(i, j, 7, nb, nbCoupsInit, largeur)))
    #            clause.append((cell_to_variable(i, j, 8, nb-1, nbCoupsInit, largeur)))
    #            liste.append(clause)


    # un piege pas fixe en attente devient un piege pas fixe actif.
    # A MODIFIER /SUPPRIMER : FAIRE A CHAQUE FOIS DANS CONTINUITE
    #for i in range(0, hauteur):
    #    for j in range(0, largeur):
    #        for nb in range(1, nbCoupsInit + 1):  # attention au cas 0
    #            clause = []
    #            clause.append(-1 * (cell_to_variable(i, j, 8, nb, nbCoupsInit, largeur)))
    #            clause.append((cell_to_variable(i, j, 7, nb - 1, nbCoupsInit, largeur)))
    #            liste.append(clause)


    # un soldat sur un piege fixe meurt
    # A MODIFIER /SUPPRIMER : Plutot faire une action CasserSoldat : car ici, il se détruit un coup trop tard

    #for i in range(0, hauteur):
    #    for j in range(0, largeur):
    #        for nb in range(1, nbCoupsInit + 1):  # attention au cas 0
    #            clause = []
    #            clause.append(-1 * (cell_to_variable(i, j, 5, nb, nbCoupsInit, largeur)))
    #            clause.append(-1 * (cell_to_variable(i, j, 6, nb, nbCoupsInit, largeur)))
    #            clause.append((cell_to_variable(i, j, 5, nb - 1, nbCoupsInit, largeur)))
    #            liste.append(clause)


    # un soldat sur un piege en attente meurt le coup apres
    for i in range(0, hauteur):
        for j in range(0, largeur):
            for nb in range(1, nbCoupsInit + 1):  # attention au cas 0
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 5, nb, nbCoupsInit, largeur)))
                clause.append(-1 * (cell_to_variable(i, j, 8, nb, nbCoupsInit, largeur)))
                clause.append((cell_to_variable(i, j, 5, nb - 1, nbCoupsInit, largeur)))
                liste.append(clause)

    #etre sur piegeFixe fait perdre un tour : risque de s'enfermer est perdre toute sa vie?
#  for  i in range (0,hauteur):
#       for j in range (0,largeur):
            #for nbCoup in range (1, nbCoupsInit+1):
                #for type in range(0,10):
                    #clause=[]
                    #clause.append(-1*cell_to_variable(i,j,2,nbCoup,nbCoupsInit,largeur)) #non perso est sur position la case
                    # clause.append(-1*cell_to_variable(i,j,6,nbCoup,nbCoupsInit,largeur)) #ou non piege actif sur la meme case
                    #clause.append()

    return liste

#Unique et at_least ont l'ai bon!
def at_leat_one_action(nbActionsInit : int) -> List[List[int]] :

    liste=[]
    actions=["H","D","B","G"]
    for coups in range(1,nbActionsInit+1):
        clause=[]
        for a in actions :
            clause.append(action_to_variable(coups,a))
        liste.append(clause)

    return liste

def unique_action(nbActionsInit : int) -> List[List[int]] :
    liste = []
    actions = ["H", "D", "B", "G"]



    for nb in range(1,nbActionsInit+1):
        vars=range(1+(nb-1)*4,1+nb*4) #ensemble de nos variables actions pour le coup nb
        for i in itertools.combinations(vars, 2):
            l = []
            l.append(-1 * i[0])
            l.append(-1 * i[1])
            liste.append(l)
        return liste
#print(at_leat_one_action(2))
#print(unique_action(2))
########################################


#######Regles mouvement

def regles_mouvD(largeur : int, hauteur:int, nbCoupsInit : int) -> List[List[int]]:
    liste = []
    #MouvD sans Piege :

    for i in range(1, hauteur-1): #car premiere et derniere lignes sont que des murs
        for j in range(1, largeur-1): #car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1*action_to_variable(nb,"D")) #si on fait l'action d'aller à droite au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # et perso en i,j
                clause.append( (cell_to_variable(i, j+1, 4, nb, nbCoupsInit, largeur))) #et non block en i+j
                clause.append((cell_to_variable(i, j + 1, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append( (cell_to_variable(i, j + 1, 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append( (cell_to_variable(i, j + 1, 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append( (cell_to_variable(i, j + 1, 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i+j
                clause.append( (cell_to_variable(i, j + 1, 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                                                  #IMPLIQUE


                clauseNvPosPerso=clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j + 1, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso) #Clause qui donne la position du perso


                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip==i and jp==j+1):
                            clauseInterditPosPerso=clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb-1, nbCoupsInit, largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                #Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3,4,5,9,10]:
                    for ip in range(1,hauteur-1):
                        for jp in range(1,largeur-1):

                            #A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))  # nouvelle situation

                            else :
                                for sens in [1,-1]: #car continuité est une équivalence. ...=>(nbPortei,j<=>(nb-1)Portei,j)
                                    #Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    #Qu'on specialise par case et type


                                    clauseSpecialise.append(-1 * sens * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                                    if type == 7:  # cas  des pieges en attente qui deviennent actifs
                                        clauseSpecialise.append(1 *sens*(cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,largeur)))  # devient un piege actif

                                    elif type==8 : #cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 *sens *(cell_to_variable(ip, jp, 7, nb-1, nbCoupsInit, largeur))) #devient un piege en attente

                                    else:
                                         clauseSpecialise.append(1*sens* (cell_to_variable(ip, jp, type, nb-1, nbCoupsInit, largeur))) #nouvelle situation
                
                            liste.append(clauseSpecialise)



    ##MouvD avec piegeFixe
    #C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2


    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i, j + 1, 4, nb, nbCoupsInit, largeur)))  # et non block en i+j
                clause.append((cell_to_variable(i, j + 1, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i, j + 1, 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append((cell_to_variable(i, j + 1, 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append(-1*(cell_to_variable(i, j + 1, 6, nb, nbCoupsInit, largeur)))  # et piege actif fixe en i+j
                clause.append((cell_to_variable(i, j + 1, 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                                            #IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j + 1, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j + 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                    # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7,8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type==5 : #cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append( (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur))) #si pas de piege fixe
                                clauseSpecialise.append( (cell_to_variable(ip, jp, 8, nb, nbCoupsInit, largeur))) #et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit, largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit, largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                #Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]: #les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                     for jp in range(1, largeur - 1):
                        # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                        clauseSpecialise = clause.copy()
                        # Qu'on specialise par case et type
                        clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb-1, nbCoupsInit, largeur)))
                        if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                            clauseSpecialise.append(
                                (cell_to_variable(ip, jp, 6, nb-1, nbCoupsInit, largeur)))  # si pas de piege fixe
                            clauseSpecialise.append(
                                (cell_to_variable(ip, jp, 8, nb-1, nbCoupsInit, largeur)))  # et pas de piège en attente

                        clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit, largeur)))  # nouvelle situation, on a perdu un coup

                        liste.append(clauseSpecialise)



    #MouvD avec piegeAttente a côté
    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i, j + 1, 4, nb, nbCoupsInit, largeur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i, j + 1, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i, j + 1, 1, nb, nbCoupsInit, largeur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i, j + 1, 3, nb, nbCoupsInit, largeur)))  # et non porte en i,j+1
                clause.append( (cell_to_variable(i, j + 1, 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i,j+1
                clause.append(-1*(cell_to_variable(i, j + 1, 8, nb, nbCoupsInit, largeur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j + 1, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j + 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit, largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

            # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit, largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit, largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit, largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit, largeur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit, largeur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)


    return liste


def regles_mouvG(largeur: int, hauteur: int, nbCoupsInit: int) -> List[List[int]]:
    liste = []
    # MouvG sans Piege :
    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * action_to_variable(nb, "G"))  # si on fait l'action d'aller à gauche au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # et perso en i,j
                clause.append((cell_to_variable(i, j - 1, 4, nb, nbCoupsInit, largeur)))  # et non block en i+j
                clause.append((cell_to_variable(i, j - 1, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i, j - 1, 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append((cell_to_variable(i, j - 1, 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append(
                    (cell_to_variable(i, j - 1, 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i, j - 1, 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j - 1, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j - 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui deviennent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

    ##MouvD avec piegeFixe
    # C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2

    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i, j - 1, 4, nb, nbCoupsInit, largeur)))  # et non block en i+j
                clause.append((cell_to_variable(i, j - 1, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i, j - 1, 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append((cell_to_variable(i, j - 1, 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append(
                    -1 * (cell_to_variable(i, j - 1, 6, nb, nbCoupsInit, largeur)))  # et piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i, j - 1, 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j - 1, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j - 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                    # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                      largeur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    # MouvD avec piegeAttente a côté


    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i, j - 1, 4, nb, nbCoupsInit, largeur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i, j - 1, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i, j - 1, 1, nb, nbCoupsInit, largeur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i, j - 1, 3, nb, nbCoupsInit, largeur)))  # et non porte en i,j+1
                clause.append(
                    (cell_to_variable(i, j - 1, 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i,j+1
                clause.append(
                    -1 * (cell_to_variable(i, j- 1, 8, nb, nbCoupsInit, largeur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j - 1, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j - 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (
                                cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    return liste


def regles_mouvH(largeur: int, hauteur: int, nbCoupsInit: int) -> List[List[int]]:
    liste = []


    # MouvH sans Piege :
    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * action_to_variable(nb, "H"))  # si on fait l'action d'aller en haut au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # et perso en i,j
                clause.append((cell_to_variable(i-1, j, 4, nb, nbCoupsInit, largeur)))  # et non block en i+j
                clause.append((cell_to_variable(i- 1, j , 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i- 1, j , 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append((cell_to_variable(i- 1, j , 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append(
                    (cell_to_variable(i- 1, j , 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i- 1, j , 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i- 1, j , 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i - 1and jp == j ):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui deviennent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

    ##MouvD avec piegeFixe
    # C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2

    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i- 1, j , 4, nb, nbCoupsInit, largeur)))  # et non block en i+j
                clause.append((cell_to_variable(i- 1, j , 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i- 1, j , 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append((cell_to_variable(i - 1, j, 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append(
                    -1 * (cell_to_variable(i - 1, j, 6, nb, nbCoupsInit, largeur)))  # et piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i - 1, j, 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i- 1, j , 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i - 1 and jp == j ):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                    # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                      largeur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    # MouvD avec piegeAttente a côté

    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i- 1, j , 4, nb, nbCoupsInit, largeur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i- 1, j , 5, nb, nbCoupsInit, largeur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i - 1, j, 1, nb, nbCoupsInit, largeur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i - 1, j, 3, nb, nbCoupsInit, largeur)))  # et non porte en i,j+1
                clause.append(
                    (cell_to_variable(i - 1, j, 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i,j+1
                clause.append(
                    -1 * (cell_to_variable(i - 1, j, 8, nb, nbCoupsInit, largeur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i - 1, j, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i - 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (
                                cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    return liste


def regles_mouvB(largeur: int, hauteur: int, nbCoupsInit: int) -> List[List[int]]:
    liste = []

    # MouvH sans Piege :
    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * action_to_variable(nb, "B"))  # si on fait l'action d'aller en bas au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i + 1, j, 4, nb, nbCoupsInit, largeur)))  # et non block en i+j
                clause.append((cell_to_variable(i + 1, j, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i + 1, j, 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append((cell_to_variable(i + 1, j, 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append(
                    (cell_to_variable(i + 1, j, 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i + 1, j, 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i + 1, j, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i + 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui deviennent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

    ##MouvD avec piegeFixe
    # C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2

    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i + 1, j, 4, nb, nbCoupsInit, largeur)))  # et non block en i+j
                clause.append((cell_to_variable(i + 1, j, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i + 1, j, 1, nb, nbCoupsInit, largeur)))  # et non mur en i+j
                clause.append((cell_to_variable(i + 1, j, 3, nb, nbCoupsInit, largeur)))  # et non porte en i+j
                clause.append(
                    -1 * (cell_to_variable(i + 1, j, 6, nb, nbCoupsInit, largeur)))  # et piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i + 1, j, 8, nb, nbCoupsInit, largeur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i + 1, j, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i + 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                    # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                      largeur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    # MouvD avec piegeAttente a côté

    for i in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
        for j in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur)))  # perso en i,j
                clause.append((cell_to_variable(i + 1, j, 4, nb, nbCoupsInit, largeur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i + 1, j, 5, nb, nbCoupsInit, largeur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i + 1, j, 1, nb, nbCoupsInit, largeur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i + 1, j, 3, nb, nbCoupsInit, largeur)))  # et non porte en i,j+1
                clause.append(
                    (cell_to_variable(i + 1, j, 6, nb, nbCoupsInit, largeur)))  # et non piege actif fixe en i,j+1
                clause.append(
                    -1 * (cell_to_variable(i + 1, j, 8, nb, nbCoupsInit, largeur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i + 1, j, 2, nb - 1, nbCoupsInit, largeur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(1, hauteur - 1):  # car premiere et derniere lignes sont que des murs
                    for jp in range(1, largeur - 1):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i + 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (
                                cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(1, hauteur - 1):
                        for jp in range(1, largeur - 1):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur)))

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    return liste


######################### TEST ##############""
l=regles_mouvD(3,3,1)
print(l)
for clause in l :
    print("(",end="")
    for var in clause :
        if var<0:
            print(" -",end="")
        if abs(var)<4* 1 :
            print(variable_to_action(abs(var)))
        else:
            print((variable_to_cell(abs(var),3,3,1)))
        print(" ,",end="")
    print("), ")


##############################################




def clauses_to_dimacs(clauses: List[List[int]], nb_vars: int) -> str:
    res = ""
    res = res + "c Projet IA02\n"
    res = res + "c Helltaker\nc\n"
    res = res + "p cnf " + str(nb_vars) + " " + str(len(clauses)) + "\n"

    for clause in clauses:

        for i in clause:
            res = res + str(i) + " "
        res = res + "0 \n"

    return res

