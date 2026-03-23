# Synthetic Data Walkthrough

A step-by-step guide for building and validating the calibration and physiological
aggregation pipeline in the Ryven workflow builder using the synthetic test data.

**Participants:**
- P1: age 25, avatar condition Neutral
- P2: age 35, avatar condition Gesture
- P3: age 45, avatar condition Posture

**Scenes:** Park, City (each participant sees both)

---

## How to use this guide

1. **Add a node** - drag it from the node palette onto the canvas.
2. **Configure** - double-click the node (or right-click → Configure) to open
   its config dialog. Set the values listed under each node's **Configure** step.
3. **Wire** - drag from an output port to an input port to connect nodes.
   Ports are labeled (e.g., "Target DF", "Data DF"). Each node section below
   tells you what to connect where.
4. **Run** - click the Run button on the final node in the chain (or use
   the toolbar). Data flows forward through connected nodes automatically.
5. **Verify** - click the Preview button on a node to inspect its output
   DataFrame. Use the verification notes below to confirm the node is working.

> **Tip:** You can Preview any intermediate node, not just the final one.
> This is useful for debugging when downstream results look wrong.

---

## Files

| File | Role | Rows | Description |
|------|------|------|-------------|
| `aggregated_data.csv` | Target DF | 6 | One row per participant × scene. This is the table we keep adding columns to. |
| `calibration_data.csv` | Pupil dilation calibration | 9 | Pre-computed median pupil sizes per participant per grayscale level (0, 128, 255). |
| `calibration_data_raw.csv` | Raw calibration time series | 30 | 10 timestamped readings per participant during resting calibration. Contains intentional outliers. |
| `exposure_data.csv` | Raw exposure time series | 42 | Timestamped physiological readings during scene exposure. Includes BlankScene baselines, Dog/Mirror AOI tags, and sentinel values (-1). |

---

## Part 1: Calibration Pipeline

### Node 1 - Calib: Pupil Dilation

**Wire:**
- Input 0 ("Target DF") ← CSV Load node with `aggregated_data.csv`
- Input 1 ("Data DF") ← CSV Load node with `calibration_data.csv`

**Configure:**
- Merge Key Column: `Participant_ID`
- Category Column: `Shown_Gray_Scale_Value`
- Left Value Column: `Median_Pupil_Dilation_Left`
- Right Value Column: `Median_Pupil_Dilation_Right`
- Grayscale Values: `0, 128, 255`

**Verify:** Preview should show the original 6 rows with 6 new columns added:

    Calibration_PupilDilation_Left_0
    Calibration_PupilDilation_Right_0
    Calibration_PupilDilation_Left_128
    Calibration_PupilDilation_Right_128
    Calibration_PupilDilation_Left_255
    Calibration_PupilDilation_Right_255

Spot-check: P1's rows should have Left_128 = 3.40, Right_128 = 3.50.

---

### Node 2 - Calib: Groupby Stats (Raw HR + RR)

**Wire:**
- Input 0 ("Target DF") ← output of Node 1
- Input 1 ("Data DF") ← CSV Load node with `calibration_data_raw.csv`

**Configure:**
- Groupby Key: `Participant_ID`
- Metric Row 1: Column `Polar_HearRateBPM`, Stats: median / mean / std
  - Output names: `Calibration_Median_Resting_HeartRate`, `Calibration_Mean_Resting_HeartRate`, `Calibration_SD_Resting_HeartRate`
- Metric Row 2: Column `Polar_HeartRate_RR_Interval`, Stats: median / mean / std
  - Output names: `Calibration_Median_Resting_RR_Interval`, `Calibration_Mean_Resting_RR_Interval`, `Calibration_SD_Resting_RR_Interval`

**Verify:** 6 new columns on the same 6 rows. The raw RR stats are distorted
by outliers - this is intentional:

| Participant | BPM median | RR median | RR mean | RR std |
|-------------|-----------|-----------|---------|--------|
| P1 | 74.0 | 806.5 | 989.8 | 906.3 |
| P2 | 80.0 | 749.0 | 805.0 | 533.1 |
| P3 | 66.0 | 906.5 | 1110.3 | 1050.5 |

The huge std values show why the threshold filter matters.

---

### Node 3 - Calib: Compute RMSSD (Raw)

**Wire:**
- Input 0 ("Target DF") ← output of Node 2
- Input 1 ("Data DF") ← CSV Load node with `calibration_data_raw.csv`

**Configure:**
- Groupby / Merge Key: `Participant_ID`
- RR Interval Column: `Polar_HeartRate_RR_Interval`
- Output Column Name: `Calibration_RR_Interval_RAW_RMSSD`

**Verify:** 1 new column. Raw RMSSD is inflated by outliers:

| Participant | Raw RMSSD |
|-------------|-----------|
| P1 | 1315.3 |
| P2 | 759.4 |
| P3 | 1520.5 |

Compare these to the cleaned values later to see the improvement.

---

### Node 4 - Calib: Threshold Filter

> **Note:** This node has **1 input** (no Target DF port). It takes a single
> DataFrame, filters rows, and outputs the filtered result.

**Wire:**
- Input 0 ← CSV Load node with `calibration_data_raw.csv`

**Configure:**
- Row 1: `Polar_HeartRate_RR_Interval` > `200`
- Connector: AND
- Row 2: `Polar_HeartRate_RR_Interval` < `2000`

**Verify:** Preview should show **24 rows** (was 30). Each participant loses
2 outlier rows:

| Participant | Removed values | Rows remaining |
|-------------|---------------|----------------|
| P1 | RR=150 (too low), RR=3500 (too high) | 8 |
| P2 | RR=100 (too low), RR=2200 (too high) | 8 |
| P3 | RR=50 (too low), RR=4000 (too high) | 8 |

---

### Node 5 - Calib: Groupby Stats (ABS-Cleaned RR)

**Wire:**
- Input 0 ("Target DF") ← output of Node 3
- Input 1 ("Data DF") ← output of Node 4

**Configure:**
- Groupby Key: `Participant_ID`
- Metric: Column `Polar_HeartRate_RR_Interval`, Stats: median / mean / std
  - Output names: `Calibration_Median_RR_CLEANED_ABS`, `Calibration_Mean_RR_CLEANED_ABS`, `Calibration_SD_RR_CLEANED_ABS`

**Verify:** 3 new columns. The stats are more stable now, but the remaining
outlier values (P1: 600, P2: 500, P3: 700) still pull the mean down:

| Participant | Median | Mean | Std |
|-------------|--------|------|-----|
| P1 | 806.5 | 781.0 | 73.7 |
| P2 | 749.0 | 718.8 | 88.6 |
| P3 | 906.5 | 881.6 | 73.8 |

---

### Node 6 - Calib: Compute RMSSD (ABS-Cleaned)

**Wire:**
- Input 0 ("Target DF") ← output of Node 5
- Input 1 ("Data DF") ← output of Node 4

**Configure:**
- Groupby / Merge Key: `Participant_ID`
- RR Interval Column: `Polar_HeartRate_RR_Interval`
- Output Column Name: `Calibration_RR_CLEANED_ABS_RMSSD`

**Verify:** 1 new column. RMSSD is dramatically lower than raw:

| Participant | ABS RMSSD | (was Raw) |
|-------------|-----------|-----------|
| P1 | 114.1 | (1315.3) |
| P2 | 134.7 | (759.4) |
| P3 | 113.6 | (1520.5) |

Still affected by the borderline values (600, 500, 700) - the relative
threshold addresses these next.

---

### Node 7 - Calib: Relative Threshold Filter

> **Note:** This node has 2 inputs labeled "Target DF" and "Data DF", but it
> **only reads from Data DF** (input 1). The output is the cleaned Data DF,
> not Target DF. Target DF (input 0) is defined but unused.

**Wire:**
- Input 0 ("Target DF") ← not connected (unused)
- Input 1 ("Data DF") ← output of Node 4 (ABS-filtered data, 24 rows)

**Configure:**
- Groupby Column: `Participant_ID`
- Age Column: `Participant_Age`
- RR Interval Column: `Polar_HeartRate_RR_Interval`
- Max Iterations: `20`

**How it works:** For each participant, the age-based threshold is:

    threshold = -age / 3 + 45

Younger participants get stricter (higher) thresholds. Each interior value is
checked: if its percentage deviation from the average of its two neighbors
exceeds the threshold, it is removed. This repeats until no more values are
removed or max iterations is reached.

**P1 (age 25), threshold = 36.67%:**

    RR values: [810, 800, 820, 805, 790, 815, 600, 808]

    Interior value checks (iteration 1):
      800: |800 - avg(810,820)| / 800 = 1.9%  → keep
      820: |820 - avg(800,805)| / 820 = 2.1%  → keep
      805: |805 - avg(820,790)| / 805 = 0.0%  → keep
      790: |790 - avg(805,815)| / 790 = 2.5%  → keep
      815: |815 - avg(790,600)| / 815 = 14.7% → keep
      600: |600 - avg(815,808)| / 600 = 35.2% → keep (just under 36.67%)

    Result: all 8 rows kept (600 is borderline but survives)

**P2 (age 35), threshold = 33.33%:**

    RR values: [740, 750, 760, 745, 755, 500, 748, 752]

    Iteration 1:
      750: |750 - avg(740,760)| / 750 = 0.0%  → keep
      760: |760 - avg(750,745)| / 760 = 1.6%  → keep
      745: |745 - avg(760,755)| / 745 = 1.7%  → keep
      755: |755 - avg(745,500)| / 755 = 17.5% → keep
      500: |500 - avg(755,748)| / 500 = 50.3% → REMOVE
      748: |748 - avg(500,752)| / 748 = 16.3% → keep

    After removal: [740, 750, 760, 745, 755, 748, 752]
    Iteration 2: all deviations < 2% → no removals, done.

    Result: 7 rows (500 removed)

**P3 (age 45), threshold = 30.00%:**

    RR values: [900, 910, 920, 905, 895, 915, 700, 908]

    Iteration 1:
      910: |910 - avg(900,920)| / 910 = 0.0%  → keep
      920: |920 - avg(910,905)| / 920 = 1.4%  → keep
      905: |905 - avg(920,895)| / 905 = 0.3%  → keep
      895: |895 - avg(905,915)| / 895 = 1.7%  → keep
      915: |915 - avg(895,700)| / 915 = 12.8% → keep
      700: |700 - avg(915,908)| / 700 = 30.2% → REMOVE (just over 30.0%)

    After removal: [900, 910, 920, 905, 895, 915, 908]
    Iteration 2: all deviations < 2% → done.

    Result: 7 rows (700 removed)

**Verify:** Preview should show **22 rows** total (was 24). P1 keeps all 8;
P2 and P3 each drop to 7.

---

### Node 8 - Calib: Groupby Stats (REL-Cleaned RR)

**Wire:**
- Input 0 ("Target DF") ← output of Node 6
- Input 1 ("Data DF") ← output of Node 7

**Configure:**
- Groupby Key: `Participant_ID`
- Metric: Column `Polar_HeartRate_RR_Interval`, Stats: median / mean / std
  - Output names: `Calibration_Median_RR_CLEANED_REL`, `Calibration_Mean_RR_CLEANED_REL`, `Calibration_SD_RR_CLEANED_REL`

**Verify:** 3 new columns. P1 stats are unchanged (nothing was removed), but
P2 and P3 improve dramatically now that the borderline values are gone:

| Participant | Median | Mean | Std |
|-------------|--------|------|-----|
| P1 | 806.5 | 781.0 | 73.7 |
| P2 | 750.0 | 750.0 | 6.56 |
| P3 | 908.0 | 907.6 | 8.54 |

Compare P2's std: 533.1 (raw) → 88.6 (ABS) → 6.56 (REL).

---

### Node 9 - Calib: Compute RMSSD (REL-Cleaned)

**Wire:**
- Input 0 ("Target DF") ← output of Node 8
- Input 1 ("Data DF") ← output of Node 7

**Configure:**
- Groupby / Merge Key: `Participant_ID`
- RR Interval Column: `Polar_HeartRate_RR_Interval`
- Output Column Name: `Calibration_RR_CLEANED_REL_RMSSD`

**Verify:** 1 new column. The full cleaning progression:

| Participant | Raw RMSSD | ABS RMSSD | REL RMSSD |
|-------------|-----------|-----------|-----------|
| P1 | 1315.3 | 114.1 | 114.1 |
| P2 | 759.4 | 134.7 | 9.9 |
| P3 | 1520.5 | 113.6 | 12.7 |

P1 is unchanged (nothing removed by REL filter). P2 and P3 drop to single
digits, showing the relative filter caught what the absolute filter missed.

The target DF after all 9 nodes has the original 6 rows with ~16 new
calibration columns.

---

## Part 2: Physiological Aggregation Pipeline

### Starting Point

- **Target DF:** output of Node 9 (aggregated_data with calibration columns)
- **Exposure DF:** `exposure_data.csv` (42 rows of timestamped physiological data)

### How the exposure data is structured

Each participant has data organized as:

    BlankScene readings (baseline before Park)
    Park scene readings (with Dog/Mirror/None AOI tags)
    BlankScene readings (baseline before City)
    City scene readings (with Dog/Mirror/None AOI tags)

Sentinel values: `-1` in pupil columns means "no valid reading" (blink/tracking loss).

---

### Node 10 - Phys: Stats Aggregation (Full Time Window)

**Wire:**
- Input 0 ("Target DF") ← output of Node 9
- Input 1 ("Exposure DF") ← CSV Load node with `exposure_data.csv`

**Configure:**
- Aggregation Name: `Exposure_Full_Time_Window`
- Groupby Key Mappings:
  - `Participant_ID` ↔ `Participant_ID`
  - `Avatar_Condition` ↔ `AvatarCondition`
  - `Scene_Name` ↔ `Shown_Scene`
- Window Mode: Full Window
- Stats: Median, Mean, SD, Min, Max
- Column Configs:
  - Source: `pupil_dilation_left`, Label: `Pupil_Left`, Filter Value: `-1`
  - Source: `Polar_HearRateBPM`, Label: `HeartRate`
  - Source: `Polar_RR_Interval`, Label: `RR_Interval_Ranged`, Lower: `200`, Upper: `2000`

**Verify:** 15 new columns (5 stats × 3 source columns). For target row
(P1, Neutral, Park) - 5 exposure rows matched, pupil has 4 valid values
after excluding -1:

| Metric | Pupil_Left (excl -1) | HeartRate | RR |
|--------|---------------------|-----------|-----|
| Median | 4.55 | 80.0 | 750.0 |
| Mean | 4.525 | 80.0 | 750.2 |
| Std | 0.25 | 1.58 | 14.5 |
| Min | 4.2 | 78 | 732 |
| Max | 4.8 | 82 | 769 |

---

### Node 11 - Phys: RMSSD Aggregation (Full Time Window)

**Wire:**
- Input 0 ("Target DF") ← output of Node 10
- Input 1 ("Exposure DF") ← CSV Load node with `exposure_data.csv`

**Configure:**
- Aggregation Name: `Exposure_Full_Time_Window`
- Groupby Key Mappings: same 3 pairs as Node 10
- Window Mode: Full Window
- RR Interval Column: `Polar_RR_Interval`
- Lower Bound: `200`, Upper Bound: `2000`
- Output Label: `RR_RMSSD`

**Verify:** 1 new column: `Exposure_Full_Time_Window_RR_RMSSD`.
For (P1, Neutral, Park):

    RR values: [750, 732, 769, 741, 759]
    Diffs: [-18, 37, -28, 18]
    RMSSD = sqrt(mean([324, 1369, 784, 324])) = 26.5

---

### Node 12 - Phys: Cumulative Aggregation (Full Time Window)

**Wire:**
- Input 0 ("Target DF") ← output of Node 11
- Input 1 ("Exposure DF") ← CSV Load node with `exposure_data.csv`

**Configure:**
- Aggregation Name: `Exposure_Full_Time_Window`
- Groupby Key Mappings: same 3 pairs as Node 10
- Window Mode: Full Window
- Column Configs:
  - Source: `Shimmer_D36A_GSR_Skin_Conductance_uS`, Label: `Cumulative_EDA`
  - Source: `foveal_corrected_dilation_left`, Label: `Cumulative_Dilation_Left`

**Verify:** 2 new columns. For (P1, Neutral, Park):

    GSR values: [6.0, 6.3, 5.8, 6.1, 5.9]
    Diffs: [0.3, -0.5, 0.3, -0.2]
    Keep only positives: [0.3, 0, 0.3, 0]
    Cumulative EDA = 0.6

    Dilation values: [4.4, 4.7, 4.1, 4.5, 4.3]
    Diffs: [0.3, -0.6, 0.4, -0.2]
    Keep only positives: [0.3, 0, 0.4, 0]
    Cumulative Dilation = 0.7

Only increases are counted - captures physiological arousal accumulation.

---

### Variant: "60s Before Start" Aggregation

To demonstrate the Before Start window mode, repeat Nodes 10–12 with
different config.

> **Important:** The Before Start mode uses `pd.Timedelta` for time windowing,
> which requires the `Unity_Timestamp` column to be datetime type. If loaded
> from CSV, timestamps will be strings by default. Ensure the column parses
> correctly as datetime before using this mode (some CSV Load nodes may handle
> this automatically; if not, you may need a preprocessing step).

**Config changes (apply to each of the 3 repeated nodes):**
- Aggregation Name: `Exposure_60s_Before`
- Window Mode: **Before Start**
- Time Window: `60` (seconds)
- Timestamp Column: `Unity_Timestamp`
- Target Match Column: `Scene_Name`
- Exposure Match Column: `Shown_Scene`

**What happens for (P1, Neutral, Park):**

1. Filter exposure to P1 + Neutral (gets all P1 rows including BlankScene)
2. Find rows where Shown_Scene == 'Park' (the target's Scene_Name)
3. Get the earliest Park timestamp: `2026-01-01 10:01:00`
4. Select data in window [10:00:00, 10:01:00] - the 60 seconds up to and including Park start
5. This gives 4 rows (3 BlankScene baselines + the first Park row):

        10:00:00 → BlankScene, pupil 3.1, HR 72
        10:00:30 → BlankScene, pupil 3.2, HR 74
        10:00:50 → BlankScene, pupil 3.0, HR 73
        10:01:00 → Park, pupil 4.5, HR 80

The Park start row is included because the filter uses `<=`.

This gives you a pre-scene baseline to compare against the full-window
exposure values - the difference reveals the scene's physiological impact.

---

### Variant: AOI-Filtered Aggregation

To show extra filters, repeat with:

- Aggregation Name: `Exposure_Dog_AOI`
- Extra Filters: `AOI_TAG` == `Dog`

**What happens for (P1, Neutral, Park):**

Starts with the 5 Park rows, then further filters to AOI_TAG == 'Dog':

    10:01:00 → pupil 4.5, HR 80 (Dog)
    10:01:30 → pupil 4.8, HR 82 (Dog)
    10:02:30 → pupil 4.6, HR 81 (Dog)

The Mirror and None rows are excluded. Stats computed only on Dog-fixation data.

---

## Summary: What Each Node Demonstrates

| Node | Key Concept | What the Synthetic Data Shows |
|------|-------------|-------------------------------|
| 1 Pupil Dilation | Categorical lookup + merge | 3 grayscale levels → 6 new columns per participant |
| 2 Groupby Stats (Raw) | Grouped aggregation | Raw stats are skewed by outliers (compare before/after cleaning) |
| 3 RMSSD (Raw) | Heart rate variability metric | Raw RMSSD ~1315 vs cleaned ~114 - outliers dominate |
| 4 Threshold Filter | Absolute bounds (1 input) | Removes 6 impossible values (RR < 200 or > 2000), 30 → 24 rows |
| 5 Groupby Stats (ABS) | Cleaned aggregation | Better but borderline values (500, 600, 700) still affect stats |
| 6 RMSSD (ABS) | Cleaned HRV | RMSSD drops ~10× but borderline values remain |
| 7 Relative Threshold | Age-dependent iterative cleaning | P2's 500 and P3's 700 removed; P1's 600 survives (younger = more lenient) |
| 8 Groupby Stats (REL) | Final cleaned aggregation | P2 std drops from 88.6 to 6.56 after relative cleaning |
| 9 RMSSD (REL) | Final cleaned HRV | P2 RMSSD: 759 → 135 → 9.9 across the three stages |
| 10 Phys Stats | Per-condition descriptive stats | Filter value -1 excludes invalid readings; bounds exclude implausible values |
| 11 Phys RMSSD | Per-condition HRV | Same RMSSD metric but scoped to specific exposure conditions |
| 12 Phys Cumulative | Cumulative positive change | Only sums increases - captures arousal accumulation, not oscillation |
| Before Start mode | Time-windowed baseline | Uses BlankScene data before scene onset for comparison |
| Extra Filters | AOI-scoped analysis | Restricts to Dog-fixation or Mirror-fixation data only |
