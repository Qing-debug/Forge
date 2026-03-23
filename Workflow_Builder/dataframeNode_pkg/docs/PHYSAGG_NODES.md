# Physiological Aggregation Nodes

In-depth reference for the three physiological aggregation nodes: **Phys: Stats Aggregation**, **Phys: RMSSD Aggregation**, and **Phys: Cumulative Aggregation**. All three inherit from a shared base class that handles grouping, filtering, and time windowing.

---

## 1. Shared Configuration (PhysAggNodeBase)

Every phys aggregation node has **two inputs** and **one output**:

| Port | Label | Role |
|------|-------|------|
| Input 0 | Target DF | The table that receives new columns (one row per condition) |
| Input 1 | Exposure DF | Raw time-series data to aggregate from |
| Output 0 | Target DF | The target with new aggregation columns appended |

### Aggregation Name

A string prefix for all output column names. For example, if you set `Exposure_Full` as the aggregation name, all columns produced by that node will start with `Exposure_Full_`.

### Groupby Key Mappings

A list of `(target_col, exposure_col)` pairs that define how a target row maps to its matching exposure rows. The columns can have different names across the two DataFrames - each pair maps one target column to the corresponding exposure column.

Multiple pairs form a **compound key** (all conditions are ANDed). For each target row, the node keeps only exposure rows where every pair matches.

**Example:** Suppose the target has columns `Participant_ID`, `Avatar_Condition`, `Scene_Name` and the exposure has `Participant_ID`, `AvatarCondition`, `Shown_Scene`. Configure three mappings:

| Target Column | Exposure Column |
|---------------|-----------------|
| `Participant_ID` | `Participant_ID` |
| `Avatar_Condition` | `AvatarCondition` |
| `Scene_Name` | `Shown_Scene` |

For a target row `(P1, Neutral, Park)`, only exposure rows where `Participant_ID == P1` AND `AvatarCondition == Neutral` AND `Shown_Scene == Park` are selected.

### Extra Filters

A list of `(exposure_col, value)` pairs that further narrow the exposure data. The value is automatically type-cast to match the column's dtype before comparison.

**Example:** Adding an extra filter `AOI_TAG = Dog` means that after the groupby match, only rows where the exposure column `AOI_TAG` equals `Dog` are kept. This lets you compute stats scoped to a specific area of interest.

You can add multiple extra filters - they are all ANDed together.

### Window Mode

Controls which time range of matched exposure data is used.

#### `full` (default)

All matching exposure rows are used. No time restriction.

#### `before_start`

Restricts to a time window ending at the start of the matched condition. Requires four additional settings:

| Setting | Description | Default |
|---------|-------------|---------|
| `time_window` | Window size in seconds | 60 |
| `timestamp_column` | Column containing timestamps in the exposure DF | `Unity_Timestamp` |
| `target_match_column` | Column in the target DF identifying the condition (e.g. `Scene_Name`) | - |
| `exposure_match_column` | Corresponding column in the exposure DF (e.g. `Shown_Scene`) | - |

**How it works:**

1. Start with the exposure rows that match the groupby keys (and any extra filters).
2. Find all rows where `exposure_match_column == target_match_column` value from the target row.
3. Take the **earliest** timestamp among those rows - this is the "start time" of the condition.
4. Keep only rows where `timestamp >= start_time - time_window` AND `timestamp <= start_time`.

This gives you a pre-condition baseline. For example, if a participant's Park scene starts at `10:01:00` with a 60-second window, you get data from `[10:00:00, 10:01:00]` - typically BlankScene baseline readings plus the first moment of the scene itself.

> **Note:** The `timestamp_column` must contain datetime-compatible values. If loaded from CSV, timestamps may be strings - ensure they parse as datetime before using this mode.

### Step-by-Step: `_getExposureGroup()` Walkthrough

Consider target row `(P1, Neutral, Park)` with the configuration from the examples above (3 groupby pairs, extra filter `AOI_TAG = Dog`, window mode `before_start` with 60s window).

**Step 1 - Groupby match:**
Start with all exposure rows. Apply each key mapping:
- Keep rows where `Participant_ID == P1`
- AND `AvatarCondition == Neutral`
- AND `Shown_Scene == Park`

Result: 5 rows (all P1's Park data under Neutral condition).

**Step 2 - Extra filters:**
Apply `AOI_TAG == Dog`. The value `Dog` is type-cast to the column dtype (string → string, no conversion needed).

Result: 3 rows (only the Dog-fixation rows).

**Step 3 - Before-start windowing:**
Find rows where `Shown_Scene == Park` (the `exposure_match_column` matches `target_match_column`). Get the earliest timestamp among those rows - say `10:01:00`. Select rows in `[10:00:00, 10:01:00]`.

Result: rows within the 60-second window ending at the Park scene start.

> In `full` mode, Step 3 is skipped entirely and all rows from Step 2 are used.

---

## 2. Phys: Stats Aggregation

Computes descriptive statistics (any subset of median, mean, std, min, max) for one or more exposure columns, with optional per-column bounds and filters.

### Column Configs

A list of column configurations, each a dict with:

| Key | Required | Description |
|-----|----------|-------------|
| `source_column` | Yes | Which exposure column to read values from |
| `output_label` | Yes | Suffix for output column names |
| `lower_bound` | No | Exclude values **<= this** (strict `>` comparison) |
| `upper_bound` | No | Exclude values **>= this** (strict `<` comparison) |
| `filter_value` | No | Exclude rows with this exact value (e.g. `-1` sentinels) |

### Stats to Compute

Select any subset of: `median`, `mean`, `std`, `min`, `max`.

### Output Column Naming

Each output column is named: **`{aggregation_name}_{Stat}_{output_label}`**

For example, with aggregation name `Exposure_Full`, stat `Mean`, and output label `HeartRate`:
→ `Exposure_Full_Mean_HeartRate`

### Example Use Cases

#### 2.1 - Basic HR stats per participant per scene

The simplest case: no bounds, no filters.

**Config:**
- Aggregation Name: `Exposure_Full`
- Groupby: `Participant_ID ↔ Participant_ID`, `Scene_Name ↔ Shown_Scene`
- Window Mode: `full`
- Column Config: source=`Polar_HearRateBPM`, label=`HeartRate`
- Stats: median, mean, std

**Output columns:** `Exposure_Full_Median_HeartRate`, `Exposure_Full_Mean_HeartRate`, `Exposure_Full_Std_HeartRate`

For each target row, the node finds all exposure rows for that participant and scene, then computes median/mean/std of the `Polar_HearRateBPM` column across those rows.

#### 2.2 - RR interval stats with physiological bounds

RR intervals below 200 ms or above 2000 ms are physiologically implausible. Use bounds to exclude them.

**Column Config:**
- source=`Polar_RR_Interval`, label=`RR_Interval_Ranged`
- lower_bound=`200`, upper_bound=`2000`

Values ≤ 200 and ≥ 2000 are excluded before computing statistics. This prevents outliers (e.g., sensor glitches producing RR=50 or RR=3500) from distorting the results.

#### 2.3 - Pupil dilation stats excluding sentinel values

Some eye trackers report `-1` when tracking is lost (blinks, glances away). Use `filter_value` to exclude these.

**Column Config:**
- source=`pupil_dilation_left`, label=`Pupil_Left`
- filter_value=`-1`

All rows where `pupil_dilation_left == -1` are removed before computing stats. The remaining valid readings give accurate pupil dilation statistics.

#### 2.4 - Multiple columns configured simultaneously

You can configure multiple columns in a single node. Each column config is independent - it has its own source column, bounds, and filter.

**Column Configs:**
1. source=`pupil_dilation_left`, label=`Pupil_Left`, filter_value=`-1`
2. source=`Polar_HearRateBPM`, label=`HeartRate` (no bounds/filter)
3. source=`Polar_RR_Interval`, label=`RR_Ranged`, lower_bound=`200`, upper_bound=`2000`

With 5 stats selected, this produces **15 output columns** (5 stats × 3 columns) in a single node.

#### 2.5 - Before-start window: 60s baseline before scene onset

Compute baseline stats from the period just before a scene starts, using BlankScene data as a resting reference.

**Config changes from 2.1:**
- Window Mode: `before_start`
- Time Window: `60`
- Timestamp Column: `Unity_Timestamp`
- Target Match Column: `Scene_Name`
- Exposure Match Column: `Shown_Scene`
- Aggregation Name: `Baseline_60s`

For a target row (P1, Park), the node finds the earliest Park timestamp, then selects all P1 data in the 60 seconds up to that point. This typically captures BlankScene baseline readings plus the first moment of the scene.

Comparing `Baseline_60s_Mean_HeartRate` vs `Exposure_Full_Mean_HeartRate` reveals the scene's physiological impact.

#### 2.6 - Extra filters: Dog-AOI-only stats

Compute stats only during fixations on a specific area of interest.

**Config changes from 2.1:**
- Extra Filters: `AOI_TAG` = `Dog`
- Aggregation Name: `Exposure_Dog_AOI`

After the groupby match narrows to the correct participant/scene, the extra filter further restricts to rows where `AOI_TAG == Dog`. Stats reflect only moments when the participant was looking at the Dog AOI.

---

## 3. Phys: RMSSD Aggregation

Computes **RMSSD** (Root Mean Square of Successive Differences) - a standard heart rate variability (HRV) metric derived from RR intervals.

### Formula

```
diffs = rr_values[1:] - rr_values[:-1]
RMSSD = sqrt(mean(diffs^2))
```

RMSSD quantifies beat-to-beat variability. Higher RMSSD indicates greater parasympathetic (vagal) tone. At least 2 valid RR values are needed; otherwise the result is `NaN`.

### Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `rr_column` | `Polar_RR_Interval` | Column containing RR interval values (in ms) |
| `lower_bound` | `200` | Exclude RR values ≤ this (ms) |
| `upper_bound` | `2000` | Exclude RR values ≥ this (ms) |
| `output_label` | `RR_RMSSD` | Suffix for the output column |

Bounds use strict inequality (`>` and `<`), so values exactly at the boundary are excluded. The default range [200, 2000] excludes physiologically implausible RR intervals.

### Output Column Naming

**`{aggregation_name}_{output_label}`**

For example: `Exposure_Full_RR_RMSSD`

### Example Use Cases

#### 3.1 - Basic RMSSD per participant per scene

**Config:**
- Aggregation Name: `Exposure_Full`
- Groupby: `Participant_ID ↔ Participant_ID`, `Scene_Name ↔ Shown_Scene`
- Window Mode: `full`
- RR Column: `Polar_RR_Interval`
- Bounds: 200 / 2000

For target row (P1, Park) with 5 matching RR values `[750, 732, 769, 741, 759]`:

```
Diffs:  [-18, 37, -28, 18]
Squared: [324, 1369, 784, 324]
Mean:    700.25
RMSSD:   sqrt(700.25) = 26.5
```

#### 3.2 - Tighter bounds for a specific population

For certain populations (e.g., athletes with very low resting HR, or elderly participants), you may want different bounds.

**Config:**
- lower_bound: `300`
- upper_bound: `1500`

This excludes a wider range of borderline values, producing a more conservative RMSSD estimate.

#### 3.3 - Before-start baseline HRV

Compute resting HRV from the period before scene onset.

**Config:**
- Window Mode: `before_start`
- Time Window: `60`
- Aggregation Name: `Baseline_60s`

The node computes RMSSD from the 60 seconds of data before the scene starts. Comparing `Baseline_60s_RR_RMSSD` vs `Exposure_Full_RR_RMSSD` shows whether HRV changed during the scene (e.g., increased stress → lower RMSSD).

---

## 4. Phys: Cumulative Aggregation

Computes the **cumulative sum of positive successive differences** - a measure that captures accumulation while ignoring oscillation.

### Algorithm

```
values = exposure_column_values
diffs = values[1:] - values[:-1]
diffs[diffs < 0] = 0          # zero out negative differences
result = sum(diffs)
```

Only increases are counted. If a signal goes up by 0.3 then down by 0.5, only the 0.3 increase contributes. This is useful for measures like electrodermal activity (EDA) where cumulative increases indicate arousal accumulation regardless of subsequent decreases.

At least 2 values are needed; otherwise the result is `NaN`.

### Column Configs

A list of column configurations, each a dict with:

| Key | Required | Default | Description |
|-----|----------|---------|-------------|
| `source_column` | Yes | - | Which exposure column to read |
| `output_label` | Yes | - | Suffix for the output column |
| `use_abs` | No | `false` | If true, takes `abs(values)` before differencing |

When `use_abs` is `false` (default), the node computes differences on raw values, then keeps only positive diffs. This captures net upward movement.

When `use_abs` is `true`, the node first takes the absolute value of each data point, then computes differences and keeps only positives. This is useful for signals that can be negative (e.g., corrected pupil dilation values that may cross zero) where you want to capture total magnitude of change regardless of sign.

### Output Column Naming

**`{aggregation_name}_{output_label}`**

For example: `Exposure_Full_Cumulative_EDA`

### Example Use Cases

#### 4.1 - Cumulative EDA (only increases = arousal accumulation)

Electrodermal activity rises with sympathetic nervous system activation. Cumulative positive change captures total arousal accumulation, filtering out natural signal decay.

**Config:**
- Column Config: source=`Shimmer_D36A_GSR_Skin_Conductance_uS`, label=`Cumulative_EDA`
- use_abs: `false`

For values `[6.0, 6.3, 5.8, 6.1, 5.9]`:

```
Diffs:           [0.3, -0.5, 0.3, -0.2]
After zeroing:   [0.3, 0,    0.3, 0   ]
Cumulative EDA = 0.6
```

Only the two increases (0.3 each) are summed. The decreases are ignored.

#### 4.2 - `use_abs=true`: total pupil change magnitude

For corrected pupil dilation values that may be positive or negative, `use_abs` captures total movement in both directions.

**Config:**
- Column Config: source=`foveal_corrected_dilation_left`, label=`Cumulative_Dilation_Abs`
- use_abs: `true`

For values `[-0.2, 0.5, -0.1, 0.3, -0.4]`:

```
Absolute values: [0.2, 0.5, 0.1, 0.3, 0.4]
Diffs:           [0.3, -0.4, 0.2, 0.1]
After zeroing:   [0.3, 0,    0.2, 0.1]
Result = 0.6
```

Without `use_abs`, the raw differences would be computed on the original (possibly negative) values, which may not capture the intended total change magnitude.

#### 4.3 - Multiple columns simultaneously

Like Stats Aggregation, you can configure multiple columns in one node.

**Column Configs:**
1. source=`Shimmer_D36A_GSR_Skin_Conductance_uS`, label=`Cumulative_EDA`, use_abs=`false`
2. source=`foveal_corrected_dilation_left`, label=`Cumulative_Dilation_Left`, use_abs=`false`

This produces two output columns in a single pass over the data: `{agg_name}_Cumulative_EDA` and `{agg_name}_Cumulative_Dilation_Left`.
