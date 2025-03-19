import itertools
import re

def remove_repeating_term(s, term):
    pattern = f"({re.escape(term)})+"  # Match p repeated as many times as possible
    match = re.search(pattern, s)  # Find the first occurrence

    if match:
        prefix = s[:match.start()]  # Everything before the match
        suffix = s[match.end():]  # Everything after the match
        return (prefix, suffix)
    else:
        return None
    
def find_patterns(term, prefixes, suffixes, small, depth):
    depth += 1
    print(depth)
    print(f"prefixes: {prefixes}")
    print(f"suffixes: {suffixes}")
    print(f"small: {small}")
    patterns = generate_games(term, prefixes, suffixes)
    for pattern in patterns:
        
        pattern_string = "".join(pattern)
        for i in range(len(pattern_string)):
            positions = make_move(pattern_string, i)
            if positions:
                for direction, game in enumerate(positions):
                    
                    for subgame, position in enumerate(game):
                        result = remove_repeating_term(position, term)
                        
                        if result:
                            prefixes.append(result[0])
                            suffixes.append(result[1])
                        else: 
                            # if we made a move that altered the prefix or suffix and we couldn't remove repeating terms, then ignore the result
                            prefix = pattern[0]
                            suffix = pattern[-1]
                            # direction says we moved left if 0, right if 1
                            # subgame says whether we are looking at the left or right subgame: left = 0 right = 1
                            if subgame == 0:
                                # we moved left into the prefix
                                if i <= len(prefix) and direction == 0:
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
                                prefixes.append(prefix)
                                suffixes.append(position[len(prefix):])
                            if subgame == 1:
                                # we moved right into the suffix
                                if i >= len(pattern_string) - len(suffix) and direction == 1:
                                    small.append(position)
                                    continue
                                prefixes.append(position[:-len(suffix)])
                                suffixes.append(suffix)
    prefixes = list(set(prefixes))
    suffixes = list(set(suffixes))
    small = list(set(small))
    if depth > 10:
        return prefixes, suffixes
    prefixes, suffixes = find_patterns(term, prefixes, suffixes, small, depth)
    return prefixes, suffixes

def generate_games(term, prefixes, suffixes):
    result = []
    combos = list(itertools.product(prefixes, suffixes))
    for combo in combos:
        result.append([combo[0], term, term, combo[1]])
    return result

def make_move(pattern, index):
    piece = pattern[index]
    left = pattern[:index]
    right = pattern[index + 1:]
    #print(f"{pattern}: ", left, piece, right)
    if left[-1:] == right[:1]:
        move_left = (left[:-1] + piece, right)
        move_right = (left, piece + right[1:])
        return [move_left, move_right]
    else:
        return None
    
find_patterns("xxo", [""], [""], [], 0)