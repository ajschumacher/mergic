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
