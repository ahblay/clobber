import random
import math

width = 3
height = 3

class Node:
    def __init__(self, player, opponent, player_one, parent=None, parent_move=[]):
        self.player = player
        self.opponent = opponent
        self.children = []
        self.parent = parent
        self.n = 0
        self.w = 0
        self.player_one = player_one
        self.visited = False
        self.parent_move = parent_move

    def __str__(self):
        global width
        global height
        result = []
        if self.player_one:
            player_piece = 'o'
            opponent_piece = 'x'
        else:
            player_piece = 'x'
            opponent_piece = 'o'
        for y in range(height):
            for x in range(width):
                if (x, y) in self.player:
                    result.append(f'{player_piece}')
                elif (x, y) in self.opponent:
                    result.append(f'{opponent_piece}')
                else:
                    result.append('.')
                result.append(' ')
            result.append('\n')
        return ''.join(result)

class MCTS:
    def __init__(self):
        pass

    def get_best_move(self, position):
        best_score = 0
        best_position = None
        for child in position.children:
            if child.n == 0:
                continue
            score = child.w / child.n
            if score >= best_score:
                best_position = child
                best_score = score
        print(best_score)
        return best_position.parent_move

    def available_moves(self, p1, p2):
        moves = []
        neighbors = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        for piece in p1:
            for neighbor in neighbors:
                cell = tuple(sum(t) for t in zip(piece, neighbor))
                if cell in p2:
                    moves.append([piece, cell])
        return moves

    def make_move(self, p1, p2, move):
        p1.remove(move[0])
        p1.append(move[1])
        p2.remove(move[1])
        return p1, p2
    
    def rollout_policy(self, moves):
        # get random entry from moves
        return random.choice(moves)

    def selection(self, node):
        #print(node.__str__())
        best_score = 0
        best_node = None
        if not node.children:
            return node
        visited_children = [child for child in node.children if child.visited]
        #print(visited_children)
        if not visited_children:
            return node
        for child in visited_children:
            #print(self.uct(child))
            #print(best_score)
            if self.uct(child) >= best_score:
                best_node = child
        return self.selection(best_node)
    
    def expansion(self, node):
        moves = self.available_moves(node.player, node.opponent)
        if not moves:
            return node
        # for each move, create a child node representing the corresponding
        # game state after that move is made
        for move in moves:
            #print(move)
            #print(node.player)
            #print(node.opponent)
            player, opponent = self.make_move(node.player.copy(), node.opponent.copy(), move)
            child = Node(opponent, player, not(node.player_one), parent=node, parent_move=move)
            node.children.append(child)
        # return a randomly selected child node
        random_leaf = random.choice(node.children)
        random_leaf.visited = True
        return random_leaf

    def simulation(self, node):
        moves = self.available_moves(node.player, node.opponent)
        # randomly play out game 
        # for each step of the playout, add child nodes along the game tree
        if not moves:
            result = 0
            if node.player_one:
                result = 0
            else:
                result = 1
            return node, result
        move = self.rollout_policy(moves)
        player, opponent = self.make_move(node.player.copy(), node.opponent.copy(), move)
        child = Node(opponent, player, not(node.player_one), parent=node, parent_move=move)
        node.children.append(child)
        return self.simulation(child)

    def backpropagation(self, node, result):
        # backtrack up game tree, recording n and w for each node back to the root
        node.n += 1
        node.w += result
        while node.parent:
            print(node.__str__())
            print(f'w: {node.w}')
            print(f'n: {node.n}')
            result = (result + 1) % 2
            node = node.parent
            node.n += 1
            node.w += result

    #this SHOULD NOT be negative
    def uct(self, node):
        return (node.w / node.n) + (math.sqrt(2) * math.sqrt(math.log(node.parent.n) / node.n))

'''player = [(x, y) for x in range(width) for y in range(height) if (x + y) % 2 == 0]
opponent = [(x, y) for x in range(width) for y in range(height) if (x + y) % 2 == 1]

root = Node(player, opponent, True)
mcts = MCTS(root)
counter = 0

while counter < 100:
    to_expand = mcts.selection(root)
    to_simulate = mcts.expansion(to_expand)
    result, outcome = mcts.simulation(to_simulate)
    mcts.backpropagation(result, outcome)
    counter += 1

print(mcts.get_best_move(root))'''



'''
def playout(p1, p2, width, height):
    print(test_print(p1, p2, width, height))
    moves = available_moves(p1["pieces"], p2["pieces"])
    if not moves:
        return
    move = rollout_policy(moves)
    print(move)
    p1["pieces"], p2["pieces"] = make_move(p1["pieces"], p2["pieces"], move)
    playout(p2, p1, width, height)

def test_print(p1, p2, width, height):
    result = []
    for y in range(height):
        for x in range(width):
            if (x, y) in p1["pieces"]:
                result.append(f'[{p1["id"]}]')
            elif (x, y) in p2["pieces"]:
                result.append(f'[{p2["id"]}]')
            else:
                result.append('[ ]')
        result.append('\n')
    return ''.join(result)

width = 3
height = 3

p1 = {"id": "O", "pieces": [(x, y) for x in range(width) for y in range(height) if (x + y) % 2 == 0]}
p2 = {"id": "X", "pieces": [(x, y) for x in range(width) for y in range(height) if (x + y) % 2 == 1]}

playout(p1, p2, width, height)
'''