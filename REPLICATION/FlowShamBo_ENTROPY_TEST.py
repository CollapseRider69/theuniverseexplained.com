import os
import time
import random
import hashlib
import csv
from datetime import datetime

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
import os
import time
import random
import hashlib
import csv
from datetime import datetime

# … your FlowShamBo class definition lives above …

def run_experiment(rounds, output_file="flow.csv"):
    """
    Plays the specified number of rounds, writes each result to CSV,
    and prints the latest row every 15 seconds.
    """
    game = FlowShamBo()
    last_report = time.time()

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "round",
            "type",
            "player",
            "system",
            "outcome",
            "flow_meter",
            "external_timestamp"
        ])
        writer.writeheader()

        for i in range(1, rounds + 1):
            result = game.play_round()

            # capture timestamp once
            external_ts = datetime.now().isoformat()

            writer.writerow({
                "round": i,
                "type":              result["type"],
                "player":            result["player"],
                "system":            result["system"],
                "outcome":           result["outcome"],
                "flow_meter":        result["flow_meter"],
                "external_timestamp": external_ts,
            })
            f.flush()
            os.fsync(f.fileno())

            # every 15 seconds, print the latest row
            now = time.time()
            if now - last_report >= 15:
                print(
                    f"Latest row: round {i}, "
                    f"type {result['type']}, "
                    f"player {result['player']}, "
                    f"system {result['system']}, "
                    f"outcome {result['outcome']}, "
                    f"flow_meter {result['flow_meter']}, "
                    f"external_timestamp {external_ts}"
                )
                last_report = now


if __name__ == "__main__":
    # Prompt user for how many rounds to play
    try:
        rounds = int(input("How many rounds would you like to play? "))
    except ValueError:
        print("Invalid input; defaulting to 1,000,000 rounds.")
        rounds = 1_000_000
    print("TEST RUNNING. Ctrl+Z to quit.")
    run_experiment(rounds)
    print("TEST COMPLETE")
