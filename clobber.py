from mcts import Node, MCTS
import proof_number as pn
import string
from PrettyPrint import PrettyPrintTree

class Player:
    def __init__(self, id, width, height, first):
        self.id = id
        self.first = first
        self.pieces = self.init_pieces(width, height)

    def init_pieces(self, width, height):
        if self.first:
            pieces = [(x, y) for x in range(width) for y in range(height) if (x + y) % 2 == 0]
        else:
            pieces = [(x, y) for x in range(width) for y in range(height) if (x + y) % 2 == 1]
        return pieces

class Board:
    def __init__(self, width, height, players):
        self.width = width
        self.height = height
        self.player_1 = players[0]
        self.player_2 = players[1]

    def __str__(self):
        result = ["  "]
        alphabet = list("abcdefghijklmnopqrstuvwxyz")
        result.append(" ".join(alphabet[:self.width]))
        result.append('\n')
        for y in range(self.height):
            result.append(f"{y + 1} ")
            for x in range(self.width):
                if (x, y) in self.player_1.pieces:
                    result.append(f'{self.player_1.id}')
                elif (x, y) in self.player_2.pieces:
                    result.append(f'{self.player_2.id}')
                else:
                    result.append('.')
                result.append(' ')
            result.append('\n')
        return ''.join(result)
    
    def check_validity(self, game_player, oppo, coord, destination):
        if coord not in game_player.pieces:
            return (False, "Cannot move requested piece")
        if destination[0] < 0 or destination[1] < 0:
            return (False, "Cannot move off of board")
        if destination[0] >= self.width or destination[1] >= self.height:
            return (False, "Cannot move off of board")
        # if destination is not opponent color, return 
        if destination not in oppo.pieces:
            return (False, "Cannot move to requested square")
        return (True, "No error")
    
    def move(self, player, coord, dir):
        game_player = None 
        if player == self.player_1.id:
            game_player = self.player_1
            oppo = self.player_2
        if player == self.player_2.id:
            game_player = self.player_2
            oppo = self.player_1
        if not game_player:
            return(f"{player} is not a piece.")
        
        directions = {"n": (0, -1),
                      "e": (1, 0),
                      "s": (0, 1),
                      "w": (-1, 0)}
        destination = tuple(sum(t) for t in zip(coord, directions[dir]))
        valid, error = self.check_validity(game_player, oppo, coord, destination)
        if valid:
            # remove piece from coord and add piece of opposite color to destination
            game_player.pieces.remove(coord)
            game_player.pieces.append(destination)
            oppo.pieces.remove(destination)
            
            return (valid, error)
        else:
            return (valid, error)
        
    def move_destination(self, origin, destination):
        valid, error = self.check_validity(origin, destination)
        if valid:
            # remove piece from coord and add piece of opposite color to destination
            self.player.pieces.remove(origin)
            self.player.pieces.append(destination)
            self.opponent.pieces.remove(destination)
            
            self.player, self.opponent = self.opponent, self.player
            return error
        else:
            return error

def game_loop():
    node_label = lambda x: f"player: {x.player}\npn: {x.proof_number}\ndpn: {x.disproof_number}"
    pt = PrettyPrintTree(lambda x: x.children, node_label, lambda x: x.label)
    commands = [
        "quit",
        "size",
        "play",
        "show",
        "pn"
    ]
    print("Known commands:")
    for command in commands:
        print(command)
    player_1 = None
    player_2 = None
    board = None
    while True:
        user = input().split(" ")
        action = user[0]
        if action not in commands:
            print("Lo siento, no comprendo.")
            continue
        if action == "quit":
            print("Goodbye :)")
            return
        if action == "size":
            try:
                args = user[1].split("x")
                width = int(args[0])
                height = int(args[1])
                player_1 = Player("o", width, height, True) 
                player_2 = Player("x", width, height, False) 
                board = Board(width, height, [player_1, player_2])
                print(board.__str__())
            except:
                print("Unknown argument.")
                continue
        if action == "show":
            if board == None:
                print("Please provide board size.")
                continue
            print(board.__str__())
        if action == "play":
            if board == None:
                print("Please provide board size.")
                continue
            if len(user) != 4:
                print("Incorrect args.")
                continue
            try:
                player = user[1]
                piece = list(user[2])
                direction = user[3]
                col = string.ascii_lowercase.index(piece[0])
                row = int(piece[1]) - 1
                success, result = board.move(player, (col, row), direction)
                if not success:
                    print(result)
                print(board.__str__())
            except:
                print("Unknown argument.")
                continue
        if action == "pn":
            if len(user) <= 1:
                print("Please provide a player.")
                continue
            if user[1] not in ["x", "o"]:
                print("Unknown player.")
                continue
            player = []
            if user[1] == "o":
                player_pieces = board.player_1.pieces
                oppo_pieces = board.player_2.pieces
            else:
                player_pieces = board.player_2.pieces
                oppo_pieces = board.player_1.pieces
            root = pn.Node("root", "or", None, player_pieces, oppo_pieces, [])
            pt(root)
            print("-" * 100)
            pns = pn.PNSearch()
            while True:
                to_expand = pns.select(root)
                pns.expand(to_expand)
                if root.proof_number == 0 or root.disproof_number == 0:
                    break
            best_node = pns.get_best(root)
            print(best_node.label)
            print(best_node.parent_move)
            print(best_node.proof_number)
            print(best_node.disproof_number)


game_loop()
        
'''width = 8
height = 1

player_1 = Player("o", width, height, True) 
player_2 = Player("x", width, height, False) 

b = Board(width, height, [player_1, player_2])

mcts = MCTS()

while True:
    print(b.__str__())
    info = list(input("Column, row, direction?\n"))
    print(info)
    x = int(info[0]) - 1
    y = int(info[1]) - 1
    direction = info[2]
    #y = int(input("Row?\n"))
    #direction = input("Where to?\n")
    result = b.move((x, y), direction)
    print(result)
    
    print(b.__str__())
    root = Node(b.player.pieces, b.opponent.pieces, False)
    counter = 0

    while counter < 300:
        to_expand = mcts.selection(root)
        to_simulate = mcts.expansion(to_expand)
        result, outcome = mcts.simulation(to_simulate)
        mcts.backpropagation(result, outcome)
        counter += 1
    
    origin, destination = mcts.get_best_move(root)
    b.move_destination(origin, destination)

    


    '''