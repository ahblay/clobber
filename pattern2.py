import pg
from itertools import product
from collections import defaultdict

def safe_concat(a, b):
    return a + b if a is not None and b is not None else None

def append_unique(parent, item):
    if sorted(item) not in parent:
        parent.append(sorted(item))
    return parent

def generate_patterns(prefixes, suffixes, smalls, term):
    print(f'prefixes: {prefixes}')
    print(f'suffixes: {suffixes}')
    print(f'smalls: {smalls}')
    
    prefixes_copy = prefixes.copy()
    suffixes_copy = suffixes.copy()
    smalls_copy = smalls.copy()

    all_combos = list(product(prefixes, suffixes))
    for prefix, suffix in all_combos:
        p, s, sm = get_components(prefix, suffix, term)
        prefixes.extend(p)
        suffixes.extend(s)
        smalls.extend(sm)
    if set(prefixes) == set(prefixes_copy) and set(suffixes) == set(suffixes_copy) and set(smalls) == set(smalls_copy):
        print(f'prefixes: {prefixes_copy}')
        print(f'suffixes: {suffixes_copy}')
        print(f'smalls: {smalls_copy}')
        return prefixes_copy, suffixes_copy, smalls_copy
    prefixes, suffixes, smalls = generate_patterns(list(set(prefixes)), list(set(suffixes)), list(set(smalls)), term)
    return prefixes, suffixes, smalls

def get_components(prefix, suffix, term):
    prefixes = []
    suffixes = []
    small = []
    
    functions = [
        inside_q,
        between_q,
        inside_prefix,
        inside_suffix,
        between_prefix_q,
        between_q_suffix
    ]
    for f in functions:
        p, s, sm = f(prefix, suffix, term)
        prefixes.extend(p)
        suffixes.extend(s)
        small.extend(sm)
    return list(set(prefixes)), list(set(suffixes)), list(set(small))

def inside_q(prefix, suffix, term):
    """Iterate over each character of term, and return the prefixes, suffixes and small positions resulting
    from moving that character."""
    prefixes = set()
    suffixes = set()
    small = set()
    children = defaultdict(list)
    for index in range(len(term)):
        positions, piece = pg.make_move(term, index)
        print(positions)
        for position in positions:
            if position:
                child_positions = []
                print(list(zip(["left", "right"], position)))
                for location, component in zip(["left", "right"], position):
                    if location == "left":
                        suffixes.add(component)
                        small.add(prefix + component)
                        child_positions.append("_".join([prefix, component]))
                    if location == "right":
                        prefixes.add(component)
                        small.add(component + suffix)
                        child_positions.append("_".join([component, suffix]))
                append_unique(children[piece], sorted(child_positions))
    return prefixes, suffixes, small, children

def between_q(prefix, suffix, term):
    children = defaultdict(list)
    prefixes = set()
    suffixes = set()
    small = set()

    left_move_piece = term[0]
    right_move_piece = term[-1]
    
    q_plus = update_component_right(term, left_move_piece)
    q_minus = term[:-1]
    plus_q = update_component_left(term, right_move_piece)
    minus_q = term[1:]

    if q_plus is not None:
        suffixes.add(q_plus)
        prefixes.add(minus_q)
        small.add(prefix + q_plus)
        small.add(minus_q + suffix)
        append_unique(children[left_move_piece], [prefix + "_" + q_plus, minus_q + "_" + suffix])

    if plus_q is not None:
        prefixes.add(plus_q)
        suffixes.add(q_minus)
        small.add(plus_q + suffix)
        small.add(prefix + q_minus)
        append_unique(children[right_move_piece], [plus_q + "_" + suffix, prefix + "_" + q_minus])

    return prefixes, suffixes, small, children

def inside_prefix(prefix, suffix, term):
    prefixes = set()
    suffixes = set()
    small = set()
    children = defaultdict(list)
    
    if prefix == "":
        return prefixes, suffixes, small, children

    for index in range(len(prefix)):
        positions, piece = pg.make_move(prefix, index)
        for position in positions:
            if position:
                for location, component in zip(["left", "right"], position):
                    if location == "left":
                        small.append(component)
                    if location == "right":
                        prefixes.append(component)
    return list(set(prefixes)), [], list(set(small))

def inside_suffix(prefix, suffix, term):
    if suffix == "":
        return [], [], []
    suffixes = []
    small = []

    for index in range(len(suffix)):
        positions, piece = pg.make_move(suffix, index)
        for position in positions:
            if position:
                for location, component in zip(["left", "right"], position):
                    if location == "left":
                        suffixes.append(component)
                    if location == "right":
                        small.append(component)
    return [], list(set(suffixes)), list(set(small))

def between_prefix_q(prefix, suffix, term):
    if prefix == "":
        return [], [], []
    prefix_plus_q = update_component_right(prefix, term[0])
    minus_q = term[1:]
    prefix_minus = prefix[:-1]
    plus_prefix_q = update_component_left(term, prefix[-1])

    small = [sm for sm in (prefix_plus_q, prefix_minus) if sm is not None]
    prefixes = [p for p in (minus_q, plus_prefix_q) if p is not None]

    return list(set(prefixes)), [], list(set(small))

def between_q_suffix(prefix, suffix, term):
    if suffix == "":
        return [], [], []
    plus_q_suffix = update_component_left(suffix, term[-1])
    q_minus = term[:-1]
    minus_suffix = suffix[1:]
    q_plus_suffix = update_component_right(suffix, term[0])

    small = [sm for sm in (plus_q_suffix, minus_suffix) if sm is not None]
    suffixes = [p for p in (q_minus, q_plus_suffix) if p is not None]

    return [], list(set(suffixes)), list(set(small))

def update_component_right(component, piece):
    if component[-1] == piece:
        return None
    else:
        return component[:-1] + piece
    
def update_component_left(component, piece):
    if component[0] == piece:
        return None
    else:
        return piece + component[1:]

p, s, sm, c = inside_q("p", "s", "oxo")
print(p, s, sm, c)