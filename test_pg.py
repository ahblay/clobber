import pytest
import pg

@pytest.mark.parametrize("string, term, expected", [
    ("xyz", "abc", None),
    ("abcxyz", "abc", ("", "xyz")),
    ("abcabcxyz", "abc", ("", "xyz")),
    ("abcxyzabc", "abc", ("", "xyzabc")),
    ("", "abc", None),
    ("abc", "", ("", "abc")),
    ("aaaaa", "aa", ("", "a")),
    ("aaa", "a", ("", "")),
    ("xxoxoxo", "ox", ("xx", "o"))
])
def test_remove_repeating_term(string, term, expected):
    assert pg.remove_repeating_term(string, term) == expected