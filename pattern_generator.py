import re

def remove_first_pn(s, p, original_prefix_suffix, is_prefix=True):
    pattern = f"({re.escape(p)})+"  # Match p repeated as many times as possible
    match = re.search(pattern, s)  # Find the first occurrence

    if match:
        before = s[:match.start()]  # Everything before the match
        after = s[match.end():]  # Everything after the match
        return before, after
    else:
        num_chars = len(original_prefix_suffix)
        if is_prefix:
        # split off existing prefix
            if s[-num_chars:] == original_prefix_suffix:
                return s[-num_chars:], s[:-num_chars]
            else: return "", ""
        else:
            if s[:num_chars] == original_prefix_suffix:
                return s[:num_chars], s[num_chars:]
            else: return "", ""
        

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
                print(f"to_test: {p}:{term}:{s}")
                if right_piece[0] != left_piece[-1]:
                    print(f"left: {left_piece}")
                    print(f"right: {right_piece}")
                    candidates = []
                    # p1: oo -> o
                    p1 = right_piece[1:]
                    candidates.append(remove_first_pn(p1, term, s))
                    # s1: xx -> xo
                    s1 = left_piece[:-1] + right_piece[0]
                    candidates.append(remove_first_pn(s1, term, p, False))
                    # p2: oo -> xo
                    p2 = left_piece[-1] + right_piece[1:]
                    candidates.append(remove_first_pn(p2, term, s))
                    # s2: xx -> x
                    s2 = left_piece[:-1]
                    candidates.append(remove_first_pn(s2, term, p, False))
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
    if depth > 4:
        return prefixes, suffixes
    prefixes, suffixes = find_patterns(term, prefixes, suffixes, depth)
    return prefixes, suffixes

find_patterns("xo", [""], [""])
#print(remove_first_pn("ooxoxoo", "ox"))