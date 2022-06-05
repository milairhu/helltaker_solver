from collections import namedtuple
from helltaker_utils import grid_from_file

State = namedtuple(
    "State",
    ("hero", "block", "mob", "trapSafe", "trapUnSafe", "max_steps", "lock", "key"),
)  # fluents
Predicat = namedtuple("Predicat", ("goal", "wall", "spikes"))  # predicats

Action = namedtuple("action", ("verb", "direction"))
actions = {
    d: frozenset({Action("move", d), Action("pushMob", d), Action("pushBlock", d)})
    for d in "udrl"
}  # actions

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
        max_steps=dic["max_steps"],
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


def do_fn(action, state, map_rules):
    X0 = state.hero
    block_ = state.block
    mob_ = state.mob
    trapSafe_ = state.trapSafe
    trapUnSafe_ = state.trapUnSafe
    max_steps_ = state.max_steps
    key_ = state.key
    lock_ = state.lock
    wall_ = map_rules.wall
    goal_ = map_rules.goal
    spikes_ = map_rules.spikes
    X1 = one_step(X0, action.direction)
    if action.verb == "move":
        if (
            is_free_wall(X1, map_rules)
            and is_free_block(X1, action)
            and is_free_mob(X1, action)
            and is_free_lock(X1, action)
            and is_free_key(X1, action)
            and is_free_trapSafe(X1, action)
            and is_free_trapUnSafe(X1, action)
            and is_free_spikes(X1, map_rules)
        ):
            newMob = [
                x for x in list(mob_) if x not in list(trapSafe_)
            ]  # we will add it every time, basically if there is an existing mob in a spike it kills it
            max_steps_ -= 1
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

    if action.verb == "pushSoldat":
        X2 = one_step(X1, action.direction)
        if X1 in mob_ and is_free_wall(X2, map_rules)and is_free_block(X2, action)and is_free_mob(X2, action)and is_free_lock(X2, action)and is_free_key(X2, action)and is_free_spikes(X2, map_rules):
            newMob=list(state.mob)
            newMob.add(X2)
            newMob.remove(X1)
            newMob = [x for x in newMob if x not in list(trapSafe_)]
            max_steps_ -= 1
            return State(hero=X0,block=block_,mob=frozenset(newMob),trapSafe=trapUnSafe_,trapUnSafe=trapSafe_,max_steps=max_steps_,lock=lock_,key=key_,)
        else:
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
