from collections import namedtuple
from helltaker_utils import grid_from_file

State = namedtuple(
    "State", ("hero", "block", "mob", "trapSafe", "trapUnSafe", "max_steps")
)  # fluents
Predicat = namedtuple(
    "Predicat", ("goal", "demoness", "wall", "key", "lock", "spikes")
)  # predicats

Action = namedtuple("action", ("verb", "direction"))
actions = {
    d: frozenset({Action("move", d), Action("push", d)}) for d in "udrl"
}  # toutes les actions

#################################### demoness_to_goal ne pas toucher & init_map à changer potentiellement mais fonctionnel


def demoness_to_goal(demonessPos: list, wallPos: list):
    goal = []
    print(demonessPos)
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
    tmp["hero"] = []
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
                    tmp["hero"].append((i, j))
                case "D":
                    tmp["demoness"].append((i, j))
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
        hero=frozenset(tmp["hero"]),
        block=frozenset(tmp["block"]),
        mob=frozenset(tmp["mob"]),
        trapSafe=frozenset(tmp["trapSafe"]),
        trapUnSafe=frozenset(tmp["trapUnSafe"]),
        max_steps=frozenset({dic["max_steps"]}),
    )
    # init de map_rules
    map_rules = Predicat(
        goal=frozenset(demonessToGoal(tmp["demoness"], tmp["wall"])),
        demoness=frozenset(tmp["demoness"]),
        wall=frozenset(tmp["wall"]),
        key=frozenset(tmp["key"]),
        lock=frozenset(tmp["lock"]),
        spikes=frozenset(tmp["spikes"]),
    )
    return s0, map_rules


#################################### is_free_XXX pas terminé
# TODO je crois que certaines sont inutiles, à la fin on pourra retirer celles qu'on n'utilise pas
def is_free_demoness(position, map_rules):
    return not (position in map_rules.demoness)


def is_free_wall(position, map_rules):
    return not (position in map_rules.wall)


def is_free_key(position, map_rules):
    return not (position in map_rules.key)


def is_free_lock(position, map_rules):
    return not (position in map_rules.lock)


def is_free_spikes(position, map_rules):
    return not (position in map_rules.spikes)


def is_free_hero(position, map_rules):
    return not (position in map_rules.hero)


def is_free_block(position, map_rules):
    return not (position in map_rules.block)


def is_free_mob(position, map_rules):
    return not (position in map_rules.mob)


def is_free_trapSafe(position, map_rules):
    return not (position in map_rules.trapSafe)


def is_free_trapUnSafe(position, map_rules):
    return not (position in map_rules.trapUnSafe)


#################################### one_step ne pas toucher


def one_step(position, direction):
    i, j = position
    return {"r": (i, j + 1), "l": (i, j - 1), "u": (i - 1, j), "d": (i + 1, j)}[
        direction
    ]


###################################


def do_fn(action, state):
    X0 = (
        state.me
    )  # on aura besoin de stocker temporairement les données le l'etat entré comme X0=state.me boxes1 = state.boxes
    boxes1 = (
        state.boxes
    )  # alors je pense que c'est mieux d'avoir une variable pour tous les prédicat/fluents afin de les manipuler facilement
    X1 = one_step(
        X0, action.direction
    )  # et vérifier les pré condition de chaque action.
    if action.verb == "move":
        if free(X1, map_rules) and not (X1 in boxes1):
            return State(
                me=X1, boxes=boxes1
            )  # LE PLUS IMPORTANT est d'avoir comme retour un type State qui est immutable alors hashable
        else:
            return None
    if action.verb == "push":
        X2 = one_step(X1, action.direction)
        if X1 in boxes1 and free(X2, map_rules) and not (X2 in boxes1):
            newBox = set(boxes1)
            newBox.add(X2)
            newBox.remove(X1)
            return State(boxes=frozenset(newBox), me=X1)
            # return State(boxes={X2} | boxes1 - {X1} ,me=X1) #ce retour est faux ! apparement le type de retour ici n'est pas un State alors pas hashable
            # alors vaut mieux prendre son temps et transformer le frozenset en set normal, faire les modifications adéquates, puis un retour simple de type State !!!!!!!!!!!!!!!!
        else:
            return None
    return None


############################################################### cette partie est fonctionne correctement je crois, vaut mieux de ne pas la toucher mdr
"""def succ_factory(rules) :
    def succ(state) :
        l = [(do_fn(a,state._asdict()),a) for a in actions]
        return {State(**x) : a for x,a in l if x}
    return succ"""


def succ(state, rules):
    dic = {}
    for a in rules.actions:
        for n in rules.actions[a]:
            if do_fn(n, state) != None:
                dic[do_fn(n, state)] = a
    return dic


"""def goal_factory(rules) :
    def goals(state) :
        return state.boxes == rules['goals']
    return goals"""


def goals(state, rules):
    return state.boxes == rules.goals


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


########################################################### cette partie est la derniere à modifier à mon avis, on utilisera une recherche non informé pour le moment
# dés que tout fonctionne, on peut faire une recherche informée
def search_with_parent(s0, goals, succ, remove, insert, debug=True):
    l = [s0]
    save = {s0: None}
    s = s0
    while l:
        if debug:
            print("l =", l)
        s, l = remove(l)
        for s2, a in succ(s, map_rules).items():
            if not s2 in save:
                save[s2] = (s, a)
                if goals(s2, map_rules):
                    return s2, save
                insert(s2, l)
    return None, save


"""s_end, save = search_with_parent(s0, goals, succ,remove_head, insert_tail, debug=False)
plan = ''.join([a for s,a in dict2path(s_end,save) if a])
print(plan)"""
