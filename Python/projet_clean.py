from collections import namedtuple
from helltaker_utils import grid_from_file
import time

State = namedtuple(
    "State",
    ("hero", "block", "mob", "trapSafe", "trapUnSafe", "max_steps", "lock", "key"),
)  # fluents
Predicat = namedtuple("Predicat", ("goal", "wall", "spikes"))  # predicats

Action = namedtuple("action", ("verb", "direction"))
actions = {
    d: frozenset({Action("move", d), Action("pushMob", d), Action("killMobObject", d),Action("openLock", d),Action("pushBlock", d),Action("tapBlock", d)})
    for d in "udrl"
}  
def demoness_to_goal(demonessPos: list, wallPos: list):
    goal = []
    for pair in demonessPos:
        if not ((pair[0] + 1, pair[1]) in wallPos):
            goal.append((pair[0] + 1, pair[1]))
        if not ((pair[0] - 1, pair[1]) in wallPos):
            goal.append((pair[0] - 1, pair[1]))
        if not ((pair[0], pair[1] + 1) in wallPos):
            goal.append((pair[0], pair[1] + 1))
        if not ((pair[0], pair[1] - 1) in wallPos):
            goal.append((pair[0], pair[1] - 1))
    return goal


def init_map(filename: str):
    dic = grid_from_file(filename)
    tmp = {}  # dictionnaire temporaire qui sera inséré dans les types immutables
    i = 0  # coordonnées
    j = 0  # coordonnées
    # init des listes des objets possibles
    tmp["demoness"] = []
    tmp["wall"] = []
    tmp["block"] = []
    tmp["key"] = []
    tmp["lock"] = []
    tmp["mob"] = []
    tmp["spikes"] = []
    tmp["trapSafe"] = []
    tmp["trapUnSafe"] = []
    tmp["block"] = []
    tmp["spikes"] = []
    tmp["block"] = []
    tmp["trapSafe"] = []
    tmp["block"] = []
    tmp["trapUnSafe"] = []
    # init du tmp
    for line in dic["grid"]:
        i += 1
        j = 0
        for cell in line:
            j += 1
            match cell:
                case "H":
                    tmp["hero"]=(i, j)
                case "D":
                    tmp["demoness"].append((i, j))
                    tmp["wall"].append((i, j))
                case "#":
                    tmp["wall"].append((i, j))
                case "B":
                    tmp["block"].append((i, j))
                case "K":
                    tmp["key"].append((i, j))
                case "L":
                    tmp["lock"].append((i, j))
                case "M":
                    tmp["mob"].append((i, j))
                case "S":
                    tmp["spikes"].append((i, j))
                case "T":
                    tmp["trapSafe"].append((i, j))
                case "U":
                    tmp["trapUnSafe"].append((i, j))
                case "O":
                    tmp["block"].append((i, j))
                    tmp["spikes"].append((i, j))
                case "P":
                    tmp["block"].append((i, j))
                    tmp["trapSafe"].append((i, j))
                case "Q":
                    tmp["block"].append((i, j))
                    tmp["trapUnSafe"].append((i, j))
    # init de s0
    s0 = State(
        hero=tmp["hero"],
        block=frozenset(tmp["block"]),
        mob=frozenset(tmp["mob"]),
        trapSafe=frozenset(tmp["trapSafe"]),
        trapUnSafe=frozenset(tmp["trapUnSafe"]),
        lock=frozenset(tmp["lock"]),
        max_steps=dic["max_steps"],
        key=frozenset(tmp["key"]),
    )
    # init de map_rules
    map_rules = Predicat(
        goal=frozenset(demoness_to_goal(tmp["demoness"], tmp["wall"])),
        wall=frozenset(tmp["wall"]),
        spikes=frozenset(tmp["spikes"]),
    )
    return s0, map_rules


def is_free_wall(position, map_rules):
    return not (position in map_rules.wall)


def is_free_key(position, map_rules):
    return not (position in map_rules.key)


def is_free_lock(position, map_rules):
    return not (position in map_rules.lock)


def is_free_spikes(position, map_rules):
    return not (position in map_rules.spikes)

def is_free_block(position, map_rules):
    return not (position in map_rules.block)

def is_free_mob(position, map_rules):
    return not (position in map_rules.mob)

def is_free_trapSafe(position, map_rules):
    return not (position in map_rules.trapSafe)

def is_free_trapUnSafe(position, map_rules):
    return not (position in map_rules.trapUnSafe)



def one_step(position, direction):
    i, j = position
    return {"r": (i, j + 1), "l": (i, j - 1), "u": (i - 1, j), "d": (i + 1, j)}[
        direction
    ]


###################################

def do_fn(action, state, map_rules):
    if (state.max_steps<=0): return None
    X0 = state.hero
    block_ = state.block
    mob_ = state.mob
    trapSafe_ = state.trapSafe
    trapUnSafe_ = state.trapUnSafe
    max_steps_ = state.max_steps
    key_ = state.key
    lock_ = state.lock
    X1 =one_step(X0, action.direction)
    if action.verb == "move":
        if (
            is_free_wall(X1, map_rules)
            and is_free_block(X1, state)
            and is_free_mob(X1, state)
            and is_free_lock(X1, state)
        ):
            newMob = [
                x for x in list(mob_) if x not in list(trapSafe_)
            ]  # we will add it every time, basically if there is an existing mob in a spike it kills it
            if not is_free_trapSafe(X1, state) or not is_free_spikes(X1, map_rules):
                max_steps_ -= 2
            else:
                max_steps_ -= 1
            if(not is_free_key(X1,state)):key_=frozenset({})
            return State(
                hero=X1,
                block=block_,
                mob=frozenset(newMob),
                trapSafe=trapUnSafe_,
                trapUnSafe=trapSafe_,
                max_steps=max_steps_,
                lock=lock_,
                key=key_,
            )  # swap trapsafe with trapsUnsafe
        else:
            return None

    if (
        action.verb == "pushMob"
    ):  # without killing him against an object other than traps
        X2 = one_step(X1, action.direction)
        if not is_free_mob(X1,state) and is_free_wall(X2, map_rules)and is_free_block(X2, state)and is_free_mob(X2, state)and is_free_lock(X2, state)and is_free_spikes(X2, map_rules):
            newMob = list(state.mob)
            newMob.append(X2)
            newMob.remove(X1)
            newMob = [x for x in newMob if x not in list(trapSafe_)]
            if not is_free_trapSafe(X0, state) or not is_free_spikes(X0, map_rules):
                max_steps_ -= 2
            else:
                max_steps_ -= 1
            return State(
                hero=X0,
                block=block_,
                mob=frozenset(newMob),
                trapSafe=trapUnSafe_,
                trapUnSafe=trapSafe_,
                max_steps=max_steps_,
                lock=lock_,
                key=key_,
            )
        else:
            return None
    if action.verb == "killMobObject":
        X2 = one_step(X1, action.direction)
        if not is_free_mob(X1,state) and ( not is_free_block(X2,state) or not is_free_wall(X2,map_rules) or not is_free_mob(X2,state) or not is_free_lock(X2,state) or not is_free_spikes(X2,map_rules) or not is_free_trapSafe(X2,state)):
            newMob = list(state.mob)
            newMob.remove(X1)
            newMob = [x for x in newMob if x not in list(trapSafe_)]
            if not is_free_trapSafe(X0, state) or not is_free_spikes(X0, map_rules):
                max_steps_ -= 2
            else:
                max_steps_ -= 1
            return State(
                hero=X0,
                block=block_,
                mob=frozenset(newMob),
                trapSafe=trapUnSafe_,
                trapUnSafe=trapSafe_,
                max_steps=max_steps_,
                lock=lock_,
                key=key_,
            )
    if action.verb == "openLock":
        a=state.key
        if (    
            is_free_wall(X1, map_rules)
            and is_free_block(X1, state)
            and is_free_mob(X1, state)
            and not is_free_lock(X1, state)
            and a==frozenset()  # Le joueur possède la clef
        ):
            newMob = [x for x in list(state.mob) if x not in list(trapSafe_)]
            if not is_free_trapSafe(X1, state) or not is_free_spikes(X1, map_rules):
                max_steps_ -= 2
            else:
                max_steps_ -= 1
            return State(
                hero=X1,
                block=block_,
                mob=frozenset(newMob),
                trapSafe=trapUnSafe_,
                trapUnSafe=trapSafe_,
                max_steps=max_steps_,
                lock=frozenset({}),
                key=key_,
            )  # swap trapsafe with trapsUnsafe
        else:
            return None
    if action.verb == "pushBlock":
        X2 = one_step(X1, action.direction)
        if not is_free_block(X1,state) and is_free_wall(X2, map_rules)and is_free_block(X2, state)and is_free_mob(X2, state)and is_free_lock(X2, state):
            newBlock = list(state.block)
            newBlock.append(X2)
            newBlock.remove(X1)
            newMob = [x for x in list(state.mob) if x not in list(trapSafe_)]
            if not is_free_trapSafe(X0, state) or not is_free_spikes(X0, map_rules):
                max_steps_ -= 2
            else:
                max_steps_ -= 1
            return State(
                hero=X0,
                block=frozenset(newBlock),
                mob=frozenset(newMob),
                trapSafe=trapUnSafe_,
                trapUnSafe=trapSafe_,
                max_steps=max_steps_,
                lock=lock_,
                key=key_,
            )
        else:
            return None
    if action.verb == "tapBlock":
        X2 = one_step(X1, action.direction)
        if not is_free_block(X1,state) and (not is_free_wall(X2, map_rules) or not is_free_block(X2, state)or not is_free_mob(X2, state) or not is_free_lock(X2, state)):
            newMob = [x for x in list(state.mob) if x not in list(trapSafe_)]
            if not is_free_trapSafe(X0, state) or not is_free_spikes(X0, map_rules):
                max_steps_ -= 2
            else:
                max_steps_ -= 1
            return State(
                hero=X0,
                block=block_,
                mob=frozenset(newMob),
                trapSafe=trapUnSafe_,
                trapUnSafe=trapSafe_,
                max_steps=max_steps_,
                lock=lock_,
                key=key_,
            )
        else:
            return None

###############################################################
"""def succ_factory(rules) :
    def succ(state) :
        l = [(do_fn(a,state._asdict()),a) for a in actions]
        return {State(**x) : a for x,a in l if x}
    return succ"""

def succ(state, actions,map_rules):
    dic = {}
    for a in actions:
        for n in actions[a]:
            Temp=do_fn(n, state,map_rules)
            if Temp != None:
                dic[Temp] = a
    return dic

"""def goal_factory(rules) :
    def goals(state) :
        return state.boxes == rules['goals']
    return goals"""


def goals(state, rules):
    return (state.hero in list(rules.goal))

def insert_tail(s, l):
    l.append(s)
    return l
def remove_head(l):
    return l.pop(0), l
def remove_tail(l):
    return l.pop(), l
def dict2path(s, d):
    l = [(s, None)]
    while not d[s] is None:
        parent, a = d[s]
        l.append((parent, a))
        s = parent
    l.reverse()
    return l

######################################### recherche par lageur d'abord avec sauvegarde des états ######################################
def BFS(s0,actions,map_rules, goals, succ, remove, insert, debug=True):
    l = [s0]
    save = {s0: None}
    s = s0
    while l:
        if debug:
            print("l : ",l,'\n')# suivi précis:  print("keys : ",l[0].key,"hero : ",l[0].hero,"steps left :",l[0].max_steps,'\n')
        s, l = remove(l)
        for s2, a in succ(s, actions,map_rules).items():
            if not s2 in save:
                save[s2] = (s, a)
                if goals(s2, map_rules):
                    return s2, save
                insert(s2, l)
    return None, save

######################################### recherche en profondeur avec sauvegarde des états #########################
def DFS(s0,actions,map_rules, goals, succ, remove, insert, debug=True):
    l = [s0]
    save = {s0: None}
    s = s0
    while l:
        if debug:
            print("l : ",l,'\n')# suivi précis:  print("keys : ",l[0].key,"hero : ",l[0].hero,"steps left :",l[0].max_steps,'\n')
        s, l = remove(l)
        for s2, a in succ(s, actions,map_rules).items():
            if not s2 in save:
                save[s2] = (s, a)
                if goals(s2, map_rules):
                    return s2, save
                insert(s2, l)
    return None, save
###########################################################"
# Astar
def distManhattan(startingPoint, endPoint):
    x1, y1 = startingPoint[0],startingPoint[1]
    x2, y2 = endPoint[0], endPoint[1]
    dist = abs(x1 - x2) + abs(y1 - y2)
    return dist
def nearestGoal(position,goals):
    x=float('inf')
    for min in goals.goal:
     if x>=distManhattan(position,min):
         x=distManhattan(position,min)
         y=min
    return y


def Astar(s0,actions,map_rules, goals, succ, remove, insert, debug=True):
    l = [(s0,distManhattan(s0.hero,nearestGoal(s0.hero,map_rules)))]
    save = {s0: None}
    s = s0
    while l:
        if debug:
            print("l : ",l,'\n')
            #print("keys : ",l[0][0].key,"hero : ",l[0][0].hero,"steps left :",l[0][0].max_steps," heuristique",l[0][1],'\n')
        l.sort(key=lambda x:x[1])
        s, l = remove(l)
        for s2, a in succ(s[0], actions,map_rules).items():
            if not s2 in save:
                save[s2] = (s[0], a)
                if goals(s2, map_rules):
                    return s2, save
                insert((s2,distManhattan(s2.hero,nearestGoal(s2.hero,map_rules))+ s[1] - distManhattan(s[0].hero,nearestGoal(s[0].hero,map_rules))+1),l)
    return None, save



####################################################################################################""
t0 = time.time()
s0, map_rules=init_map('C:/Users/erraz/OneDrive/Bureau/projet IA02/Tests/level9.txt')

#s_end, save = BFS(s0,actions,map_rules, goals, succ, remove_head, insert_tail, debug=False)
s_end, save = DFS(s0,actions,map_rules, goals, succ, remove_tail, insert_tail, debug=False)
#s_end, save = Astar(s0,actions,map_rules, goals, succ, remove_head, insert_tail, debug=False)

plan = ''.join([a for s,a in dict2path(s_end,save) if a])

t1 = time.time()
total = t1-t0
#print(plan,"Breadth-First Search -> Execution time : ",total)
print(plan,"Depth First Search -> Execution time : ",total)
#print(plan,"A* -> Execution time : ",total)
