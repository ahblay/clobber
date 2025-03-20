import itertools
import re

def remove_repeating_term(s, term):
    """Takes a string s and a term and removes the first occurence of (term)^n for n > 0."""
    # defines the pattern to match as a repeated occurence of term
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
    
def find_patterns(term, prefixes, suffixes, small, depth):
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
        # TODO: Shouldn't this be range(len(pattern_string) + 1)? We care about the last character of the pattern too.
        for i in range(len(pattern_string)):
            # determine the positions resulting from moving the ith piece in a pattern left and right
            # each position is of the form [moved_left, moved_right]
            # moved_left, moved_right are of the form (left_piece, right_piece)
            # E.g. pattern_string = "xxOxxo" --> positions = [(xo, xxo), (xx, oxo)]
            # if a move is not legal, moved_left(right) is None
            positions = make_move(pattern_string, i)
            # iterate over moved_left, moved_right
            # direction = 0 --> piece moved left
            # direction = 1 --> piece moved right
            for direction, game in enumerate(positions):
                # if move was legal
                if game:
                    # iterate over left_piece, right_piece
                    # subgame = 0 --> left piece
                    # subgame = 1 --> right piece
                    for subgame, position in enumerate(game):
                        # remove occurences of term
                        result = remove_repeating_term(position, term)
                        """if pattern_string == "oxoxxoxxo":
                            print(f"pattern: {pattern}")
                            print(f"left and right moves: {positions}")
                            print(f"position (left and right subgames): {game}")
                            print(f"specific subgame: {position}")
                            print(f"result: {result}")"""
                        # if position had occurences of term, add characters before occurence to prefixes, after occurence to suffixes   
                        if result:
                            prefixes.append(result[0])
                            suffixes.append(result[1])
                        # if position did not have occurences of term
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

                                # TODO: are we missing the case where we move out of the original prefix?
                            # if we are looking at a right subgame
                            if subgame == 1:
                                # if that subgame was created by moving right into the original suffix
                                if i >= len(pattern_string) - len(suffix) and direction == 1:
                                    # add pattern to the set of small patterns
                                    small.append(position)
                                    continue
                                # mark the original suffix
                                suffixes.append(suffix)
                                # designate the leftover characters of position as a new prefix
                                prefixes.append(position[:-len(suffix)])
    # delete duplicate patterns from prefixes, suffixes, and small positions
    prefixes = list(set(prefixes))
    suffixes = list(set(suffixes))
    small = list(set(small))

    # if we didn't find any new patterns, return
    if set(prefixes) == set(pfxs) and set(suffixes) == set(sfxs) and set(small) == set(sm):
        return prefixes, suffixes, small
    
    # if we exceeded our depth restriction, return
    if depth > 10:
        return prefixes, suffixes, small
    
    # otherwise, keep searching with new set of prefixes, suffixes
    prefixes, suffixes, small = find_patterns(term, prefixes, suffixes, small, depth)
    return prefixes, suffixes, small

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
    return [move_left, move_right]
    
prefix, suffix, small = find_patterns("xxo", [""], [""], [], 0)
print(f"prefix: {prefix}")
print(f"suffix: {suffix}")
print(f"small: {small}")

def check_against_ryan():
    prefixes = ['', 'o', 'x', 'oxo', 'oo', 'xo']
    suffixes = ['', 'xx', 'xxx', 'o', 'x', 'xo']
    small = ['o', 'xx', 'x', 'ox', 'oxx', 'oo']
    result = []  
    for p in prefixes:
        for s in suffixes:
            #result.append(p + s)
            result.append(p + "q" + s)
    result.extend(small)
    return list(set(result))

'''print(check_against_ryan())

list1 = ['ooq', 'ooqo', 'ooqx', 'ooqxo', 'oox', 'ooxo', 'oq', 'oqx', 'oqxo', 'ox', 'oxo', 'oxoqx', 'oxoqxo', 'oxox', 'oxoxo', 'q', 'qo', 'qx', 'qxo', 'qxx', 'qxxx', 'xoqx', 'xox', 'xq', 'xqo', 'xqx', 'xqxo', 'xqxxx']
list2 = ['', 'q', 'xoqxxx', 'xoxo', 'oxo', 'oxoqxxx', 'xox', 'xoqx', 'ooqo', 'ooqxo', 'oxx', 'x', 'xxxx', 'xoqxx', 'xoxx', 'xoo', 'ooqxx', 'xoq', 'qx', 'xxo', 'oox', 'xqo', 'xoqxo', 'xx', 'ooxxx', 'xxx', 'ox', 'oxoo', 'xq', 'oxxx', 'oxoxxx', 'xqxxx', 'oxox', 'qxxx', 'qxo', 'oo', 'oxoxo', 'ooo', 'oqo', 'xoxxx', 'oxoqxx', 'xo', 'ooxx', 'oqxxx', 'ooxo', 'oxoq', 'oxoqo', 'qo', 'oxoqx', 'xqxx', 'ooqxxx', 'xqx', 'qxx', 'oxoqxo', 'o', 'oqx', 'oqxx', 'xoqo', 'ooq', 'xqxo', 'oq', 'oqxo', 'ooqx', 'oxoxx']
is_subset = set(list1).issubset(set(list2))
print(is_subset)
difference = set(list2) - set(list1)
print(list(difference))''' 