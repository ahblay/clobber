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
    # each pattern is of the form [prefix, term, term, suffix]
    patterns = generate_games(term, prefixes, suffixes)
    for pattern in patterns:
        # write pattern as string
        pattern_string = "".join(pattern)
        # iterate over each piece in pattern
        for i in range(len(pattern_string)):
            # determine the positions resulting from moving the ith piece in a pattern left and right
            # each position is of the form [moved_left, moved_right]
            # moved_left, moved_right are of the form (left_piece, right_piece)
            # E.g. pattern_string = "xxOxxo" --> positions = [(xo, xxo), (xx, oxo)]
            # if a move is not legal, moved_left(right) is None
            positions, piece = make_move(pattern_string, i)
            # iterate over moved_left, moved_right
            # direction = 0 --> piece moved left
            # direction = 1 --> piece moved right
            for direction, game in enumerate(positions):
                # if move was legal
                if game:
                    children = []
                    # iterate over left_piece, right_piece
                    # subgame = 0 --> left piece
                    # subgame = 1 --> right piece
                    for subgame, position in enumerate(game):
                        # remove occurrences of term
                        result = remove_repeating_term(position, term)
                        if pattern_string == "xoxoxx":
                            print(f"pattern: {pattern}")
                            print(f"left and right moves: {positions}")
                            print(f"position (left and right subgames): {game}")
                            print(f"specific subgame: {position}")
                            print(f"result: {result}")
                        # if position had occurrences of term, add characters before occurrence to prefixes, after occurrence to suffixes   
                        if result:
                            prefixes.append(result[0])
                            suffixes.append(result[1])
                            children.append(result[0] + "_" + result[1])
                        # if position did not have occurrences of term
                        else: 
                            # define the original prefix, suffix used to build the pattern
                            prefix = pattern[0]
                            suffix = pattern[-1]
                            # if we are looking at a left subgame
                            if subgame == 0:
                                # if that subgame was created by moving left into the original prefix
                                if i <= len(prefix) and direction == 0:
                                    # add pattern to the set of small patterns
                                    small.append(position)
                                    children.append(position)
                                    continue
                                # if subgame was created by moving right out of prefix
                                if i < len(prefix) and direction == 1:
                                    # add pattern to the set of small patterns
                                    small.append(position)
                                    children.append(position)
                                    continue
                                '''
                                print(f"pattern: {pattern}")
                                print(f"left and right moves: {positions}")
                                print(f"position (left and right subgames): {game}")
                                print(f"specific subgame: {position}")
                                print(f"new prefix: {prefix}")
                                print(f"new suffix: {position[len(prefix):]}")
                                '''
                                # mark the original prefix
                                prefixes.append(prefix)
                                # designate the leftover characters of position as a new suffix
                                suffixes.append(position[len(prefix):])

                                children.append(prefix + "_" + position[len(prefix):])

                            # if we are looking at a right subgame
                            if subgame == 1:
                                # if that subgame was created by moving right into the original suffix
                                if pattern_string == "xoxoxx":
                                    print(position)
                                    print(pattern_string)
                                    print(suffix)
                                    print(i)
                                if i >= len(pattern_string) - len(suffix) - 1 and direction == 1:
                                    # add pattern to the set of small patterns
                                    small.append(position)
                                    children.append(position)
                                    continue
                                # if subgame was created by moving a piece left out of original suffix
                                if i >= len(pattern_string) - len(suffix) and direction == 0:
                                    # add pattern to the set of small patterns
                                    small.append(position)
                                    children.append(position)
                                    continue

                                # mark the original suffix
                                suffixes.append(suffix)
                                # designate the leftover characters of position as a new prefix
                                if len(suffix) > 0:
                                    prefixes.append(position[:-len(suffix)])
                                    children.append(position[:-len(suffix)] + "_" + suffix)
                                else:
                                    prefixes.append(position)
                                    children.append(position + "_" + suffix)

                    if pattern_string == "xoxoxx":    
                        print(f"children: {children}")
                    binary_tree = {pattern[0] + "_" + pattern[-1]: sorted(children)}
                    if piece not in trees.keys(): trees[piece] = [] 
                    if binary_tree not in trees[piece]: trees[piece].append(binary_tree)             
    # delete duplicate patterns from prefixes, suffixes, and small positions
    prefixes = list(set(prefixes))
    suffixes = list(set(suffixes))
    small = list(set(small))

    # if we didn't find any new patterns, return
    if set(prefixes) == set(pfxs) and set(suffixes) == set(sfxs) and set(small) == set(sm):
        return sorted(prefixes), sorted(suffixes), sorted(small), trees
    
    # if we exceeded our depth restriction, return
    if depth > 10:
        return prefixes, suffixes, small, trees
    
    # otherwise, keep searching with new set of prefixes, suffixes
    prefixes, suffixes, small, trees = find_patterns(term, prefixes, suffixes, small, trees, depth)
    return prefixes, suffixes, small, trees

def generate_games(term, prefixes, suffixes):
    """Generate all possible games from a list of prefixes, suffixes and a repeating term."""
    result = []
    combos = list(itertools.product(prefixes, suffixes))
    for combo in combos:
        # each game has the form [prefix, term, term, suffix]
        result.append([combo[0], term, term, combo[1]])
    return result

def make_move(pattern, index):
    """Given a pattern string representing a game and a piece index to move, supply the games 
    resulting from moving that piece left and right."""
    # piece to move
    piece = pattern[index]
    # everything to the left of piece
    left = pattern[:index]
    # everything to the right of piece
    right = pattern[index + 1:]
    """
    if pattern == "oxoxxoxxo":
        print("%" * 50)
        print(f"index: {index}")
        print(f"left: {left}")
        print(f"piece: {piece}")
        print(f"right: {right}")
        print("%" * 50)
    """
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
        result = remove_repeating_term(pattern_string[::-1], term)
        if result:
            if result[0] in prefixes and result[1] in suffixes:
                symmetries[(prefix, suffix)] = (result[0], result[1])
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
            result[k].append(v)
    return dict(result)

# TODO: there is some bug here relating to small positions and the children of symmetric positions not being the same
def consolidate_trees(trees, symmetries):
    print(symmetries)
    reduced_trees = []
    # iterate over each dict representing a position type and its two child positions
    for tree in trees:
        print(tree)
        for position, children in tree.items():
            # if the prefix-suffix pair (p, s) is the shorter of its symmetric pair 
            if tuple(position.split("_")) not in symmetries.keys():
                new_children = []
                # iterate over children of current position
                for child in children:
                    # if child is not a small position, and it is not the shorter of the symmetric pair
                    if "_" in child and tuple(child.split("_")) in symmetries.keys():
                        # get shorter symmetry
                        shortened_child = symmetries[tuple(child.split("_"))]
                        new_child = "_".join(shortened_child)
                        # add it to list of new children
                        new_children.append(new_child)
                    else:
                        new_children.append(child)
                reduced_trees.append({position: new_children})
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