#from typing import List, Tuple
#import itertools
#import subprocess
import sys
from helltaker_utils import grid_from_file, check_plan
from clingo.symbol import Number
from clingo.control import Control





################## Infos sur la grille ####################


infosGrille=grid_from_file(sys.argv[1]) #on initialise la grille

nbCol=infosGrille["n"]
nbLigne=infosGrille["m"]
nbCoups=infosGrille["max_steps"] #horizon



###############################################################

################# Parametres clingo ######################
class Context:
    def inc(self, x):
        return Number(x.number)

    def seq(self, x, y):
        return [x, y]

def on_model(m):
    print (m)


##################################################

##### Fonctions pour mettre en chaine de caractères les faits de la grille

def grid_to_environnment() ->str:
    res="%%%%%% Initialisation %%%%%%\n"

    res += "%% taille de monde%%\n"
    res += "#const nbCol = " + str(nbCol) + ".\n"
    res += "#const nbLigne = " + str(nbLigne) + ".\n\n"


    res += "%% pour la gestion de l'horizon%%\n"
    res += "#const horizon=" + str(nbCoups )+ ".\n"
    res += "step(0..horizon-1).\n\n"

    res+="%% Cellules : %%\n"
    res+="cell(0..nbLigne-1, 0..nbCol-1).\n\n"


    return res


def liste_actions() ->str:
    return "action(right; left; up;down;\
    pushup;pushdown;pushright;pushleft;\
    pushMobleft ;pushMobright; pushMobup;pushMobdown ;\
    takeKeyDown;takeKeyUp;takeKeyLeft;takeKeyRight;\
    unlockLeft; unlockRight; unlockUp; unlockDown;\
    hitLockLeft;hitLockRight;hitLockUp;hitLockDown;\
    nop).\n\n"

#Voir aClé, différent des autres
def grid_to_faits() -> str :

    global infosGrille
    res=""


    for ligne in range(0,infosGrille["m"]):
        for col in range(0,infosGrille["n"]):
            nvClause=[]
            if infosGrille["grid"][ligne][col] == "#" : #cas mur

                res+="mur("+str(ligne)+", "+str(col)+").\n"
            elif infosGrille["grid"][ligne][col] == "H" : #cas Perso
                res+="init(at("+str(ligne)+", "+str(col)+")).\n"
            elif infosGrille["grid"][ligne][col] == "B" : #cas Block
                res+="init(block("+str(ligne)+", "+str(col)+")).\n"
            elif infosGrille["grid"][ligne][col] == "K" : #cas clé
                res+="init(key("+str(ligne)+", "+str(col)+")).\n"
            elif infosGrille["grid"][ligne][col] == "L" : #cas Porte
                res+="init(lock("+str(ligne)+", "+str(col)+")).\n"
            elif infosGrille["grid"][ligne][col] == "M" : #cas Soldat
                res+="init(mob("+str(ligne)+", "+str(col)+")).\n"
            elif infosGrille["grid"][ligne][col] == "S" : #cas Piege Fixe
                res+="spike("+str(ligne)+", "+str(col)+").\n"
            elif infosGrille["grid"][ligne][col] == "T" : #cas PiegePasFixeAttente
                res+="init(trapOff("+str(ligne)+", "+str(col)+")).\n"
            elif infosGrille["grid"][ligne][col] == "U" : #cas PiegePasFixeActif
                res+="init(trapOn("+str(ligne)+", "+str(col)+")).\n"
            elif infosGrille["grid"][ligne][col] == "O" : #cas Block ET PiegeFixe
                res+="init(block("+str(ligne)+", "+str(col)+")).\n"
                res += "init(spike(" + str(ligne)+", "+str(col) + ")).\n"
            elif infosGrille["grid"][ligne][col] == "P" : #cas Block ET PiegePasFixeAttente
                res+="init(block("+str(ligne)+", "+str(col)+")).\n"
                res += "init(trapOff(" + str(ligne)+", "+str(col)+ ")).\n"
            elif infosGrille["grid"][ligne][col] == "Q" : #cas Block ET PiegePasFixeActif
                res+="init(block("+str(ligne)+", "+str(col)+")).\n"
                res += "init(trapOn(" + str(ligne)+", "+str(col) + ")).\n"

            elif infosGrille["grid"][ligne][col] == "D" : #cas Démonne, on met les voisins en sortie
                voisins=[(ligne-1,col),(ligne+1,col),(ligne,col+1),(ligne,col-1)]
                res += "demonne(" + str(ligne) + ", " + str(col) + ").\n"
                for v in voisins:
                    res+="goal(at("+str(v[0])+", "+str(v[1])+")).\n"

    res+="init(aCle(0)).\n\n" #vaudra 1 si on récupère la clé
    res+="fluent(F, 0) :- init(F).\n\n"

    return res

def regles_achieved() ->str :
    res="""
achieved(T) :- fluent(F, T),goal(F).

:- not achieved(_). % on doit finir
:- achieved(T), T > horizon. % on doit finir avant l'horizon
:- achieved(T), do(Act, T), Act != nop. % la seule action possible une fois qu'on a fini : nop
:- do(nop, T), not achieved(T). % mais on ne peut faire nop qu'une fois qu'on a fini


"""
    return res


##### Fonction generateur :
def generateur() ->str:
    res="%%%% Generateur d'actions : %%%\n"
    res+="{ do(Act, T): action(Act) } = 1 :- step(T).\n\n"

    return res


##### Frame Problem
def frame_problem() ->str:
    res="""
%%% Frame Problem
% les fluents qui n'ont pas ete supprimes restent a leur valeur
fluent(F, T + 1) :-
fluent(F, T),
    T + 1 < horizon,
    not removed(F, T).

% apres la fin, plus rien ne bouge
fluent(F, T + 1) :-
    fluent(F, T),
    achieved(T),
    T + 1 <= horizon.

"""
    return res


##### Actions possibles
def simpleMouv() ->str:
    res="%%% Mouvements simples %%%\n\n"
    res+="""
%%  action left
% preconditions
:-  do(left, T),
    fluent(at(X, Y), T),
    fluent(block(X, Y - 1), T).

:-  do(left, T),
    fluent(at(X, Y), T),
    not cell(X, Y -1).

:-  do(left, T),
    fluent(at(X, Y), T),
    mur(X,Y-1).
    
:-  do(left, T),
    fluent(at(X, Y), T),
    fluent(mob(X, Y - 1), T).
    
:-  do(left, T),
    fluent(at(X, Y), T),
    fluent(lock(X, Y - 1), T).
    
:-  do(left, T),
    fluent(at(X, Y), T),
    fluent(key(X, Y - 1), T).
    
:-  do(left, T),
    fluent(at(X, Y), T),
    fluent(spike(X, Y - 1), T). 
    
:-  do(left, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X, Y - 1), T). 
    
% effets
fluent(at(X, Y - 1), T + 1) :-
    do(left, T),
    fluent(at(X, Y), T).

removed(at(X, Y), T) :-
    do(left, T),
    fluent(at(X, Y), T).

%% action right
% preconditions
:-  do(right, T),
    fluent(at(X, Y), T),
    not cell(X, Y + 1).

:-  do(right, T),
    fluent(at(X, Y), T),
    fluent(block(X, Y + 1), T).

:-  do(right, T),
    fluent(at(X, Y), T),
    mur(X,Y+1).
    
:-  do(right, T),
    fluent(at(X, Y), T),
    fluent(mob(X, Y + 1), T).
    
:-  do(right, T),
    fluent(at(X, Y), T),
    fluent(lock(X, Y + 1), T).
    
:-  do(right, T),
    fluent(at(X, Y), T),
    fluent(key(X, Y + 1), T).
    
:-  do(right, T),
    fluent(at(X, Y), T),
    fluent(spike(X, Y + 1), T).    
    
:-  do(right, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X, Y + 1), T). 
    
% effets
fluent(at(X, Y + 1), T + 1) :-
    do(right, T),
    fluent(at(X, Y), T),
    cell(X, Y + 1),
    not fluent(block(X, Y + 1), T).

removed(at(X, Y), T) :-
    do(right, T),
    fluent(at(X, Y), T).
    
%% action down
% preconditions
:-  do(down, T),
    fluent(at(X, Y), T),
    not cell(X+ 1, Y ).

:-  do(down, T),
    fluent(at(X, Y), T),
    fluent(block(X+ 1, Y ), T).

:-  do(down, T),
    fluent(at(X, Y), T),
    mur(X+1,Y).
    
:-  do(down, T),
    fluent(at(X, Y), T),
    fluent(mob(X+1, Y ), T).
    
:-  do(down, T),
    fluent(at(X, Y), T),
    fluent(lock(X+1, Y), T).
    
:-  do(down, T),
    fluent(at(X, Y), T),
    fluent(key(X+1, Y), T).

:-  do(down, T),
    fluent(at(X, Y), T),
    fluent(spike(X+1, Y), T).


:-  do(down, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X+1, Y), T).
 
% effets
fluent(at(X+ 1, Y ), T + 1) :-
    do(down, T),
    fluent(at(X, Y), T),
    cell(X+ 1, Y ),
    not fluent(block(X+ 1, Y ), T).

removed(at(X, Y), T) :-
    do(down, T),
    fluent(at(X, Y), T).

%% action up
% preconditions
:-  do(up, T),
    fluent(at(X, Y), T),
    not cell(X- 1, Y ).

:-  do(up, T),
    fluent(at(X, Y), T),
    fluent(block(X-1, Y), T).

:-  do(up, T),
    fluent(at(X, Y), T),
    mur(X-1,Y).
    
:-  do(up, T),
    fluent(at(X, Y), T),
    fluent(mob(X-1, Y ), T).
    
:-  do(up, T),
    fluent(at(X, Y), T),
    fluent(lock(X-1, Y ), T).
    
:-  do(up, T),
    fluent(at(X, Y), T),
    fluent(key(X-1, Y ), T).

:-  do(up, T),
    fluent(at(X, Y), T),
    fluent(key(X-1, Y ), T). 
    
:-  do(up, T),
    fluent(at(X, Y), T),
    fluent(spike(X-1, Y ), T). 
        
:-  do(up, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X-1, Y ), T).
    
% effets
fluent(at(X-1, Y ), T + 1) :-
    do(up, T),
    fluent(at(X, Y), T),
    cell(X-1, Y ),
    not fluent(block(X-1, Y ), T).

removed(at(X, Y), T) :-
    do(up, T),
    fluent(at(X, Y), T).
    
"""

    return res


def pushBlock() -> str:
    res = "%%% Pousser blocks %%%\n\n"
    res += """
%%  push left
% preconditions
:-  do(pushleft, T),
    fluent(at(X, Y), T),
    not fluent(block(X, Y - 1), T).

:-  do(pushleft, T),
    fluent(at(X, Y), T),
    not cell(X, Y -1).
    
:-  do(pushleft, T),
    fluent(at(X, Y), T),
    not cell(X, Y -2).
    
:-  do(pushleft, T),
    fluent(at(X, Y), T),
    mur(X,Y-2).

:-  do(pushleft, T),
    fluent(at(X, Y), T),
    fluent(mob(X, Y -2), T).

:-  do(pushleft, T),
    fluent(at(X, Y), T),
    fluent(lock(X, Y - 2), T).

:-  do(pushleft, T),
    fluent(at(X, Y), T),
    fluent(key(X, Y - 2), T).

:-  do(pushleft, T),
    fluent(at(X, Y), T),
    fluent(block(X , Y - 2), T).

:-  do(pushleft, T),
    fluent(at(X, Y), T),
    demonne(X, Y -1).
    
% effets
fluent(block(X, Y - 2), T + 1) :-
    do(pushleft, T),
    fluent(at(X, Y), T).


removed(block(X, Y-1), T) :-
    do(pushleft, T),
    fluent(at(X, Y), T).
    
    
%%  push right
% preconditions
:-  do(pushright, T),
    fluent(at(X, Y), T),
    not fluent(block(X, Y + 1), T).

:-  do(pushright, T),
    fluent(at(X, Y), T),
    not cell(X, Y +1).
    
:-  do(pushright, T),
    fluent(at(X, Y), T),
    not cell(X, Y +2).
    
:-  do(pushright, T),
    fluent(at(X, Y), T),
    mur(X,Y+2).

:-  do(pushright, T),
    fluent(at(X, Y), T),
    fluent(mob(X, Y +2), T).

:-  do(pushright, T),
    fluent(at(X, Y), T),
    fluent(lock(X, Y + 2), T).

:-  do(pushright, T),
    fluent(at(X, Y), T),
    fluent(key(X, Y + 2), T).

:-  do(pushright, T),
    fluent(at(X, Y), T),
    fluent(block(X , Y + 2), T).

:-  do(pushright, T),
    fluent(at(X, Y), T),
    demonne(X , Y + 2).
    
    
% effets
fluent(block(X, Y + 2), T + 1) :-
    do(pushright, T),
    fluent(at(X, Y), T).

removed(block(X, Y+1), T) :-
    do(pushright, T),
    fluent(at(X, Y), T).
    
    
    
    
%%  push down
% preconditions
:-  do(pushdown, T),
    fluent(at(X, Y), T),
    not fluent(block(X+ 1, Y ), T).

:-  do(pushdown, T),
    fluent(at(X, Y), T),
    not cell(X+1, Y ).
    
:-  do(pushdown, T),
    fluent(at(X, Y), T),
    not cell(X+2, Y ).
    
:-  do(pushdown, T),
    fluent(at(X, Y), T),
    mur(X+2,Y).

:-  do(pushdown, T),
    fluent(at(X, Y), T),
    fluent(mob(X+2, Y ), T).

:-  do(pushdown, T),
    fluent(at(X, Y), T),
    fluent(lock(X+ 2, Y ), T).

:-  do(pushdown, T),
    fluent(at(X, Y), T),
    fluent(key(X+ 2, Y ), T).
    
:-  do(pushdown, T),
    fluent(at(X, Y), T),
    fluent(block(X + 2, Y ), T).

:-  do(pushdown, T),
    fluent(at(X, Y), T),
    demonne(X+2,Y).


% effets
fluent(block(X+ 2, Y ), T + 1) :-
    do(pushdown, T),
    fluent(at(X, Y), T).

removed(block(X+1, Y), T) :-
    do(pushdown, T),
    fluent(at(X, Y), T).




%%  push up
% preconditions
:-  do(pushup, T),
    fluent(at(X, Y), T),
    not fluent(block(X- 1, Y ), T).

:-  do(pushup, T),
    fluent(at(X, Y), T),
    not cell(X-1, Y ).
    
:-  do(pushup, T),
    fluent(at(X, Y), T),
    not cell(X-2, Y ).
    
:-  do(pushup, T),
    fluent(at(X, Y), T),
    mur(X-2,Y).

:-  do(pushup, T),
    fluent(at(X, Y), T),
    fluent(mob(X-2, Y ), T).

:-  do(pushup, T),
    fluent(at(X, Y), T),
    fluent(lock(X - 2, Y ), T).

:-  do(pushup, T),
    fluent(at(X, Y), T),
    fluent(key(X - 2, Y ), T).

:-  do(pushup, T),
    fluent(at(X, Y), T),
    fluent(block(X - 2, Y ), T).

:-  do(pushup, T),
    fluent(at(X, Y), T),
    demonne(X-2,Y).

% effets
fluent(block(X - 2, Y ), T + 1) :-
    do(pushup, T),
    fluent(at(X, Y), T).

removed(block(X - 1, Y), T) :-
    do(pushup, T),
    fluent(at(X, Y), T).

"""

    return res


def pushMob() -> str:

    res = "%%% Pousser mobs %%%\n\n"
    res += """
%%  push left
% preconditions
:-  do(pushMobleft, T),
    fluent(at(X, Y), T),
    not fluent(mob(X, Y - 1), T).

:-  do(pushMobleft, T),
    fluent(at(X, Y), T),
    not cell(X, Y -1).

:-  do(pushMobleft, T),
    fluent(at(X, Y), T),
    not cell(X, Y -2).

:-  do(pushMobleft, T),
    fluent(at(X, Y), T),
    fluent(key(X, Y - 2), T).

:-  do(pushMobleft, T),
    fluent(at(X, Y), T),
    demonne(X,Y-2).
    
    
% effets
    
    % quand le mob ne se casse pas
fluent(mob(X, Y - 2), T + 1) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    not fluent(block(X,Y-2),T),
    not fluent(mob(X,Y-2),T),
    not fluent(lock(X,Y-2),T),
    not mur(X,Y-2),
    not fluent(spike(X,Y-2),T),
    not fluent(trapOff(X,Y-2),T).

removed(mob(X, Y-1), T) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    not fluent(block(X,Y-2),T),
    not fluent(mob(X,Y-2),T),
    not fluent(lock(X,Y-2),T),
    not mur(X,Y-2),
    not fluent(spike(X,Y-2),T),
    not fluent(trapOff(X,Y-2),T).

    % quand le mob se casse : plusieurs possibilités
removed(mob(X, Y-1), T) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    fluent(block(X,Y-2),T).

removed(mob(X, Y-1), T) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    fluent(mob(X,Y-2),T).
    
removed(mob(X, Y-1), T) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    fluent(lock(X,Y-2),T). 
    
removed(mob(X, Y-1), T) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    mur(X,Y-2).    
    
removed(mob(X, Y-1), T) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    fluent(spike(X,Y-2),T).    
    
removed(mob(X, Y-1), T) :-
    do(pushMobleft, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X,Y-2),T).    
    
    
%%  push right
% preconditions
:-  do(pushMobright, T),
    fluent(at(X, Y), T),
    not fluent(mob(X, Y + 1), T).

:-  do(pushMobright, T),
    fluent(at(X, Y), T),
    not cell(X, Y +1).

:-  do(pushMobright, T),
    fluent(at(X, Y), T),
    not cell(X, Y + 2).

:-  do(pushMobright, T),
    fluent(at(X, Y), T),
    fluent(key(X, Y + 2), T).

:-  do(pushMobright, T),
    fluent(at(X, Y), T),
    demonne(X, Y + 2).
    
    
% effets
    
    % quand le mob ne se casse pas
    
fluent(mob(X, Y + 2), T + 1) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    not fluent(block(X,Y+2),T),
    not fluent(mob(X,Y+2),T),
    not fluent(lock(X,Y+2),T),
    not mur(X,Y+2),
    not fluent(spike(X,Y+2),T),
    not fluent(trapOff(X,Y+2),T).

removed(mob(X, Y+1), T) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    not fluent(block(X,Y+2),T),
    not fluent(mob(X,Y+2),T),
    not fluent(lock(X,Y+2),T),
    not mur(X,Y+2),
    not fluent(spike(X,Y+2),T),
    not fluent(trapOff(X,Y+2),T).

    % quand le mob se casse : plusieurs possibilités
removed(mob(X, Y+1), T) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    fluent(block(X,Y+2),T).

removed(mob(X, Y+1), T) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    fluent(mob(X,Y+2),T).
    
removed(mob(X, Y+1), T) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    fluent(lock(X,Y+2),T). 
    
removed(mob(X, Y+1), T) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    mur(X,Y+2).    
    
removed(mob(X, Y+1), T) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    fluent(spike(X,Y+2),T).    
    
removed(mob(X, Y+1), T) :-
    do(pushMobright, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X,Y+2),T).  


%%  push down
% preconditions
:-  do(pushMobdown, T),
    fluent(at(X, Y), T),
    not fluent(mob(X+ 1, Y ), T).

:-  do(pushMobdown, T),
    fluent(at(X, Y), T),
    not cell(X+1, Y ).

:-  do(pushMobdown, T),
    fluent(at(X, Y), T),
    not cell(X+ 2, Y ).

:-  do(pushMobdown, T),
    fluent(at(X, Y), T),
    fluent(key(X + 2, Y), T).

:-  do(pushMobdown, T),
    fluent(at(X, Y), T),
    demonne(X + 2, Y).

% effets
    
    % quand le mob ne se casse pas
    
fluent(mob(X+ 2, Y ), T + 1) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    not fluent(block(X+2,Y),T),
    not fluent(mob(X+2,Y),T),
    not fluent(lock(X+2,Y),T),
    not mur(X+2,Y),
    not fluent(spike(X+2,Y),T),
    not fluent(trapOff(X+2,Y),T).

removed(mob(X+1, Y), T) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    not fluent(block(X+2,Y),T),
    not fluent(mob(X+2,Y),T),
    not fluent(lock(X+2,Y),T),
    not mur(X+2,Y),
    not fluent(spike(X+2,Y),T),
    not fluent(trapOff(X+2,Y),T).

    % quand le mob se casse : plusieurs possibilités
removed(mob(X+1, Y), T) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    fluent(block(X+2,Y),T).

removed(mob(X+1, Y), T) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    fluent(mob(X+2,Y),T).
    
removed(mob(X+1, Y), T) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    fluent(lock(X+2,Y),T). 
    
removed(mob(X+1, Y), T) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    mur(X+2,Y).    
    
removed(mob(X+1, Y), T) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    fluent(spike(X+2,Y),T).    
    
removed(mob(X+1, Y), T) :-
    do(pushMobdown, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X+2,Y),T).  



%%  push up
% preconditions
:-  do(pushMobup, T),
    fluent(at(X, Y), T),
    not fluent(mob(X- 1, Y ), T).

:-  do(pushMobup, T),
    fluent(at(X, Y), T),
    not cell(X-1, Y ).

:-  do(pushMobup, T),
    fluent(at(X, Y), T),
    not cell(X- 2, Y ).

:-  do(pushMobup, T),
    fluent(at(X, Y), T),
    fluent(key(X - 2, Y), T).

:-  do(pushMobup, T),
    fluent(at(X, Y), T),
    demonne(X - 2, Y).

% effets
    
    % quand le mob ne se casse pas
    
fluent(mob(X - 2, Y ), T + 1) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    not fluent(block(X-2,Y),T),
    not fluent(mob(X-2,Y),T),
    not fluent(lock(X-2,Y),T),
    not mur(X-2,Y),
    not fluent(spike(X-2,Y),T),
    not fluent(trapOff(X-2,Y),T).

removed(mob(X-1, Y), T) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    not fluent(block(X-2,Y),T),
    not fluent(mob(X-2,Y),T),
    not fluent(lock(X-2,Y),T),
    not mur(X-2,Y),
    not fluent(spike(X-2,Y),T),
    not fluent(trapOff(X-2,Y),T).

    % quand le mob se casse : plusieurs possibilités
removed(mob(X-1, Y), T) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    fluent(block(X-2,Y),T).

removed(mob(X-1, Y), T) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    fluent(mob(X-2,Y),T).
    
removed(mob(X+1, Y), T) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    fluent(lock(X-2,Y),T). 
    
removed(mob(X-1, Y), T) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    mur(X-2,Y).    
    
removed(mob(X-1, Y), T) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    fluent(spike(X-2,Y),T).    
    
removed(mob(X-1, Y), T) :-
    do(pushMobup, T),
    fluent(at(X, Y), T),
    fluent(trapOff(X-2,Y),T).  


"""

    return res


#la cle ne peut être que sur une case sans rien dessus? On prevoit quand meme si soldat ou block...

def takeKey() -> str:
    res = "%%% Take the key (max. 1 on the map) %%%\n\n"
    res += """
%%  action left
% preconditions

:- do(takeKeyLeft,T),
    fluent(at(X,Y),T),
    not fluent(key(X,Y-1),T).
    
:-  do(takeKeyLeft, T),
    fluent(at(X, Y), T),
    fluent(key(X,Y-1),T),
    fluent(block(X, Y - 1), T).


:-  do(takeKeyLeft, T),
    fluent(at(X, Y), T),
    fluent(mob(X, Y - 1), T),
    fluent(key(X,Y-1),T).


% effets
fluent(at(X, Y - 1), T + 1) :-
    do(takeKeyLeft, T),
    fluent(at(X, Y), T).

fluent(aCle(1),T+1):-
    do(takeKeyLeft, T).

removed(key(X,Y-1),T) :-
    do(takeKeyLeft,T),
    fluent(at(X,Y),T).

removed(at(X, Y), T) :-
    do(takeKeyLeft, T),
    fluent(at(X, Y), T).

removed(aCle(0), T) :-
    do(takeKeyLeft, T).

%%  action right
% preconditions

:- do(takeKeyRight,T),
    fluent(at(X,Y),T),
    not fluent(key(X,Y+1),T).
    
:-  do(takeKeyRight, T),
    fluent(at(X, Y), T),
    fluent(key(X,Y+1),T),
    fluent(block(X, Y + 1), T).


:-  do(takeKeyRight, T),
    fluent(at(X, Y), T),
    fluent(mob(X, Y + 1), T),
    fluent(key(X,Y+1),T).


% effets
fluent(at(X, Y + 1), T + 1) :-
    do(takeKeyRight, T),
    fluent(at(X, Y), T).

fluent(aCle(1),T+1):-
    do(takeKeyRight, T).

removed(key(X,Y+1),T) :-
    do(takeKeyRight,T),
    fluent(at(X,Y),T).

removed(at(X, Y), T) :-
    do(takeKeyRight, T),
    fluent(at(X, Y), T).

removed(aCle(0), T) :-
    do(takeKeyRight, T).
    
    
%%  action up
% preconditions

:- do(takeKeyUp,T),
    fluent(at(X,Y),T),
    not fluent(key(X-1,Y),T).
    
:-  do(takeKeyUp, T),
    fluent(at(X, Y), T),
    fluent(key(X-1,Y),T),
    fluent(block(X- 1, Y ), T).


:-  do(takeKeyUp, T),
    fluent(at(X, Y), T),
    fluent(mob(X- 1, Y ), T),
    fluent(key(X-1,Y),T).


% effets
fluent(at(X- 1, Y ), T + 1) :-
    do(takeKeyUp, T),
    fluent(at(X, Y), T).

fluent(aCle(1),T+1):-
    do(takeKeyUp, T).

removed(key(X-1,Y),T) :-
    do(takeKeyUp,T),
    fluent(at(X,Y),T).

removed(at(X, Y), T) :-
    do(takeKeyUp, T),
    fluent(at(X, Y), T).

removed(aCle(0), T) :-
    do(takeKeyUp, T).

%%  action down
% preconditions

:- do(takeKeyDown,T),
    fluent(at(X,Y),T),
    not fluent(key(X+1,Y),T).
    
:-  do(takeKeyDown, T),
    fluent(at(X, Y), T),
    fluent(key(X+1,Y),T),
    fluent(block(X+ 1, Y ), T).


:-  do(takeKeyDown, T),
    fluent(at(X, Y), T),
    fluent(mob(X+ 1, Y ), T),
    fluent(key(X+1,Y),T).


% effets
fluent(at(X+ 1, Y ), T + 1) :-
    do(takeKeyDown, T),
    fluent(at(X, Y), T).

fluent(aCle(1),T+1):-
    do(takeKeyDown, T).

removed(key(X+1,Y),T) :-
    do(takeKeyDown,T),
    fluent(at(X,Y),T).

removed(at(X, Y), T) :-
    do(takeKeyDown, T),
    fluent(at(X, Y), T).
    
removed(aCle(0), T) :-
    do(takeKeyDown, T).
    
    
"""

    return res


def unlock() -> str:
    res = "%%% Unlock Door (max. 1 on the map) %%%\n\n"
    res += """
%%  action left
% preconditions

:- do(unlockLeft,T),
    fluent(at(X,Y),T),
    not fluent(lock(X,Y-1),T).

:-  do(unlockLeft, T),
    fluent(at(X, Y), T),
    not fluent(aCle(1), T).

% effets
fluent(at(X, Y - 1), T + 1) :-
    do(unlockLeft, T),
    fluent(at(X, Y), T).

fluent(aCle(0),T+1):-
    do(unlockLeft, T).

removed(lock(X,Y-1),T) :-
    do(unlockLeft,T),
    fluent(at(X,Y),T).

removed(aCle(1), T) :-
    do(unlockLeft, T).


%%  action right
% preconditions

:- do(unlockRight,T),
    fluent(at(X,Y),T),
    not fluent(lock(X,Y+1),T).

:-  do(unlockRight, T),
    fluent(at(X, Y), T),
    not fluent(aCle(1), T).

% effets
fluent(at(X, Y + 1), T + 1) :-
    do(unlockRight, T),
    fluent(at(X, Y), T).

fluent(aCle(0),T+1):-
    do(unlockRight, T).

removed(lock(X,Y+1),T) :-
    do(unlockRight,T),
    fluent(at(X,Y),T).

removed(aCle(1), T) :-
    do(unlockRight, T).


%%  action up
% preconditions

:- do(unlockUp,T),
    fluent(at(X,Y),T),
    not fluent(lock(X-1,Y),T).

:-  do(unlockUp, T),
    fluent(at(X, Y), T),
    not fluent(aCle(1), T).

% effets
fluent(at(X - 1, Y ), T + 1) :-
    do(unlockUp, T),
    fluent(at(X, Y), T).

fluent(aCle(0),T+1):-
    do(unlockUp, T).

removed(lock(X-1,Y),T) :-
    do(unlockUp,T),
    fluent(at(X,Y),T).

removed(aCle(1), T) :-
    do(unlockUp, T).



%%  action down
% preconditions

:- do(unlockDown,T),
    fluent(at(X,Y),T),
    not fluent(lock(X+1,Y),T).

:-  do(unlockDown, T),
    fluent(at(X, Y), T),
    not fluent(aCle(1), T).

% effets
fluent(at(X + 1, Y ), T + 1) :-
    do(unlockDown, T),
    fluent(at(X, Y), T).

fluent(aCle(0),T+1):-
    do(unlockDown, T).

removed(lock(X+1,Y),T) :-
    do(unlockDown,T),
    fluent(at(X,Y),T).

removed(aCle(1), T) :-
    do(unlockDown, T).


"""

    return res

#Tape dans porte si pas de clé
def hitLock() ->str:
    res = "%%% Tape dans une porte %%%\n\n"
    res += """
    %%  action left
    % preconditions

    :- do(hitLockLeft,T),
        fluent(at(X,Y),T),
        not fluent(lock(X,Y-1),T).

    :-  do(hitLockLeft, T),
        fluent(at(X, Y), T),
        fluent(aCle(1), T).

    % effets
    

    %%  action right
    % preconditions

    :- do(hitLockRight,T),
        fluent(at(X,Y),T),
        not fluent(lock(X,Y+1),T).

    :-  do(hitLockRight, T),
        fluent(at(X, Y), T),
        fluent(aCle(1), T).

    % effets
    
    
    %%  action up
    % preconditions

    :- do(hitLockUp,T),
        fluent(at(X,Y),T),
        not fluent(lock(X-1,Y),T).

    :-  do(hitLockUp, T),
        fluent(at(X, Y), T),
        fluent(aCle(1), T).

    % effets
    

    %%  action down
    % preconditions

    :- do(hitLockDown,T),
        fluent(at(X,Y),T),
        not fluent(lock(X+1,Y),T).

    :-  do(hitLockDown, T),
        fluent(at(X, Y), T),
        fluent(aCle(1), T).

    % effets
   

    """

    return res


####################################################################
def main():

    res=""
    res+=grid_to_environnment()
    res+=liste_actions()
    res+=grid_to_faits()
    res+=regles_achieved()
    res+=generateur()
    res+=frame_problem()
    res+=simpleMouv()
    res+=pushBlock()
    res+=pushMob()
    res+=takeKey()
    res+=unlock()
    res+=hitLock()
    res+="\n#show do/2.\n"

    f = open("ASP_file.txt", "w")
    f.write(res)
    f.close()

    ctl = Control()
    ctl.add("base", [],res)
    ctl.ground([("base", [])], context=Context())
    ctl.solve()
    print(ctl.solve(on_model=on_model))





if __name__ == "__main__":
    main()