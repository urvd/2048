"""Smoke test of the game logic (no display needed)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Le smoke test fait jouer l'IA : sans le mode apprentissage, aucun coup n'est joué
os.environ["MODE_APPRENTISSAGE"] = "true"

from environnement import Environment  # noqa: E402
from agent import Agent  # noqa: E402

environment = Environment(3)
environment.states = {
    (row, col): 2 if (row + col) % 2 == 0 else 4
    for row in range(3)
    for col in range(3)
}
assert environment.evaluate_when_game_over()

environment.states[(0, 1)] = 2
assert not environment.evaluate_when_game_over()

for size in (3, 4, 5):
    agent = Agent(Environment(size))
    agent.do(init=True)
    for _ in range(200):
        if not agent.continue_game():
            break
        agent.do()
    print(f"taille {size}: score {agent.state_score}")
    assert agent.state_score > 0, "l'IA n'a marqué aucun point"
print("SMOKE_OK")
