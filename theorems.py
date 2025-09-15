import pg
from pprint import pp

a = [['', 'o']]
a0 = ['o', 'oxo', 'oxoxoxoxo']

b = [['o', 'o']]
b0 = ['oo', 'ooxo']

c = [['o', 'oo']]
c0 = ['ooo', 'ooxoxoo']

d = ['ox', 'oxox', 'ooxo', 'ooxoxo']

e = ['xxo']

y = [['','']]
y0 = ['ox', 'oxox', 'oxoxoxoxoxox']

z = [[['o', '']]]
z0 = ['o', 'oox', 'ooxox']

def get_positions(count_vector, player):
    '''
    for every entry in count_vector:
        consider the position resulting from each possible move by player
        for each of these, determine the corresponding count vector
        e.g. Left makes a move in the first entry 'a' to games in categories 'b' and 'c'
        resulting count vector for this move is (0, 1, 1, 0, 0, 0, 0) + count_vector with entry 'a' decremented by 1
    this loop returns a dict containing count vectors resulting from moves in each component a, b, ..., z
    return this dict
    '''
    pass

trees = {"x": {}, "o": {}}
prefixes, suffixes, small, trees = pg.find_patterns("ox", [""], [""], [], trees, 0)
print(f'prefixes: {prefixes}')
print(f'suffixes: {suffixes}')
print(f'small: {small}')
pp(trees)

symmetries = pg.generate_symmetries("ox", prefixes, suffixes)
print("symmetries")
pp(symmetries)

reduced_symmetries = pg.consolidate_symmetries_dict(symmetries)
print("reduced symmetries")
pp(reduced_symmetries)

small_symmetries = pg.generate_symmetries_small("ox", prefixes, suffixes, small)
print("small symmetries")
pp(small_symmetries)