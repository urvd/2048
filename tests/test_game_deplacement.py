import os
import sys
import unittest
from copy import copy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_deplacement import (  # noqa: E402
    DownActionImpl,
    LeftActionImpl,
    RightActionImpl,
    UpActionImpl,
)


def make_states(values):
    return {(x, y): values[y][x] for y in range(4) for x in range(4)}


def apply_action(action_class, values):
    states = make_states(values)
    action = action_class(current_states=copy(states), lenght=4)
    return action.get_states(), action.get_score()


class GameDeplacementTest(unittest.TestCase):
    def assert_states(self, actual, expected):
        expected_states = make_states(expected)
        self.assertEqual(actual, expected_states)

    def test_left_moves_and_merges(self):
        actual, score = apply_action(
            LeftActionImpl,
            [
                [2, 0, 2, 0],
                [4, 4, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        )

        self.assert_states(
            actual,
            [
                [4, 0, 0, 0],
                [8, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        )
        self.assertEqual(score, 12)

    def test_right_moves_and_merges(self):
        actual, score = apply_action(
            RightActionImpl,
            [
                [2, 0, 2, 0],
                [4, 4, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        )

        self.assert_states(
            actual,
            [
                [0, 0, 0, 4],
                [0, 0, 0, 8],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        )
        self.assertEqual(score, 12)

    def test_up_moves_and_merges(self):
        actual, score = apply_action(
            UpActionImpl,
            [
                [2, 0, 0, 0],
                [2, 0, 0, 0],
                [4, 0, 0, 0],
                [4, 0, 0, 0],
            ],
        )

        self.assert_states(
            actual,
            [
                [4, 0, 0, 0],
                [8, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
            ],
        )
        self.assertEqual(score, 12)

    def test_down_moves_and_merges(self):
        actual, score = apply_action(
            DownActionImpl,
            [
                [2, 0, 0, 0],
                [2, 0, 0, 0],
                [4, 0, 0, 0],
                [4, 0, 0, 0],
            ],
        )

        self.assert_states(
            actual,
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [4, 0, 0, 0],
                [8, 0, 0, 0],
            ],
        )
        self.assertEqual(score, 12)


if __name__ == "__main__":
    unittest.main()
