# COLLAPSE_PATH — Gravitational Phase Modulation of Collapse

This folder contains a complete replication toolset for testing collapse polarity as described in Sections 5.1–5.3 of the gPCT paper.

These tools generate entropy using a timestamp-seeded system, apply gravitational phase context (via lunar altitude and slope), and output both statistical and visual evidence of gravitationally modulated collapse symmetry.

---

## What This Tests

- Whether entropy resolution (FlowShamBo) leans during lunar ascent/descent
- Whether that lean **inverts** predictably at gravitational slope zero-crossings
- Whether symmetry modulation is visible both **statistically** (Z-flip) and **visually** (1.035h binned graph)

The hypothesis:

> Collapse is not binary. It leans. And that lean is gravitationally modulated.

---

## Included Tools

### `1_gpct_flowshambo_test.py`
- Runs FlowShamBo entropy test
- Logs outcomes and flow_meter values to `flow.csv`
- Recommended: Run until at least **10 million rounds**

### `2_gpct_moon_altitude_collapse.py`
- Adds moon altitude and slope to each timestamp
- Uses observer's lat/lon/time to calculate gravitational phase

### `3_gpct_collapse_analysis.py`
- Segments data into lunar ascent/descent
- Computes correlation, Z-score, and Z-flip
- Outputs results to `z_bias_output.csv`

### `4_gpct_graph_1-035_analysis.py`
- Bins and z-normalizes collapse data into 1.035h intervals
- Anchors to lunar midnight to reveal waveform shape
- Outputs correlation and phase-locked polarity plot

---

## How to Run

### 1. Run the FlowShamBo test
```bash
python 1_gpct_flowshambo_test.py
```
Let it run until **at least 10 million rounds** are complete. Output: `gpct_collapse.csv`

---

### 2. When the test is complete, add moon altitude and gravitational slope
```bash
python 2_gpct_moon_altitude_collapse.py
```
Generates: `moon.csv`

---

### 3. Analyze collapse symmetry
```bash
python 3_gpct_collapse_analysis.py
```
Outputs r, p, Z, and Z-flip to `z_bias_output.csv`

---

### 4. Visualize polarity over gravitational phase
```bash
python 4_gpct_graph_1-035_analysis.py
```
Generates a graph comparing Flow Meter polarity to lunar phase.

---

## Expected Result

| Segment         | r       | Z        |
|----------------|---------|----------|
| Lunar Ascent   | ~–0.50  | > 1000   |
| Lunar Descent  | ~+0.50  | > 1000   |
| Total          | ~0.00   | < 100    |
| Z-Flip         |         | > 2500   |

---

## Replication Note

This test is **highly sensitive to gravitational slope**. The polarity signal only appears when segmented by lunar ascent/descent, or binned by phase. Importantly, the low global correlation is not a limitation — it's a feature of gPCT. Symmetry modulation occurs in opposite directions across the gravitational waveform and cancels in aggregate, producing a near-zero net signal by design.

---

## Output Files

- `flow.csv` — Raw entropy + Flow Meter values
- `moon.csv` — Moon altitude and slope (1s intervals)
- `z_bias_output.csv` — Collapse correlation and Z-flip
- `z_normalized_1.035h_anchored.png` — Phase-aligned waveform of collapse polarity

---

## Final Note

This test reveals the rhythm of collapse.

It shows that entropy resolution is not perfectly neutral — it leans with gravity, resolves in phase, and resets when the waveform turns.

This tool lets you see that symmetry in motion.
