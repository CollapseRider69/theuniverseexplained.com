# TIME_PATH — Gravitational Phase Modulation of Time

This folder contains a full toolchain to replicate the time drift tracking test described in Section 5.4 of the gPCT paper.

These tools measure and visualize the relationship between local clock drift and gravitational phase (as defined by lunar altitude). The result is a time-domain analog of collapse symmetry: a measurable waveform in clock drift that mirrors the gravitational slope structure over time.

---

## What This Tests

- Whether **local clock drift** expresses gravitational slope symmetry.
- Whether **drift direction** reverses predictably with lunar phase.
- Whether that structure appears **without segmentation**, using only phase-aligned binning.

The hypothesis:

> Time is not a neutral container.  
> It accumulates collapse bias, and drifts in sync with gravitational phase.  
> This structure appears naturally in raw drift data when binned along the lunar waveform.

---

## Included Tools

### `1_gpct_time_flow_tracker.py`

- Tracks time drift between a local system clock and NTP reference.
- Appends time-tagged drift samples to `gpct_time.csv`.
- Can be run indefinitely or at fixed daily intervals.

### `2_gpct_moon_altitude_time.py`

- Adds lunar altitude to each timestamp, in 1 second intervals, in system local time.
- Uses observer’s lat/lon and Python’s ephemeris tools to calculate altitude.

### `3_gpct_graph_1-035_analysis_time.py`

- Z-normalizes the drift signal and moon altitude.
- Bins into 1.035-hour intervals, anchored to lunar midnight.
- Plots both signals to show visual alignment.
- Outputs correlation, p-value, and Z-score.

---

## How to Run

### 1. Begin collecting drift data:

```bash
python 1_gpct_time_flow_tracker.py
```

Let it run in the background for several days (30 days, or a full lunar phase cycle, is recommended).

---

### 2. When the test is complete, add moon altitude:

```bash
python 2_gpct_moon_altitude_time.py
```

---

### 3. Generate and view phase-aligned graph:

```bash
python 3_gpct_graph_1-035_analysis_time.py
```

---

## Expected Result

You should see a clear phase-aligned pattern in the drift signal, tracking gravitational slope. Example output:

- `r ≈ 0.35`
- `Z ≈ 5.00`
- Drift waveform mirrors moon altitude in time.

---

## Replication Note

No segmentation is required — the structure appears in whole-form via binning. This makes the time drift signal a clean test of gravitational modulation, revealing the rhythmic memory of collapse bias.

---

## Output Files

- `gpct_time.csv` — Your evolving local clock drift record.
- `moon.csv` - 1-second lunar data, localized, over the test date-range.
- `time-drift_z_norm_1.035h_anchored.png` (optional) — Your phase-aligned visualization.

---

## Final Note

This system doesn’t calculate time — it watches it lean.

If collapse symmetry is modulated by gravitational slope, then time, as the memory of collapse, should drift in step with it.

This tool lets you watch that happen.
