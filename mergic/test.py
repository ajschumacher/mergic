import unittest
import mergic


class TestCheck(unittest.TestCase):

    def test_raises_on_duplicate_in_value_list(self):
        with self.assertRaises(ValueError):
            mergic._check({1: [1, 1]})

    def test_raises_on_duplicates_across_keys(self):
        with self.assertRaises(ValueError):
            mergic._check({1: [1], 2: [1]})

    def test_returns_number_of_values(self):
        partition = {1: [1], 2: [2, 3], 3: [4]}
        self.assertEqual(mergic._check(partition), 4)


class TestLinkItems(unittest.TestCase):

    def test_doesnt_change_if_already_together(self):
        group = (1, 2)
        group_of = {1: group, 2: group}
        mergic._link_items(group_of, {(1, 2)}, [(1, 2)])
        self.assertIs(group_of[1], group_of[2])

    def test_joins_to_same_thing(self):
        group_of = {1: (1,), 2: (2,)}
        mergic._link_items(group_of, {(1,), (2,)}, [(1, 2)])
        self.assertIs(group_of[1], group_of[2])
