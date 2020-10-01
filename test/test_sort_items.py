import dbex.lib.sort_items as sorter
import unittest
import os

sort = sorter.sorter


class TestSortItems(unittest.TestCase):
    test_file = "dbex/test/test_tests.dbex"

    def setUp(self):
        with open(self.test_file, "w+") as file:
            file.write("")

    def tearDown(self):
        os.remove(self.test_file)

    def test_None(self):
        tester = None
        result = sort(tester)

        self.assertEqual(result, tester)

    def test_normal(self):
        correct_result = {"a": 1, "b": 3, "c": 2}
        tester = {"a": 1, "c": 2, "b": 3}
        result = sort(tester)

        self.assertEqual(result, correct_result)

    def test_inside_list(self):
        correct_result = [{"a": 1, "b": 3, "c": 2}, {"a": 4, "b": 6, "c": 5}]
        tester = [{"a": 1, "c": 2, "b": 3}, {"a": 4, "c": 5, "b": 6}]
        result = sort(tester)

        self.assertEqual(result, correct_result)