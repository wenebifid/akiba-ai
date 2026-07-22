import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from stable_baselines3 import PPO
from environment.custom_env import AfricanFinanceEnv

model = PPO.load("models/pg/ppo/run1/best_model")
env   = AfricanFinanceEnv(render_mode="human")
clock = pygame.time.Clock()

obs, info = env.reset(seed=42)
print("\nRunning trained PPO agent. Press Q to quit.\n")
print(f"{'Month':>6} {'Action':>22} {'Reward':>8} {'Net Worth':>12} {'Stress':>8}")
print("-" * 62)

for step in range(60):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(int(action))
    env.render()
    clock.tick(4)
    print(f"{step + 1:>6} {AfricanFinanceEnv.ACTION_NAMES[int(action)]:>22} "
          f"{reward:>+8.2f} ${info['net_worth']:>10,.0f} {info['financial_stress']:>7.2%}")
    if terminated or truncated:
        break

print(f"\nFinal net worth: ${info['net_worth']:,.0f}")
time.sleep(3)
env.close()