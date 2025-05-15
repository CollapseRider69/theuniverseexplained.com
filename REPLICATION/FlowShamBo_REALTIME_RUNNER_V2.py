import os

import time
import random
import hashlib
import csv

class FlowShamBo:
    def __init__(self):
        self.choices = ["rock", "paper", "scissors"]
        self.flow_meter = 0
        self.dummy_probability = 0.5

    def zen_rng(self):
        start_state = random.choice([0, 1, 2])
        frequency = 30 + (30 * random.uniform(-0.01, 0.01))  # 30Hz ±1%
        wobble = frequency * random.uniform(-0.02, 0.02)     # ±2% wobble
        frequency += wobble
        seed_input = f"{time.time_ns()}{start_state}{frequency}"
        hashed_seed = int(hashlib.sha256(seed_input.encode()).hexdigest(), 16)
        random.seed(hashed_seed)
        return random.choice([0, 1, 2])

    def determine_outcome(self, player, system):
        if player == system:
            return "tie"
        elif (player == 0 and system == 2) or              (player == 1 and system == 0) or              (player == 2 and system == 1):
            return "win"
        else:
            return "lose"

    def play_round(self):
        player_choice = random.choice([0, 1, 2])
        timing_jitter = random.uniform(0.001, 0.05)

        is_dummy = random.random() < self.dummy_probability

        if is_dummy:
            # DUMMY:
            system_choice = self.zen_rng()
            time.sleep(0.023)
            time.sleep(timing_jitter)
            time.sleep(0.025)
        else:
            # LIVE:
            time.sleep(0.025)
            time.sleep(timing_jitter)
            system_choice = self.zen_rng()
            time.sleep(0.025)

        outcome = self.determine_outcome(player_choice, system_choice)

        if outcome == "win":
            self.flow_meter += 1
        elif outcome == "lose":
            self.flow_meter -= 1

        return {
            "type": "dummy" if is_dummy else "live",
            "player": player_choice,
            "system": system_choice,
            "outcome": outcome,
            "flow_meter": self.flow_meter
        }

# Configurable batch runner
def run_experiment(rounds, output_file="FlowShamBo_REALTIME_RESULTS_V2.csv"):
    game = FlowShamBo()
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["round", "type", "player", "system", "outcome", "flow_meter"])
        writer.writeheader()
        for i in range(1, rounds + 1):
            result = game.play_round()
            writer.writerow({
                "round": i,
                "type": result["type"],
                "player": result["player"],
                "system": result["system"],
                "outcome": result["outcome"],
                "flow_meter": result["flow_meter"]
            })
            f.flush()
            os.fsync(f.fileno())

if __name__ == "__main__":
    run_experiment(rounds=10000000)  # ← Set number of rounds here for replication
