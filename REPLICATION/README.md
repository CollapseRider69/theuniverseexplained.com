# Replication Tools for FlowShamBo and gPCT Testing

This folder contains all scripts, instructions, and tools required to replicate the experiments and analysis described in the Gravitational Phase-Cancellation Theory (gPCT) project.

## Contents

### Experiment Code
- `FlowShamBo_REALTIME_RUNNER_V2.py`  
  Main testbed. A perceptual-architecture entropy system designed to detect gravitational modulation of collapse symmetry.
  
- `FlowShamBo_dual_launcher.py`  
  Launches FlowShamBo in real-time alongside its external logger.

- `FlowShamBo_external_realtime_logger.py`  
  Logs FlowShamBo outcomes with real-time timestamps for later correlation.

- `coinflip_entropy_test.py`  
  A control experiment using a time-seeded coin flip to compare against the FlowShamBo architecture.

### Gravitational & Lunar Tools
- `moon_altitude.py`  
  Generates moon altitude data for your location and test window.

- `dTide_dt.py`  
  Converts harmonic tide data into a dTide/dt CSV file for analysis.

- `lunar_lag_shift_tool.py`  
  Applies daily lunar lag correction and outputs lag-adjusted tide.csv.

### Analysis & Visualization
- `gpct_analysis_FINAL.py`  
  Computes r, p, and z correlation statistics from FlowShamBo and gravitational phase data.

- `gpct_graph_analysis.py`  
  Visualizes correlations between z-scored FlowMeter and moon altitude/dTide_dt.

- `phase_sweep_analysis.py`  
  Sweeps dTide/dt across 1-hour phase windows to detect optimal alignment.

### Documentation
- `gpct_replication_instructions.txt`  
  Full step-by-step guide for setting up the environment, running the test, and analyzing the results.

- `LICENSE`  
  MIT License for all scripts and analysis code.

---

## Disclaimer

This codebase is provided for educational and experimental purposes only.  
Use at your own risk. No guarantees are made regarding performance, accuracy, or interpretation of results.  
The authors are not responsible for any outcomes resulting from use or modification of this code.

---

MIT © 2025 CollapseRider69
