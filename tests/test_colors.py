import unittest
from server.colors import random_color, color, USER_COLORS, RESET

class TestColors(unittest.TestCase):
    def test_random_color_is_from_pool(self):
        self.assertIn(random_color(), USER_COLORS)

    def test_color_wraps_text_and_resets(self):
        code = USER_COLORS[0]
        out = color("hello", code)
        self.assertTrue(out.startswith(code))
        self.assertTrue(out.endswith(RESET))

if __name__ == "__main__":
    unittest.main()