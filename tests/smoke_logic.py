"""Smoke test of the game logic (no display needed)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environnement import Environment  # noqa: E402
from agent import Agent  # noqa: E402

for size in (3, 4, 5):
    agent = Agent(Environment(size))
    agent.do(init=True)
    for _ in range(200):
        if not agent.continue_game():
            break
        agent.do()
    print(f"taille {size}: score {agent.state_score}")
print("SMOKE_OK")
