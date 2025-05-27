import proof_number as pn
from clobber import Board, Player
import pg
from pprint import pp

def generate_positions():
    prefixes = ["", "x", "o", "xx"]
    suffixes = ["", "x", "o", "oo"]
    positions = {}
    for p in prefixes:
        for s in suffixes:
            copies = []
            for n in range(1, 8):
                copies.append(f"{p}{"ox" * n}{s}")
            positions[f"{p}_{s}"] = copies
    return positions

def check_win_loss(game):
    position = list(game)
    width = len(position)
    height = 1

    player_1 = Player("o", width, height, True, position=[position]) 
    player_2 = Player("x", width, height, False, position=[position]) 
    board = Board(width, height, [player_1, player_2])
    #print(board.__str__())

    o_first_root = pn.Node("root", "or", None, player_1.pieces, player_2.pieces, [])
    x_first_root = pn.Node("root", "or", None, player_2.pieces, player_1.pieces, [])

    pns = pn.PNSearch()

    # outcome = [o_first {true: win, false: loss}, x_first {true: win, false: loss}]
    # for example, if the first player always loses, then outcome = [false, false]
    # if o always wins, then outcome = [true, false]
    # possible outcomes: 
    #   [true, true] <- first player win (fuzzy) <- 11
    #   [false, false] <- second player win (zero) <- 00
    #   [true, false] <- o win (positive) <- 10
    #   [false, true] <- x win (negative) <- 01
    outcome = ""
    for root in [o_first_root, x_first_root]:
        while True:
            to_expand = pns.select(root)
            # check if to_expand exists in the transposition table
            # normally, we expand to_expand and assign pn, dpn to each of its children
            # we then update to_expand according to the values of its children <-- self.backpropagate()
            # if a position's value is already known, then we skip this entire process and just backpropagate from that node's parent?
            if pns.look_up(to_expand):
                pns.update(to_expand)
            else:
                pns.expand(to_expand)
            if root.proof_number == 0 or root.disproof_number == 0:
                break
        best_node = pns.get_best(root)
        if best_node.proof_number == 0:
            outcome += "1"
        elif best_node.disproof_number == 0:
            outcome += "0"
    
    outcomes = [
        "zero",
        "negative",
        "positive",
        "fuzzy"
    ]
    return outcomes[int(outcome, 2)]

def write_to_file(filename):
    positions = generate_positions()

    with open(f'{filename}.txt', 'w') as f:
        for label, position in positions.items():
            f.write(label)
            f.write("\n")
            for game in position:
                outcome = check_win_loss(game)
                f.write(f"{game}: {outcome}")
                f.write("\n")
            f.write("\n")

def prover(hypotheses, trees, memo, errors):
    '''The idea here is as follows:
    1. Provide as input the inductive assumptions for every possible prefix/suffix pair. 
        E.g. [p](xo)^n[s] has some score s(n) for sufficiently large n. 
    2. Iterate over all trees representing the possible child positions for each p/s pair. 
        E.g. We might start with the tree (xo)^n --> (xo)^i, (xo)^jo.
            a. We memoize (xo)^n ["this is a first player win"]
            b. Look at the children: (xo)^i has been memoized! We apply our IH.
                                     (xo)^jo has NOT been memoized. Memoize it.
            c. Search the tree for (xo)^jo.
    3. Keep recursively searching trees until we can apply IH for all children. Add the child 
        values to obtain the parent value. Once a tree is resolved, search remaining 
        binary trees with the same root.
    4. Combine the results of the binary trees according to which player moved.

    hypotheses: dict of all possible reachable positions and their corresponding value
    trees: dict with every possible position as a key, and corresponding subpositions as values
        e.g. {
            'x_o': [['x_', 'x_o'],
                    ['_', '_o'],
                    ['oo_o', 'x_x'],
                    ['o_o', 'x_xx'],
                    ['_', 'x_'],
                    ['_o', 'x_o']]
        }
    memo: an empty list to contain all positions that have been searched
    errors: any position that hasn't been memoized?
    '''
    proven = {}

    # internal recursive function to act on each entry in trees
    # takes a position (e.g. x_o) as input
    def evaluate(position):
        # memoize position (we've now seen it)
        memo.append(position)
        # get the list of positions corresponding to a move from the input position
        try:
            children = trees[position]
        # if these don't exist (i.e. a position has no children), append them to errors
        except:
            errors.append(position)
            children = []
        # iterate over all child positions (typically two positional types per move)
        for child in children:
            # check each of these two positions
            for move in child:
                # if we've seen the move, add it to the set of proven moves
                if move in memo:
                    # this is the line that applies the induction hypothesis to the move
                    proven[move] = hypotheses[move]
                    continue
                # otherwise evaluate it recursively
                else:
                    evaluate(move)

    for position in trees.keys():
        print(position)
        evaluate(position)

    return proven, errors

pattern = "ox"

# trees is every possible set of two position types reachable by a move from a given position type
# e.g. [..., {'_': ['_x', 'x_']}, ...]
prefixes, suffixes, small, trees = pg.find_patterns(pattern, [""], [""], [], {}, 0)
print(prefixes)
print(suffixes)
print(small)
pp(trees)

# dict matching pairs (prefix, suffix) to pairs (prefix, suffix) that correspond to symmetric games
# e.g. ('', ''): ('o', 'xx') --> xxoxxo: oxxoxxoxx --> xxoxxoxxo --> _
# TODO: Include small positions in this dict
symmetries = pg.find_symmetries(pattern, prefixes, suffixes)
small_symmetries = pg.find_symmetries_small(pattern, prefixes, suffixes, small)

# removes duplicated entries in symmetries dict (i.e. ('', ''): ('o', 'xx') and ('o', 'xx'): ('', ''))
# sets keys to be the larger prefix-suffix pair in dict
consolidated_symmetries = pg.consolidate_symmetries_dict(symmetries)

print("################------------ SYMMETRIES ----------------##############")
pp(consolidated_symmetries)
pp(small_symmetries)
all_syms = consolidated_symmetries | small_symmetries
pp(all_syms)

# restructures trees to dict and removes trees that are the longer symmetric pair
# e.g. {
#   'x_o': [
#       ['x_o', 'x_x'],
#       ['_', '_o'],
#       ['oxo_o', 'x_xx'],
#       ['x_xxx', 'xo_o'],
#       ['_o', 'x_xo']
#   ],
#       }
consolidated_tree = pg.consolidate_trees(trees['x'], all_syms)
pp(consolidated_tree)

# all this hypotheses shit is just to test the prover
hypotheses = {
    '_': "pos",
    '_o': "pos",
    'oo_': "pos",
    'x_': "pos",
    'x_x': "pos",
    'x_o': "pos"
}
keys = list(set(pg.restructure_trees(trees).keys()))
hypotheses = {}
for k in keys:
    hypotheses[k] = []
for s in small:
    hypotheses[s] = []

#pp(consolidated_tree)
print("___________________________________________")
#pp(pg.restructure_trees(trees))
test, errors = prover(hypotheses, pg.restructure_trees(trees), [], [])
pp(f"hypotheses: {hypotheses}")
print(test.keys())
print(errors)
print(small)