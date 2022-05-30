"""
[IA02] Projet SAT/Helltaker python
author:  Hugo Milair
version: 1.0
"""
from typing import List, Tuple
import itertools
import subprocess
import sys
from helltaker_utils import grid_from_file, check_plan

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
#constantes
map_constantes = {'sortie': [(7, 4), (2, 1)],'murs': [(4, 0),(5, 7),(8, 0)],'piegesFixe': []}


######################################## INITIALISATION ################################

infosGrille=grid_from_file(sys.argv[1])

nb_vars=infosGrille["max_steps"]*10*infosGrille["n"]*infosGrille["m"]+infosGrille["max_steps"]*4 #chrono * nb variable par case * largeur * hauteur + chrono*mouvementpossibles
listeClauses=[]


########################## STRUCTURE PROGRAMME #######"

    #1) Lire fichier avec grid_from_file. On aura toutes les données (largeur, hauteur, chrono, carte)
    #2) A partir de la grille, on génère les fait de de base.
    #3) On génère toutes les règles indépendamment de la grille. On les met dans une liste
    #4) On ecrit le DIMACS et on exécute avec gophersat (//Sudoku)
    #5) Du retour, on prend les mouvement pour chaque chrono. On en fait une chaine de caractère "HGBD"
    #6) On teste la chaine avec check_plan


    # VARIABLES :
    # de 1 à chrono*4 : variables de mouvement : on se base là dessus pour avoir le plan à la fin
    # de chrono*4+1 à chrono*10*largeur*hauteur+chrono*4  : variables pour les etats des cases


######################################################################################################

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



#Faite dans Sudoku
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

## Cellules en var : renvoie 0 si erreur
def cell_to_variable(i: int, j: int, val: int, nbCoupsCherche : int, nbCoupsInit : int, largeur:int, hauteur : int) -> int: #verifier, mais me parait corrrect
    #les nb*4 premieres variables sont pour donner la direction choisie par coup : nbG, nbD, nbH, nbB

    if i<0 or j<0 or j>=largeur or i>=hauteur :
        return 0

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
"""
i=action_to_variable(24,"H")
print(i)
j=variable_to_action(i)
print(j)
"""
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
                    clause.append(-1*(cell_to_variable(i, j, type, nb, nbCoupsInit, largeur,hauteur)))
                    clause.append((cell_to_variable(i, j, type, nb-1, nbCoupsInit, largeur,hauteur)))
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
                clause.append(-1 * (cell_to_variable(i, j, 5, nb, nbCoupsInit, largeur,hauteur)))
                clause.append(-1 * (cell_to_variable(i, j, 8, nb, nbCoupsInit, largeur,hauteur)))
                clause.append((cell_to_variable(i, j, 5, nb - 1, nbCoupsInit, largeur,hauteur)))
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

def create_fait_bonneFin() -> List[List[int]] : #ATTENTION : cette création dépend de la grille de départ
    global infosGrille
    largeur=infosGrille["n"]
    hauteur=infosGrille["m"]
    nbCoupsInit=infosGrille["max_steps"]

    posSorties=[]

    clauseDisjonctionPosPerso=[]
    liste=[]

    #on trouve la démonne ou les demonnes (cf niveau3)

    for i in range(0,hauteur):
        for j in range(0,largeur):
            if infosGrille["grid"] == "D":
                voisins = [(i- 1, j), (i+ 1, j), (i, j + 1), (i, j - 1)]
                for v in voisins:
                    if(v[0]>=0 and v[0]<hauteur and v[1]>=0 and v[1]<largeur): #si voisin est dans grille

                        if infosGrille["grid"][v[0]][v[1]]!= "#" and infosGrille["grid"][v[0]][v[1]]!= "D" : #si ce n'est pas un mur ou une autre demonne (il est possible d'aller dessus:

                            posSorties.append((v[0],v[1]))
                                #couplesPosSortiesPosPerso.append((cell_to_variable(i,j,0,coup,nbCoupsInit,largeur,hauteur),(cell_to_variable(i,j,2,coup,nbCoupsInit,largeur,hauteur))) )

    for coup in range(0,nbCoupsInit+1) :
        for pos in posSorties:
            clauseDisjonctionPosPerso.append(cell_to_variable(pos[0],pos[1],2,coup,nbCoupsInit,largeur,hauteur))

    liste.append(clauseDisjonctionPosPerso)
    return liste







######################## REGLES ############################################################


#######Regles mouvement
####### ATTENTION : EN FAIT LES LIGNES EXTERIEURES SONT PAS FORCEMENT QUE DES MURS
def regles_mouvD(largeur : int, hauteur:int, nbCoupsInit : int) -> List[List[int]]:
    liste = []
    #MouvD sans Piege :

    for i in range(0, hauteur): #car premiere et derniere lignes sont que des murs
        for j in range(0, largeur): #car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1*action_to_variable(nb,"D")) #si on fait l'action d'aller à droite au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # et perso en i,j
                clause.append( (cell_to_variable(i, j+1, 4, nb, nbCoupsInit, largeur,hauteur))) #et non block en i+j
                clause.append((cell_to_variable(i, j + 1, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append( (cell_to_variable(i, j + 1, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append( (cell_to_variable(i, j + 1, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append( (cell_to_variable(i, j + 1, 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i+j
                clause.append( (cell_to_variable(i, j + 1, 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                                                  #IMPLIQUE


                clauseNvPosPerso=clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j + 1, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso) #Clause qui donne la position du perso


                for ip in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
                        if not (ip==i and jp==j+1):
                            clauseInterditPosPerso=clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb-1, nbCoupsInit, largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                #Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3,4,5,9,10]:
                    for ip in range(0,hauteur):
                        for jp in range(0,largeur):


                            #A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(-1*(cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(-1*(cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                #Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(-1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit, largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)



                            else :
                                for sens in [1,-1]: #car continuité est une équivalence. ...=>(nbPortei,j<=>(nb-1)Portei,j)

                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    #Qu'on specialise par case et type


                                    clauseSpecialise.append(-1 * sens * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente

                                    if type == 7:  # cas  des pieges en attente qui deviennent actifs
                                        clauseSpecialise.append(1 *sens*(cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,largeur,hauteur)))  # devient un piege actif

                                    elif type==8 : #cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 *sens *(cell_to_variable(ip, jp, 7, nb-1, nbCoupsInit, largeur,hauteur))) #devient un piege en attente

                                    else:
                                         clauseSpecialise.append(1*sens* (cell_to_variable(ip, jp, type, nb-1, nbCoupsInit, largeur,hauteur))) #nouvelle situation

                                    liste.append(clauseSpecialise)



    ##MouvD avec piegeFixe
    #C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2


    for i in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i, j + 1, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i+j
                clause.append((cell_to_variable(i, j + 1, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i, j + 1, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append((cell_to_variable(i, j + 1, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append(-1*(cell_to_variable(i, j + 1, 6, nb, nbCoupsInit, largeur,hauteur)))  # et piege actif fixe en i+j
                clause.append((cell_to_variable(i, j + 1, 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                                            #IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j + 1, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j + 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                    # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7,8, 9, 10]:
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur):



                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit, largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)

                            else:
                                for sens in [-1,1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type
                                    clauseSpecialise.append(-1 *sens* (cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                    if type == 7:  # cas  des pieges en attente qui passent actifs
                                        clauseSpecialise.append(1*sens*(cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit, largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1*sens *(cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit, largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(1*sens * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

                #Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]: #les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur):
                     for jp in range(0, largeur):

                        # A PART car l'équivalence est pas vrai?
                        if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()
                            clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, type, nb-1, nbCoupsInit, largeur,hauteur)))  # situation précédente
                            clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb-1, nbCoupsInit, largeur,hauteur)))  # si pas de piege fixe
                            clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb-1, nbCoupsInit, largeur,hauteur)))  # et pas de piège en attente
                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit, largeur,hauteur)))  # nouvelle situation
                            liste.append(clauseSpecialise)



                        else:
                            for sens in [-1,1]:
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 *sens* (cell_to_variable(ip, jp, type, nb-1, nbCoupsInit, largeur,hauteur)))
                                clauseSpecialise.append(1*sens*(cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit, largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                                liste.append(clauseSpecialise)



    #MouvD avec piegeAttente a côté
    for i in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i, j + 1, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i, j + 1, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i, j + 1, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i, j + 1, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i,j+1
                clause.append( (cell_to_variable(i, j + 1, 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i,j+1
                clause.append(-1*(cell_to_variable(i, j + 1, 8, nb, nbCoupsInit, largeur,hauteur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j + 1, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j + 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit, largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)
                            else:

                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente
                                    if type == 7:  # cas  des pieges en attente qui passent actifs
                                        clauseSpecialise.append(-1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(-1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9,
                             10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)
                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))

                                    clauseSpecialise.append(sens * (
                                        cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                         largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                                    liste.append(clauseSpecialise)


    return liste


def regles_mouvG(largeur: int, hauteur: int, nbCoupsInit: int) -> List[List[int]]:
    liste = []
    # MouvG sans Piege :
    for i in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * action_to_variable(nb, "G"))  # si on fait l'action d'aller à gauche au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # et perso en i,j
                clause.append((cell_to_variable(i, j - 1, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i+j
                clause.append((cell_to_variable(i, j - 1, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i, j - 1, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append((cell_to_variable(i, j - 1, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append(
                    (cell_to_variable(i, j - 1, 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i, j - 1, 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j - 1, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j - 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 9, 10]:
                    for ip in range(0, hauteur):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit, largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)

                            else:
                                for sens in [1,
                                             -1]:  # car continuité est une équivalence. ...=>(nbPortei,j<=>(nb-1)Portei,j)

                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type

                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente

                                    if type == 7:  # cas  des pieges en attente qui deviennent actifs
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

    ##MouvD avec piegeFixe
    # C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2

    for i in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i, j - 1, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i+j
                clause.append((cell_to_variable(i, j - 1, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i, j - 1, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append((cell_to_variable(i, j - 1, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append(
                    -1 * (cell_to_variable(i, j - 1, 6, nb, nbCoupsInit, largeur,hauteur)))  # et piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i, j - 1, 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j - 1, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j - 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(0, hauteur):
                        for jp in range(0, largeur):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)

                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente
                                    if type == 7:  # cas  des pieges en attente qui passent actifs
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9,
                             10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)



                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))
                                    clauseSpecialise.append(1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                         largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                                    liste.append(clauseSpecialise)

    # MouvD avec piegeAttente a côté


    for i in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur - 1):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i, j - 1, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i, j - 1, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i, j - 1, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i, j - 1, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i,j+1
                clause.append(
                    (cell_to_variable(i, j - 1, 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i,j+1
                clause.append(
                    -1 * (cell_to_variable(i, j- 1, 8, nb, nbCoupsInit, largeur,hauteur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i, j - 1, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i and jp == j - 1):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)
                            else:

                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente
                                    if type == 7:  # cas  des pieges en attente qui passent actifs
                                        clauseSpecialise.append(-1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(-1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9,
                             10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur):
                        for jp in range(0, largeur):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)
                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))

                                    clauseSpecialise.append(sens * (
                                        cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                         largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                                    liste.append(clauseSpecialise)

    return liste


def regles_mouvH(largeur: int, hauteur: int, nbCoupsInit: int) -> List[List[int]]:
    liste = []


    # MouvH sans Piege :
    for i in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * action_to_variable(nb, "H"))  # si on fait l'action d'aller en haut au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # et perso en i,j
                clause.append((cell_to_variable(i-1, j, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i+j
                clause.append((cell_to_variable(i- 1, j , 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i- 1, j , 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append((cell_to_variable(i- 1, j , 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append(
                    (cell_to_variable(i- 1, j , 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i- 1, j , 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i- 1, j , 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i - 1and jp == j ):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 9, 10]:
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit, largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)

                            else:
                                for sens in [1,
                                             -1]:  # car continuité est une équivalence. ...=>(nbPortei,j<=>(nb-1)Portei,j)

                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type

                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente

                                    if type == 7:  # cas  des pieges en attente qui deviennent actifs
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

    print("Fin regles specifiques H")
    ##MouvD avec piegeFixe
    # C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2

    for i in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i- 1, j , 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i+j
                clause.append((cell_to_variable(i- 1, j , 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i- 1, j , 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append((cell_to_variable(i - 1, j, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append(
                    -1 * (cell_to_variable(i - 1, j, 6, nb, nbCoupsInit, largeur,hauteur)))  # et piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i - 1, j, 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i- 1, j , 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i - 1 and jp == j ):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)

                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente
                                    if type == 7:  # cas  des pieges en attente qui passent actifs
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9,
                             10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)



                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))
                                    clauseSpecialise.append(1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                         largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                                    liste.append(clauseSpecialise)
    print("Fin regles piege fixe")
    # MouvD avec piegeAttente a côté

    for i in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i- 1, j , 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i- 1, j , 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i - 1, j, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i - 1, j, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i,j+1
                clause.append(
                    (cell_to_variable(i - 1, j, 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i,j+1
                clause.append(
                    -1 * (cell_to_variable(i - 1, j, 8, nb, nbCoupsInit, largeur,hauteur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i - 1, j, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i - 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (
                                cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur,hauteur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur,hauteur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur ):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    return liste


def regles_mouvB(largeur: int, hauteur: int, nbCoupsInit: int) -> List[List[int]]:
    liste = []

    # MouvH sans Piege :
    for i in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * action_to_variable(nb, "B"))  # si on fait l'action d'aller en bas au coup nb
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i + 1, j, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i+j
                clause.append((cell_to_variable(i + 1, j, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i + 1, j, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append((cell_to_variable(i + 1, j, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append(
                    (cell_to_variable(i + 1, j, 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i + 1, j, 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i + 1, j, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur ):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i + 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 9, 10]:
                    for ip in range(0, hauteur):
                        for jp in range(0, largeur ):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit, largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(-1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                                largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)

                            else:
                                for sens in [1,
                                             -1]:  # car continuité est une équivalence. ...=>(nbPortei,j<=>(nb-1)Portei,j)

                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type

                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente

                                    if type == 7:  # cas  des pieges en attente qui deviennent actifs
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)
    ##MouvD avec piegeFixe
    # C'est avec ca qu'on contrôle ce qu'il se passe en prennant des dégats. On dit que si on va sur piege à nb-1, alors continuité de tout jusque nb-2

    for i in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i + 1, j, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i+j
                clause.append((cell_to_variable(i + 1, j, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i+j
                clause.append((cell_to_variable(i + 1, j, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i+j
                clause.append((cell_to_variable(i + 1, j, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i+j
                clause.append(
                    -1 * (cell_to_variable(i + 1, j, 6, nb, nbCoupsInit, largeur,hauteur)))  # et piege actif fixe en i+j
                clause.append(
                    (cell_to_variable(i + 1, j, 8, nb, nbCoupsInit, largeur,hauteur)))  # et non piege en attente en i+j

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i + 1, j, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i + 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(0, hauteur):
                        for jp in range(0, largeur):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)

                                ##Si piege fixe, il meurt :
                                clauseSpecialise2 = clause.copy()
                                clauseSpecialise2.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, 6, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege fixe
                                clauseSpecialise2.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise2)

                                # Si piege en attente, il meurt :
                                clauseSpecialise3 = clause.copy()
                                clauseSpecialise3.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                           largeur,hauteur)))  # si piege en attente
                                clauseSpecialise3.append(
                                    -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                           largeur,hauteur)))  # nouvelle situation sans squelette
                                liste.append(clauseSpecialise3)

                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    # Qu'on specialise par case et type
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb, nbCoupsInit,
                                                         largeur,hauteur)))  # situation précédente
                                    if type == 7:  # cas  des pieges en attente qui passent actifs
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege actif

                                    elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # devient un piege en attente

                                    else:
                                        clauseSpecialise.append(1 * sens * (
                                            cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                             largeur,hauteur)))  # nouvelle situation

                                    liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9,
                             10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur ):
                        for jp in range(0, largeur):

                            # A PART car l'équivalence est pas vrai?
                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                clauseSpecialise = clause.copy()
                                clauseSpecialise.append(-1 * (
                                    cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                     largeur,hauteur)))  # situation précédente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation
                                liste.append(clauseSpecialise)



                            else:
                                for sens in [-1, 1]:
                                    # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                                    clauseSpecialise = clause.copy()
                                    clauseSpecialise.append(-1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))
                                    clauseSpecialise.append(1 * sens * (
                                        cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                         largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                                    liste.append(clauseSpecialise)

    # MouvD avec piegeAttente a côté

    for i in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
        for j in range(0, largeur):  # car premiere et derniere colonnes sont que des murs
            for nb in range(1, nbCoupsInit + 1):
                clause = []
                clause.append(-1 * (cell_to_variable(i, j, 2, nb, nbCoupsInit, largeur,hauteur)))  # perso en i,j
                clause.append((cell_to_variable(i + 1, j, 4, nb, nbCoupsInit, largeur,hauteur)))  # et non block en i,j+1
                clause.append((cell_to_variable(i + 1, j, 5, nb, nbCoupsInit, largeur,hauteur)))  # et non soldat en i,j+1
                clause.append((cell_to_variable(i + 1, j, 1, nb, nbCoupsInit, largeur,hauteur)))  # et non mur en i,j+1
                clause.append((cell_to_variable(i + 1, j, 3, nb, nbCoupsInit, largeur,hauteur)))  # et non porte en i,j+1
                clause.append(
                    (cell_to_variable(i + 1, j, 6, nb, nbCoupsInit, largeur,hauteur)))  # et non piege actif fixe en i,j+1
                clause.append(
                    -1 * (cell_to_variable(i + 1, j, 8, nb, nbCoupsInit, largeur,hauteur)))  # et piege en attente en i,j+1

                # IMPLIQUE

                clauseNvPosPerso = clause.copy()
                clauseNvPosPerso.append(cell_to_variable(i + 1, j, 2, nb - 1, nbCoupsInit, largeur,hauteur))  # perso en i,j+1
                liste.append(clauseNvPosPerso)  # Clause qui donne la position du perso

                for ip in range(0, hauteur):  # car premiere et derniere lignes sont que des murs
                    for jp in range(0, largeur ):  # car premiere et derniere colonnes sont que des murs
                        if not (ip == i + 1 and jp == j):
                            clauseInterditPosPerso = clause.copy()
                            clauseInterditPosPerso.append(-1 * (cell_to_variable(ip, jp, 2, nb - 1, nbCoupsInit,
                                                                                 largeur,hauteur)))  # non perso en i,j , et partout ailleurs
                            liste.append(clauseInterditPosPerso)

                # Et continuité pour chaque case autre que Piege Fixe et Sortie et Mur (regles déjà spécifiées au dessus) et Perso (fait juste avant)
                for type in [3, 4, 5, 7, 8, 9, 10]:
                    for ip in range(0, hauteur):
                        for jp in range(0, largeur ):

                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente
                            clauseSpecialise = clause.copy()

                            # Qu'on specialise par case et type
                            clauseSpecialise.append(-1 * (
                                cell_to_variable(ip, jp, type, nb, nbCoupsInit, largeur,hauteur)))  # situation précédente

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append(
                                    (cell_to_variable(ip, jp, 6, nb, nbCoupsInit, largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation

                            elif type == 7:  # cas  des pieges en attente qui passent actifs
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                               largeur,hauteur)))  # devient un piege actif

                            elif type == 8:  # cas  des pieges actifs qui deviennent en attente
                                clauseSpecialise.append(-1 * (cell_to_variable(ip, jp, 7, nb - 1, nbCoupsInit,
                                                                               largeur,hauteur)))  # devient un piege en attente

                            else:
                                clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # nouvelle situation

                            liste.append(clauseSpecialise)

                # Puis continuité de tout (sauf Murs, pieges actifs et sortie, déjà fais)
                for type in [2, 3, 4, 5, 7, 8, 9, 10]:  # les pieges pas fixes restent inchangés lors de cette opération
                    for ip in range(0, hauteur):
                        for jp in range(0, largeur ):
                            # Pour chaque cas et case possible on  cree une nouvelle clause, qui démarre comme la précédente

                            clauseSpecialise = clause.copy()
                            # Qu'on specialise par case et type
                            clauseSpecialise.append(
                                -1 * (cell_to_variable(ip, jp, type, nb - 1, nbCoupsInit, largeur,hauteur)))

                            if type == 5:  # cas du soldat, qui n'a de continuité que si pas sur piege Actif et pas sur Piege en attente
                                clauseSpecialise.append((cell_to_variable(ip, jp, 6, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # si pas de piege fixe
                                clauseSpecialise.append((cell_to_variable(ip, jp, 8, nb - 1, nbCoupsInit,
                                                                          largeur,hauteur)))  # et pas de piège en attente

                            clauseSpecialise.append((cell_to_variable(ip, jp, type, nb - 2, nbCoupsInit,
                                                                      largeur,hauteur)))  # nouvelle situation, on a perdu un coup

                            liste.append(clauseSpecialise)

    return liste



#####################################################################################
######################### TEST ##############
""""
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
"""

##############################################



################################## Partie main ################
def grid_to_faits() -> List[List[int]] :
    global infosGrille
    liste=[]
    #grille est tableau contenu dans le dictionnaire que renvoie grid_from_file()
    # A FINIR : ATTENTION AUX SORTIES
    ## ATTENTION : cas T et U (et P, Q)?

    for ligne in range(0,infosGrille["m"]):
        for col in range(0,infosGrille["n"]):
            nvClause=[]
            if infosGrille["grid"][ligne][col] == "#" : #cas mur

                nvClause.append(cell_to_variable(ligne,col,1,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "H" : #cas Perso
                nvClause.append(cell_to_variable(ligne,col,2,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "B" : #cas Block
                nvClause.append(cell_to_variable(ligne,col,4,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "K" : #cas clé
                nvClause.append(cell_to_variable(ligne,col,9,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "L" : #cas Porte
                nvClause.append(cell_to_variable(ligne,col,3,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "M" : #cas Soldat
                nvClause.append(cell_to_variable(ligne,col,5,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "S" : #cas Piege Fixe
                nvClause.append(cell_to_variable(ligne,col,6,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "T" : #cas PiegePasFixeAttente
                nvClause.append(cell_to_variable(ligne,col,8,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "U" : #cas PiegePasFixeActif
                nvClause.append(cell_to_variable(ligne,col,7,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "O" : #cas Block ET PiegeFixe
                nvClause.append(cell_to_variable(ligne,col,4,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                nvClause.append(cell_to_variable(ligne, col, 6, infosGrille["max_steps"], infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "P" : #cas Block ET PiegePasFixeAttente
                nvClause.append(cell_to_variable(ligne,col,4,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                nvClause.append(cell_to_variable(ligne, col, 8, infosGrille["max_steps"], infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)
            elif infosGrille["grid"][ligne][col] == "Q" : #cas Block ET PiegePasFixeActif
                nvClause.append(cell_to_variable(ligne,col,4,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                nvClause.append(cell_to_variable(ligne, col, 7, infosGrille["max_steps"], infosGrille["max_steps"],infosGrille["n"],infosGrille["m"]))
                liste.append(nvClause)

            elif infosGrille["grid"][ligne][col] == "D" : #cas Démonne, on met les voisins en sortie
                voisins=[(ligne-1,col),(ligne+1,col),(ligne,col+1),(ligne,col-1)]
                for v in voisins:
                    var=cell_to_variable(v[0],v[1],0,infosGrille["max_steps"],infosGrille["max_steps"],infosGrille["n"],infosGrille["m"])
                    if var != 0:
                        liste.append(var)



    return liste





def monsuperplanificateur(model, NbCoupsInit : int) ->str :
    #Le modèle renvoie dans l'ordre des var?
    #Rappel : pour les var mouvement:
        # H : litt%4==1
        # D : litt%4==2
        # B : litt%4==3
        # G : litt%4==0

    plan=""
    for littMouv in model[1]:
        if abs(littMouv)<=4*NbCoupsInit and littMouv>0:
            if littMouv%4==1:
                plan=plan+"H"
            elif littMouv%4==2:
                plan=plan+"D"
            elif littMouv%4==3:
                plan=plan+"B"
            elif littMouv%4==0:
                plan=plan+"G"

    return plan


def main():
    global infosGrille
    global listeClauses

    # récupération du nom du fichier depuis la ligne de commande
    #filename = sys.argv[1]

    # récupération de al grille et de toutes les infos déjà fait plus haut
    #infos = grid_from_file(filename)

    listeClauses+=grid_to_faits()
    print(1)
    listeClauses+=create_fait_bonneFin()
    print(2)
    listeClauses += create_regles_constantes(infosGrille["n"], infosGrille["m"], infosGrille["max_steps"])
    print(3)
    listeClauses+=at_leat_one_action(infosGrille["max_steps"])
    print(4)
    listeClauses+=unique_action(infosGrille["max_steps"])
    print(5)
    listeClauses+=regles_mouvH(infosGrille["n"],infosGrille["m"],infosGrille["max_steps"])
    print(6)
    listeClauses += regles_mouvD(infosGrille["n"], infosGrille["m"], infosGrille["max_steps"])
    print(7)
    listeClauses += regles_mouvB(infosGrille["n"], infosGrille["m"], infosGrille["max_steps"])
    print(8)
    listeClauses += regles_mouvG(infosGrille["n"], infosGrille["m"], infosGrille["max_steps"])
    print(9)

    dimacs=clauses_to_dimacs(listeClauses,nb_vars)
    print("Dimacs ok")
    write_dimacs_file(dimacs,"helltaker.cnf")
    print("Fichier dimacs créé")
    modele = exec_gophersat("helltaker.cnf", "gophersat") ##ATTENTION mettre Gophersat dans mon dossier
    print("Dimacs executé")
    # calcul du plan
    plan = monsuperplanificateur(modele,infosGrille["max_steps"])

    # affichage du résultat
    #if check_plan(plan):
    print("[OK]", plan)
    #else:
        #print("[Err]", plan, file=sys.stderr)
        #sys.exit(2)


if __name__ == "__main__":
    main()