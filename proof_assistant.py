import proof_number as pn
from clobber import Board, Player

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

positions = generate_positions()

with open('base_cases.txt', 'w') as f:
    for label, position in positions.items():
        f.write(label)
        f.write("\n")
        for game in position:
            outcome = check_win_loss(game)
            f.write(f"{game}: {outcome}")
            f.write("\n")
        f.write("\n")