import unittest

from util import checkEmptyInfo


class CheckEmptyInfoTests(unittest.TestCase):
    def test_returns_none_for_empty_values(self):
        self.assertEqual(checkEmptyInfo(""), "None")
        self.assertEqual(checkEmptyInfo("   "), "None")
        self.assertEqual(checkEmptyInfo(None), "None")

    def test_returns_original_value_for_non_empty_values(self):
        self.assertEqual(checkEmptyInfo("Shelf A"), "Shelf A")
        self.assertEqual(checkEmptyInfo("  Note "), "Note")


if __name__ == "__main__":
    unittest.main()
