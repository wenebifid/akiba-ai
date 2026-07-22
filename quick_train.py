import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.callbacks import EvalCallback
from environment.custom_env import AfricanFinanceEnv


def make_env(seed=0):
    def _init():
        env = AfricanFinanceEnv()
        env = Monitor(env)
        env.reset(seed=seed)
        return env
    return _init


print("=" * 55)
print("  Akiba AI — PPO Training")
print("  East Africa calibrated environment")
print("  Income: $20-$120/month | Inflation: ~18%")
print("=" * 55)

os.makedirs("models/pg/ppo/run1", exist_ok=True)
os.makedirs("models/pg",          exist_ok=True)
os.makedirs("results/ppo_logs",   exist_ok=True)

env      = DummyVecEnv([make_env(0)])
eval_env = DummyVecEnv([make_env(99)])

model = PPO(
    "MlpPolicy", env,
    learning_rate = 1e-3,
    gamma         = 0.99,
    n_steps       = 512,
    batch_size    = 64,
    n_epochs      = 10,
    ent_coef      = 0.01,
    clip_range    = 0.2,
    gae_lambda    = 0.95,
    policy_kwargs = dict(net_arch=[128, 128]),
    verbose       = 1,
    seed          = 42,
    tensorboard_log="results/ppo_logs",
)

cb = EvalCallback(
    eval_env,
    best_model_save_path="models/pg/ppo/run1",
    log_path            ="results/ppo_logs",
    eval_freq           = 10_000,
    n_eval_episodes     = 10,
    deterministic       = True,
    verbose             = 1,
)

t0 = time.time()
model.learn(total_timesteps=200_000, callback=cb, progress_bar=True)
elapsed = time.time() - t0

mean_r, std_r = evaluate_policy(model, eval_env, n_eval_episodes=20, deterministic=True)
print(f"\nDone in {elapsed / 60:.1f} min")
print(f"Mean reward: {mean_r:.2f} ± {std_r:.2f}")

model.save("models/pg/ppo/run1/final_model")

with open("models/pg/best_run.json", "w") as f:
    json.dump({"best_run_id": 1, "best_mean_reward": float(mean_r), "algorithm": "PPO"}, f, indent=2)

print("\n✅ Model saved.")
print("   Run the app:  streamlit run app.py")
print("   Run the demo: python demo.py")

env.close()
eval_env.close()