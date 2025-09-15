import pytest
import pg

@pytest.mark.parametrize("string, term, expected", [
    ("xoxo", "xo", ("", "")),
    ("xyz", "abc", None),
    ("abcxyz", "abc", ("", "xyz")),
    ("abcabcxyz", "abc", ("", "xyz")),
    ("abcxyzabc", "abc", ("", "xyzabc")),
    ("", "abc", None),
    ("abc", "", ("", "abc")),
    ("aaaaa", "aa", ("", "a")),
    ("aaa", "a", ("", "")),
    ("xxoxoxo", "ox", ("xx", "o")),
    ("", "", ("", ""))
])
def test_remove_repeating_term(string, term, expected):
    assert pg.remove_repeating_term(string, term) == expected

@pytest.mark.parametrize("term, prefixes, suffixes, expected", [
    ("ox", ["x", "o", ""], [""], [["x", "ox", "ox", "ox", ""], ["o", "ox", "ox", "ox", ""], ["", "ox", "ox", "ox", ""]])
])
def test_generate_games(term, prefixes, suffixes, expected):
    assert pg.generate_games(term, prefixes, suffixes) == expected
    
@pytest.mark.parametrize("pattern, index, expected", [
    ("oxoxox", 0, ([None, ("", "ooxox")], "o")),
    ("oxoxox", -1, ([None, None], None)),
    ("oxoxox", 6, ([None, None], None)),
    ("oxoxox", 5, ([("oxoxx", ""), None], "x")),
    ("oxoxox", 2, ([("oo", "xox"), ("ox", "oox")], "o")),
    ("", 0, ([None, None], None)),
    ("ox", 0, ([None, ("", "o")], "o"))
])
def test_make_move(pattern, index, expected):
    assert pg.make_move(pattern, index) == expected

@pytest.mark.parametrize("position, term, expected", [
    ("oxox", "ox", ("", "", None, "_")),
    ("ooxx", "ox", ("o", "x", None, "o_x")),
    ("xx", "ox", (None, None, "xx", "xx")),
    ("", "", (None, None, None, None)),
    ("o", "ox", (None, None, "o", "o")),
    ("x", "ox", (None, None, "x", "x")),
    ("", "ox", (None, None, None, None))
])
def test_reduce_position(position, term, expected):
    assert pg.reduce_position(position, term) == expected

@pytest.mark.parametrize("positions, term, expected", [
    (("oxo", "xx"), "ox", ([""], ["o"], ["xx"], ("_o", "xx")))
])
def test_evaluate_positions(positions, term, expected):
    assert len(pg.evaluate_positions(positions, term)) == len(expected)
    for result, target in zip(pg.evaluate_positions(positions, term), expected):
        assert set(result) == set(target)

#TODO: is it reasonable to consider "" as a small position?
@pytest.mark.parametrize("pattern_string, term, expected", [
    (
        # pattern_string
        "oxoxox", 
        # repeating term
        "ox", 
        # results
        (
            # prefixes
            ["", "o", "xx", "x"], 
            # suffixes
            ["", "x", "o", "oo"], 
            # small
            ["o", "oo", "xx", "x"], 
            # reduced children from x move
            [
                ("_", "x"),
                ("o", "xx_"),
                ("_", "_x"),
                ("_o", "xx"),
                ("_x",)
            ],
            # reduced children from o move
            [
                ("o_",),
                ("oo", "x_"),
                ("_", "o_"),
                ("_oo", "x"),
                ("_", "o")
            ]
        )
    ),
    (
        # pattern_string
        "ox", 
        # repeating term
        "ox", 
        # results
        (
            # prefixes
            [], 
            # suffixes
            [], 
            # small
            ["o", "x"], 
            # reduced children from x move
            [("x", )],
            # reduced children from o move
            [("o", )]
        )
    ),
    # no legal moves
    (
        # pattern_string
        "xxx", 
        # repeating term
        "ox", 
        # results
        (
            # prefixes
            [], 
            # suffixes
            [], 
            # small
            [], 
            # reduced children from x move
            [],
            # reduced children from o move
            []
        )
    )
])
def test_evaluate_pattern(pattern_string, term, expected):
    assert len(pg.evaluate_pattern(pattern_string, term)) == len(expected)
    for result, target in zip(pg.evaluate_pattern(pattern_string, term), expected):
        assert set(result) == set(target)

@pytest.mark.parametrize("term, prefixes, suffixes", [
    ("ox", ['', 'o', 'x', 'xx'], ['', 'o', 'oo', 'x'])
])
def test_generate_symmetries(term, prefixes, suffixes):
    results = pg.generate_symmetries(term, prefixes, suffixes)
    for k, v in results.items():
        reversed_pattern = (k[0] + term + term + term + k[1])[::-1]
        assert pg.remove_repeating_term(reversed_pattern, term) == v

@pytest.mark.parametrize("symmetries, children, expected", [
    (
        {
            ('', 'o'): ('', 'o'),
            ('', 'oo'): ('o', 'o'),
            ('o', 'oo'): ('o', 'oo'),
            ('x', ''): ('x', ''),
            ('x', 'o'): ('', ''),
            ('x', 'oo'): ('o', ''),
            ('x', 'x'): ('xx', ''),
            ('xx', 'o'): ('', 'x'),
            ('xx', 'oo'): ('o', 'x'),
            ('xx', 'x'): ('xx', 'x'),
            ('o',): ('o',),
            ('oo',): ('oo',),
            ('ooo',): ('ooo',),
            ('x',): ('x',),
            ('xo',): ('', ''),
            ('xoo',): ('o', ''),
            ('xx',): ('xx',),
            ('xxo',): ('', 'x'),
            ('xxoo',): ('o', 'x'),
            ('xxx',): ('xxx',)
        },
        [
            ('x_oo',),
            ('oo', 'x_'),
            ('o_o', 'x_'),
            ('x_oo', 'xo'),
            ('o_o', 'x'),
            ('o', 'x_o'),
            ('x_o', 'xoo')
        ],
        [
            ('o_',),
            ('oo', 'x_'),
            ('o_o', 'x_'),
            ('o_', '_'),
            ('o_o', 'x'),
            ('o', '_'),
            ('_', 'o_')
        ],
    )
])
def test_replace_symmetries_children(symmetries, children, expected):
    result = pg.replace_symmetries_children(symmetries, children)
    print(result)
    print(expected)
    assert result == expected