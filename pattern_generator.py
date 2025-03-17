import re

def remove_first_pn(part_1, part_2, p, is_prefix=True):
    s = part_1 + part_2
    pattern = f"({re.escape(p)})+"  # Match p repeated as many times as possible
    match = re.search(pattern, s)  # Find the first occurrence

    if match:
        before = s[:match.start()]  # Everything before the match
        after = s[match.end():]  # Everything after the match
        return before, after
    else:
        # instead of this, maybe see if we can decompose s into two strings that we already have as prefixes and suffixes?
        return part_1, part_2

def find_patterns(term, pfx, sfx, depth=0):
    depth += 1
    prefixes = []
    suffixes = []
    print(pfx)
    print(sfx)
    for p in pfx:
        for s in sfx:
            l = len(p + term + s)
            to_test = p + term + s
            for k in range(1, l):
                right_piece = to_test[k:]
                left_piece = to_test[:k]
                # check if right_piece first element is different from leftPiece last element
                # if so, generate two patterns by deleting from one and switching the other
                # e.g. xxoo -> xx and oo
                print(f"to_test: {to_test}")
                if right_piece[0] != left_piece[-1]:
                    print(f"left: {left_piece}")
                    print(f"right: {right_piece}")
                    candidates = []
                    # p1: oo -> o
                    p1 = right_piece[1:]
                    candidates.append(remove_first_pn(right_piece[1:], "", term))
                    # s1: xx -> xo
                    s1 = left_piece[:-1] + right_piece[0]
                    candidates.append(remove_first_pn(left_piece[:-1], right_piece[0], term, False))
                    # p2: oo -> xo
                    p2 = left_piece[-1] + right_piece[1:]
                    candidates.append(remove_first_pn(left_piece[-1], right_piece[1:], term))
                    # s2: xx -> x
                    s2 = left_piece[:-1]
                    candidates.append(remove_first_pn("", left_piece[:-1], term, False))
                    print(candidates)
                    pfxs, sfxs = zip(*candidates)
                    prefixes.extend(pfxs)
                    suffixes.extend(sfxs)
                # otherwise, the move could not have been legal, so skip
    prefixes = list(set(prefixes + pfx))
    suffixes = list(set(suffixes + sfx))
    # remove xxx and ooo from prefixes and suffixes
    if set(prefixes) == set(pfx) and set(suffixes) == set(sfx):
        return prefixes, suffixes
    if depth > 2:
        return prefixes, suffixes
    prefixes, suffixes = find_patterns(term, prefixes, suffixes, depth)
    return prefixes, suffixes

find_patterns("xo", [""], [""])
#print(remove_first_pn("ooxoxoo", "ox"))