import itertools
import re
from pprint import pp
from collections import defaultdict

def remove_repeating_term(s, term):
    """Takes a string s and a term and removes the first occurrence of (term)^n for n > 0."""
    # defines the pattern to match as a repeated occurrence of term
    pattern = f"({re.escape(term)})+"
    # finds the first instance of pattern in s
    match = re.search(pattern, s)
    if match:
        # all characters in s before the matched string
        prefix = s[:match.start()]
        # all characters in s after the matched string
        suffix = s[match.end():]
        return (prefix, suffix)
    else:
        return None
    
def find_patterns(term, prefixes, suffixes, small, trees, depth):
    """Iterates over a set of possible clobber game patterns until no new patterns are found.
    
    Keyword arguments:
    term -- one term of the repeating sequence defining the initial game (e.g. "xxo").
    prefixes -- a list of all non-repeating strings that can precede term
    suffixes -- a list of all non-repeating strings that can succede term
    small -- a list of all standalone patterns
    depth -- a counter to limit depth of recursion
    """

    # copy prefixes, suffixes and small to check if new patterns were found at current depth
    pfxs = prefixes.copy()
    sfxs = suffixes.copy()
    sm = small.copy()

    # initialize depth
    depth += 1
    """print(depth)
    print(f"prefixes: {prefixes}")
    print(f"suffixes: {suffixes}")
    print(f"small: {small}")"""

    # get all possible pattern strings
    # each pattern is of the form [prefix, term, term, term, suffix]
    patterns = generate_games(term, prefixes, suffixes)
    for pattern in patterns:
        position = pattern[0] + "_" + pattern[-1]
 
        # write pattern as string
        pattern_string = "".join(pattern)

        p, s, sml, x_children, o_children = evaluate_pattern(pattern_string, term)
        prefixes.extend(p)
        suffixes.extend(s)
        small.extend(sml)

        # update trees with new child positions
        if position in trees["x"].keys():
            for child in x_children:
                if child not in trees["x"][position]:
                    trees["x"][position].append(child)
        else:
            trees["x"][position] = x_children

        if position in trees["o"].keys():
            for child in o_children:
                if child not in trees["o"][position]:
                    trees["o"][position].append(child)
        else:
            trees["o"][position] = o_children

    # delete duplicate patterns from prefixes, suffixes, and small positions
    prefixes = list(set(prefixes))
    suffixes = list(set(suffixes))
    small = list(set(small))

    # if we didn't find any new patterns, return
    if set(prefixes) == set(pfxs) and set(suffixes) == set(sfxs) and set(small) == set(sm):
        return sorted(prefixes), sorted(suffixes), sorted(small), trees
    
    # if we exceeded our depth restriction, return
    if depth > 1000:
        return prefixes, suffixes, small, trees
    
    # otherwise, keep searching with new set of prefixes, suffixes
    prefixes, suffixes, small, trees = find_patterns(term, prefixes, suffixes, small, trees, depth)
    return prefixes, suffixes, small, trees

def evaluate_pattern(pattern_string, term):
    """
    Take a given pattern string (e.g. xx oxoxox o),
    and evaluate every position resulting from each legal move.
    Return all resulting prefix, suffix, or small positions.
    Return a list of all positional types resulting from all moves.
    """
    prefixes = []
    suffixes = []
    small = []
    x_children = []
    o_children = []

    # iterate over each piece in pattern
    for i in range(len(pattern_string)):
        # determine the positions resulting from moving the ith piece in a pattern left and right
        # each position is of the form [moved_left, moved_right]
        # moved_left, moved_right are of the form (left_piece, right_piece)
        # E.g. pattern_string = "xxOxxo" --> positions = [(xo, xxo), (xx, oxo)]
        # if a move is not legal, moved_left(right) is None
        positions, piece = make_move(pattern_string, i)
        # iterate over moved_left, moved_right
        for move in positions:
            # if move was legal
            if move:
                p, s, sm, children = evaluate_positions(move, term)

                prefixes.extend(p)
                suffixes.extend(s)
                small.extend(sm)

                if piece == "x":
                    x_children.append(children)
                elif piece == "o":
                    o_children.append(children)
                else:
                    pass
    return list(set(prefixes)), list(set(suffixes)), list(set(small)), list(set(x_children)), list(set(o_children))

def evaluate_positions(positions, term):
    """Evaluate the positions (e.g. (xoxo, oox)) resulting from a given move in a pattern string. Return the
    prefixes, suffixes, small positions, and child positions of this move."""
    prefixes = []
    suffixes = []
    small = []
    children = []
    # iterate over components
    for component in positions:
        prefix, suffix, s, reduced = reduce_position(component, term)
        if prefix is not None: prefixes.append(prefix)
        if suffix is not None: suffixes.append(suffix)
        if s is not None: small.append(s)
        # TODO: this catches the case where a move is made at the end of a pattern string
        # TODO: do we care to include this as None?
        if reduced is not None: children.append(reduced)
    return list(set(prefixes)), list(set(suffixes)), list(set(small)), tuple(sorted(set(children)))

def reduce_position(position, term):
    """Take a position and represent it as a prefix/suffix/reduced, or small/reduced.
    If position has an instance of the repeating term, then it is given values for prefix/suffix/reduced.
    If not, and position is non-empty, it is considered small."""
    prefix = None
    suffix = None
    small = None
    # reduced form replaces repeating term with an underscore (e.g. x oxox oo --> x_oo)
    reduced = None
    if position == "":
        return prefix, suffix, small, reduced
    # remove occurrences of term
    result = remove_repeating_term(position, term) 
    #print(result)
    if result:
        prefix = result[0]
        suffix = result[1]
        reduced = result[0] + "_" + result[1]
    # if position did not have occurrences of term
    # TODO: in this case, try reducing the symmetric position
    else: 
        small = position
        reduced = position
    return prefix, suffix, small, reduced

def generate_games(term, prefixes, suffixes):
    """Generate all possible games from a list of prefixes, suffixes and a repeating term."""
    result = []
    combos = list(itertools.product(prefixes, suffixes))
    for combo in combos:
        # each game has the form [prefix, term, term, suffix]
        result.append([combo[0], term, term, term, combo[1]])
    return result

def make_move(pattern, index):
    """Given a pattern string representing a game and a piece index to move, supply the games 
    resulting from moving that piece left and right."""
    if index not in range(len(pattern)):
        return [None, None], None
    # piece to move
    piece = pattern[index]
    # everything to the left of piece
    left = pattern[:index]
    # everything to the right of piece
    right = pattern[index + 1:]

    # if there is a piece to the left of the active piece that is a different color
    if left[-1:] and piece != left[-1:]:
        # tuple representing the position after the active piece captures to the left
        move_left = (left[:-1] + piece, right)
    else:
        # no move possible
        move_left = None
    # if there is a piece to the right of the active piece that is a different color
    if right[:1] and piece != right[:1]:
        # tuple representing the position after the active piece captures to the right
        move_right = (left, piece + right[1:])
    else:
        # no move possible
        move_right = None
    return [move_left, move_right], piece

def find_symmetries(term, prefixes, suffixes):
    symmetries = {}
    patterns = generate_games(term, prefixes, suffixes)
    for pattern in patterns:
        prefix = pattern[0]
        suffix = pattern[-1]
        pattern_string = "".join(pattern)
        # remove repeating term in reversed pattern
        result = remove_repeating_term(pattern_string[::-1], term)
        if result:
            if result[0] in prefixes and result[1] in suffixes:
                symmetries[(prefix, suffix)] = (result[0], result[1])
            else:
                print("UH OH")
                print(f"prefix: {result[0]}, suffix: {result[1]}, prefixes: {prefixes}, suffixes: {suffixes}")
    return symmetries

def find_symmetries_small(term, prefixes, suffixes, small):
    symmetries = {}
    for sm in small:
        result = remove_repeating_term(sm[::-1], term)
        if result:
            if result[0] in prefixes and result[1] in suffixes:
                symmetries[(sm,)] = (result[0], result[1])
            else:
                print("UH OH")
                print(f"prefix: {result[0]}, suffix: {result[1]}, prefixes: {prefixes}, suffixes: {suffixes}")
    return symmetries

# removes duplicated entries in symmetries dict (i.e. ('', ''): ('o', 'xx') and ('o', 'xx'): ('', ''))
# sets keys to be the larger prefix-suffix pair in dict
def consolidate_symmetries_dict(symmetries):
    seen = set()
    for k, v in symmetries.copy().items():
        if len(''.join(k)) < len(''.join(v)):
            del symmetries[k]
        elif len(''.join(k)) == len(''.join(v)):
            if (v, k) in seen:
                del symmetries[k]
            else:
                seen.add((k, v))
    return symmetries

def restructure_trees(trees):
    result = defaultdict(list)
    for tree in trees:
        for k, v in tree.items():
            if v not in result[k]:
                result[k].append(v)
    return dict(result)

# TODO: there is some bug here relating to small positions and the children of symmetric positions not being the same
# TODO: WHAT IS HAPPENING WITH xx_x???
def consolidate_trees(trees, symmetries):
    print(symmetries)
    reduced_trees = []
    # iterate over each dict representing a position type and its two child positions
    for tree in trees:
        print(tree)
        for position, children in tree.items():
            # if the prefix-suffix pair (p, s) is the shorter of its symmetric pair
            ps_pair = tuple(position.split("_"))
            if ps_pair not in symmetries.keys() or symmetries[ps_pair] == ps_pair:
                new_children = []
                # iterate over children of current position
                for child in children:
                    # if child is not a small position, and it is not the shorter of the symmetric pair
                    if tuple(child.split("_")) in symmetries.keys():
                        # get shorter symmetry
                        shortened_child = symmetries[tuple(child.split("_"))]
                        new_child = "_".join(shortened_child)
                        # add it to list of new children
                        new_children.append(new_child)
                    else:
                        new_children.append(child)
                if child == "xxo":
                    print(f"new_children: {new_children}")
                reduced_trees.append({position: sorted(new_children)})
    return restructure_trees(reduced_trees)

def print_repeating_patterns(base_term, length):
    prefixes = []
    suffixes = []
    smalls = []
    for i in range(length):  
        term = "xx" + base_term * i
        prefix, suffix, small, trees = find_patterns(term, [""], [""], [], {}, 0)
        prefixes.append(prefix)
        suffixes.append(suffix)
        smalls.append(small)

    print("prefix:")
    for p in prefixes: print(p)
    print("suffix:")
    for s in suffixes: print(s)
    print("small:")
    for sm in smalls: print(sm)

def get_consolidated_form(symmetries, prefixes, suffixes, small):
    result = []  
    for p in prefixes:
        for s in suffixes:
            sym_p, sym_s = symmetries[(p, s)]
            if len(sym_p + sym_s) > len(p + s):
                result.append(p + s)
                result.append(p + "q" + s)
            elif len(sym_p + sym_s) < len(p + s):
                result.append(sym_p + sym_s)
                result.append(sym_p + "q" + sym_s)
            else:
                if (sym_p + sym_s) == (p + s):
                    result.append(p + s)
                else:
                    result.append((sym_p + sym_s, p + s))
                if (sym_p + "q" + sym_s) == (p + "q" + s):
                    result.append(p + "q" + s)
                else:
                    result.append((sym_p + "q" + sym_s, p + "q" + s))
    result.extend(small)
    return list(set(result))

def remove_common_elements(result, ryan):
    # Identify tuples in result that contain elements from ryan
    tuples_to_remove = {t for t in result if isinstance(t, tuple) and any(x in ryan for x in t)}
    
    # Identify direct common elements
    common_elements = set(result) & set(ryan)
    
    # Remove common elements and tuples containing ryan elements
    result_filtered = [x for x in result if x not in common_elements and x not in tuples_to_remove]
    ryan_filtered = [x for x in ryan if x not in common_elements and all(x not in t for t in tuples_to_remove)]
    
    return result_filtered, ryan_filtered

'''prefixes, suffixes, small, trees = find_patterns("xo", [""], [""], [], [], 0)
print(f"total prefixes: {prefixes}")
print(f"total suffixes: {suffixes}")
print(f"total small: {small}")
print("total trees:")
pp(trees)
symmetries = find_symmetries("xo", prefixes, suffixes)
print(symmetries)
print("+" * 40)
consolidated_symmetries = consolidate_symmetries_dict(symmetries)
print(consolidated_symmetries)
print("+" * 40)
pp(consolidate_trees(trees, consolidated_symmetries))'''

#print_repeating_patterns("o", 9)

'''syms = find_symmetries("xxo", prefixes, suffixes)
print(f"total small: {small}")
print(f"symmetries: {syms}")
result = get_consolidated_form(syms, prefixes, suffixes, small)
print(result)

ryan = ['ooq', 'ooqo', 'ooqx', 'ooqxo', 'oox', 'ooxo', 'oq', 'oqx', 'oqxo', 'ox', 'oxo', 'oxoqx', 'oxoqxo', 'oxox', 'oxoxo', 'q', 'qo', 'qx', 'qxo', 'qxx', 'qxxx', 'xoqx', 'xox', 'xq', 'xqo', 'xqx', 'xqxo', 'xqxxx']

filtered_result, filtered_ryan = remove_common_elements(result, ryan)
print(f"result: {filtered_result}")
print(f"ryan: {filtered_ryan}")'''