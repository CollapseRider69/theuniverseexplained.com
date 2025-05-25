# REPLICATION — gPCT Experimental Framework

This is the root folder for all tools and data paths used to replicate and explore the gravitational Phase-Cancellation Theory (gPCT).

It contains three distinct subfolders:

---

## 1. `1_COLLAPSE_PATH/`

Tests collapse polarity modulation by gravitational phase. 
This folder reproduces the segmented Z-flip results described in Sections 5.1–5.3 of the paper.

- Runs FlowShamBo to generate timestamp-seeded entropy
- Segments outcomes by gravitational slope (lunar ascent/descent)
- Outputs Z-scores, correlation coefficients, and phase-aligned graphs

Recommended minimum: **10 million rounds**.

### Output:
- Z-flip values > 2500 expected
- Strong polarity inversion across gravitational waveform

---

## 2. `2_TIME_PATH/`

Tracks local clock drift against gravitational slope.
This folder replicates the time-domain test described in Section 5.4.

- Measures drift between local system clock and NTP
- Compares drift waveform against lunar altitude and dG/dt
- Requires no segmentation — phase-aligned graph reveals correlation

Recommended minimum: **30 days of drift data**.

### Output:
- Phase-aligned drift curve
- Z ≈ 3.0 expected from raw binned data

---

## 3. `3_LEGACY_TOOLS/`

Historical tools used during the discovery phase.

- Includes tide-based sweep experiments
- Frame shift correlation tests (±12h from lunar transit)
- Preserved for context, not required for replication

These tools helped reveal the phase structure now formalized by the PBI model.

---

## Summary

Each path is self-contained and independently testable.
You do not need to run all paths to confirm gPCT.

- Use `COLLAPSE_PATH` to test outcome polarity
- Use `TIME_PATH` to test temporal modulation
- Use `LEGACY_TOOLS` for curiosity or historical reference

This repo provides the tools to observe gravitational symmetry — from entropy lean to time drift.
