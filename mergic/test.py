import mergic
import unittest


class TestCheck(unittest.TestCase):

    def test_raises_on_duplicate_in_value_list(self):
        with self.assertRaises(ValueError):
            mergic.check({1: [1, 1]})

    def test_raises_on_duplicates_across_keys(self):
        with self.assertRaises(ValueError):
            mergic.check({1: [1], 2: [1]})

    def test_returns_number_of_values(self):
        partition = {1: [1], 2: [2, 3], 3: [4]}
        self.assertEqual(mergic.check(partition), 4)


class TestLinkItems(unittest.TestCase):

    def test_doesnt_change_if_already_together(self):
        group = (1, 2)
        group_of = {1: group, 2: group}
        mergic.link_items(group_of, [(1, 2)])
        self.assertIs(group_of[1], group_of[2])

    def test_joins_to_same_thing(self):
        group_of = {1: (1,), 2: (2,)}
        mergic.link_items(group_of, [(1, 2)])
        self.assertIs(group_of[1], group_of[2])

    def test_joins_to_correct_tuple(self):
        group_of = {1: (1,), 2: (2,)}
        mergic.link_items(group_of, [(1, 2)])
        self.assertEqual(set(group_of[1]), set((1, 2)))


class TestDiff(unittest.TestCase):

    def test_no_diff_when_same(self):
        self.assertEqual(mergic.diff({1: [1]}, {1: [1]}), {})

    def test_order_doesnt_matter(self):
        self.assertEqual(mergic.diff({1: [1, 2]}, {1: [2, 1]}), {})

    def test_raises_when_first_doesnt_assign(self):
        with self.assertRaises(ValueError):
            mergic.diff({1: [1]}, {1: [1, 2]})

    def test_raises_when_second_doesnt_assign(self):
        with self.assertRaises(ValueError):
            mergic.diff({1: [1, 2]}, {1: [1]})

    def test_renaming_key_picked_up(self):
        self.assertEqual(mergic.diff({1: [1]}, {2: [1]}), {2: [1]})

    def test_splitting_value_picked_up(self):
        self.assertEqual(mergic.diff({1: [1, 2], 3: [3]},
                                     {1: [1], 2: [2], 3: [3]}),
                         {1: [1], 2: [2]})


class TestEqual(unittest.TestCase):

    def test_equal_if_empty(self):
        self.assertTrue(mergic.equal({}, {}))

    def test_not_equal_if_one_not_empty(self):
        self.assertFalse(mergic.equal({}, {1: [1]}))

    def test_raises_on_string_nonsense(self):
        with self.assertRaises(AttributeError):
            mergic.equal('non', 'sense')

    def test_order_doesnt_matter_for_equality(self):
        self.assertTrue(mergic.equal({1: [1, 2]}, {1: [2, 1]}))

    def test_not_equal_if_key_different(self):
        self.assertFalse(mergic.equal({1: [1]}, {2: [1]}))

    def test_not_equal_if_value_different(self):
        self.assertFalse(mergic.equal({1: [1]}, {1: [2]}))

    def test_not_equal_if_value_moves(self):
        self.assertFalse(mergic.equal({1: [1, 2], 2: [3]},
                                      {1: [1], 2: [2, 3]}))

    def test_slightly_interesting_equality(self):
        self.assertTrue(mergic.equal({1: [1, 2, 3], 2: ['a']},
                                     {2: ['a'], 1: [3, 2, 1]}))


class TestTable(unittest.TestCase):

    def test_nothing_for_empty(self):
        self.assertEqual(len(list(mergic.table({}))), 0)

    def test_right_number_of_rows(self):
        p = {1: [2, 3], 'b': [4, 5, 6]}
        self.assertEqual(len(list(mergic.table(p))), 5)

    def test_correct_rows_appear(self):
        p = {1: [2, 3], 'b': [4, 5, 6]}
        rowset = set([(2, 1), (3, 1), (4, 'b'), (5, 'b'), (6, 'b')])
        self.assertEqual(set(mergic.table(p)), rowset)


if __name__ == '__main__':
    unittest.main()
