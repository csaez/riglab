import unittest
from riglab import naming as n


class NamingTests(unittest.TestCase):

    def test_get_tokens(self):
        n.clear_tokens()
        self.assertEqual(len(n.get_tokens()), 0)

    def test_add_tokens(self):
        n.clear_tokens()
        self.assertTrue(n.new_token("name", "value1"))
        self.assertFalse(n.new_token("name", "value2"))
        self.assertEqual(len(n.get_tokens()), 1)
        self.assertEqual(n.get_tokens(), ["name"])

    def test_get_token(self):
        n.clear_tokens()
        n.new_token("name", "value")
        self.assertEqual(n.get_token("name"), "value")
        self.assertIsNone(n.get_token("foo"))

    def test_delete_token(self):
        n.clear_tokens()
        self.assertFalse(n.delete_token("foo"))
        n.new_token("foo", "bar")
        self.assertTrue(n.delete_token("foo"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
