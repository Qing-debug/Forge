# Evaluation Task: Physiological Data Processing Pipeline

## Your Goal

Build a data processing pipeline that takes raw physiological calibration and exposure data from a VR experiment and produces a single aggregated output table. You will build this pipeline **twice** - once using Python (pandas) and once using the Workflow Builder tool.

You are free to approach the problem however you see fit. There is no single "correct" sequence of steps - only a correct final output.

---

## Input Files

All files are located in the `data/` folder of this directory.

### 1. `aggregated_data.csv` - Target Table

This is your starting table. It has **6 rows** (3 participants × 2 scenes) and will be enriched with computed columns throughout the pipeline.

| Column | Description |
|--------|-------------|
| Participant_ID | Unique participant identifier (P1, P2, P3) |
| Avatar_Condition | The avatar condition assigned to this participant (Neutral, Gesture, Posture) |
| Scene_Name | The VR scene (Park, City) |
| Participant_Age | Age of the participant in years |
| SAM_Arousal | Self-Assessment Manikin arousal rating (1–9) |
| SAM_Pleasure | Self-Assessment Manikin pleasure rating (1–9) |

### 2. `calibration_data_raw.csv` - Calibration Time-Series

Raw physiological measurements recorded during a resting calibration period. **30 rows** (10 per participant). Contains intentional outliers in the RR interval column.

| Column | Description | Units |
|--------|-------------|-------|
| Participant_ID | Participant identifier | - |
| Participant_Age | Age of the participant | years |
| Polar_HeartRate_RR_Interval | Beat-to-beat interval from heart rate monitor | milliseconds |
| Polar_HearRateBPM | Heart rate | beats per minute |
| Shimmer_D36A_GSR_Skin_Conductance_uS | Galvanic skin response conductance | microsiemens |
| Shimmer_D36A_GSR_Skin_Resistance_kOhms | Galvanic skin response resistance | kilohms |


### 3. `exposure_data.csv` - Exposure Time-Series

Raw physiological measurements recorded during VR scene exposure. **42 rows** (14 per participant, covering 2 scenes plus BlankScene baselines).

| Column | Description | Units |
|--------|-------------|-------|
| Participant_ID | Participant identifier | - |
| AvatarCondition | Avatar condition (matches `Avatar_Condition` in target) | - |
| Shown_Scene | Scene being displayed (matches `Scene_Name` in target) | - |
| Study_Phase | Experimental phase | - |
| AOI_TAG | Area of interest tag (Dog, Mirror, None) | - |
| Unity_Timestamp | Timestamp of recording | datetime |
| pupil_dilation_left | Left eye pupil dilation (**-1 = invalid/missing**) | mm |
| pupil_dilation_right | Right eye pupil dilation (**-1 = invalid/missing**) | mm |
| Polar_HearRateBPM | Heart rate | BPM |
| Polar_RR_Interval | Beat-to-beat interval | milliseconds |
| Shimmer_D36A_GSR_Skin_Conductance_uS | Skin conductance | microsiemens |
| current_blinkDuration | Duration of blink event | ms |
| foveal_corrected_dilation_left | Corrected left pupil dilation | mm |
| foveal_corrected_dilation_right | Corrected right pupil dilation | mm |

**Important:** Column names differ between this file and the target table:
- `AvatarCondition` (exposure) corresponds to `Avatar_Condition` (target)
- `Shown_Scene` (exposure) corresponds to `Scene_Name` (target)
- `Polar_RR_Interval` (exposure) corresponds to `Polar_HeartRate_RR_Interval` (calibration)

---

## Required Output

Your final output should be a CSV with **6 rows** (same as the target table) and the original columns plus all computed columns described below.
### Part A: Calibration Statistics (Clean Column Name)

Fix the incorrectly spelled column name:

- Polar_HearRateBPM -> Polar_HeartRateBPM






### Part B: Calibration Statistics (Unfiltered)

Using the freshly cleaned calibration data, compute per-participant statistics and add them to the target table:

- **Heart rate (BPM):** median, mean, standard deviation
- **RR interval (ms):** median, mean, standard deviation
- **RMSSD:** root mean square of successive differences of RR intervals (see formula below)

### Part C: Calibration Statistics (Filtered)

Using the freshly cleaned calibration data, remove physiologically implausible RR interval values:
- **Keep only rows where:** `200 < RR interval < 2000` (milliseconds)

Then compute the same statistics on the filtered data:
- **Heart rate (BPM):** median, mean, standard deviation
- **RR interval (ms):** median, mean, standard deviation
- **RMSSD** on the cleaned RR intervals

### Part D: Exposure Aggregation

You will need to use the nodes with prefix "phys" if in the workflow_builder condition. For each participant × avatar condition × scene combination in the target table, find the matching rows in the exposure data and compute:

- **Heart rate:** median, mean, standard deviation
- **RR interval:** median, mean, standard deviation - **only include values where 200 < RR < 2000**
- **Pupil dilation (left and right):** median, mean, standard deviation - **exclude rows where the value is -1** (sentinel for missing data)
- **RMSSD:** computed from RR intervals (with 200–2000 bounds applied)
- **Cumulative EDA:** sum of positive successive differences in skin conductance (see formula below)

**Important:** Column names differ between this exposure table and the target table:
- `AvatarCondition` (exposure) corresponds to `Avatar_Condition` (target)
- `Shown_Scene` (exposure) corresponds to `Scene_Name` (target)
- `Polar_RR_Interval` (exposure) corresponds to `Polar_HeartRate_RR_Interval` (calibration)

### Part E: Save results

Save the results to the `user_answers/` folder of this directory. Add your participant ID to the file path.

---

## Domain Formulas

### RMSSD (Root Mean Square of Successive Differences)

Measures heart rate variability from a series of RR intervals.

```
Given RR values: [rr_1, rr_2, rr_3, ..., rr_n]

1. Compute successive differences: diffs = [rr_2 - rr_1, rr_3 - rr_2, ..., rr_n - rr_{n-1}]
2. Square each difference: squared = [d² for d in diffs]
3. Take the mean of squared differences: mean_sq = sum(squared) / len(squared)
4. Take the square root: RMSSD = sqrt(mean_sq)
```

Formula: `RMSSD = sqrt(mean(diff(rr_values)²))`

### Threshold Filter

Remove physiologically implausible RR interval values:
- **Lower bound:** 200 ms (heart rate > 300 BPM is physiologically impossible)
- **Upper bound:** 2000 ms (heart rate < 30 BPM is physiologically impossible)
- **Keep rows where:** `200 < RR interval < 2000` (strict inequality)

### Cumulative Positive Differences

Captures one-directional accumulation in a signal (e.g., increasing skin conductance indicating arousal), ignoring decreases.

```
Given values: [v_1, v_2, v_3, ..., v_n]

1. Compute successive differences: diffs = [v_2 - v_1, v_3 - v_2, ..., v_n - v_{n-1}]
2. Set negative differences to zero: diffs = [max(0, d) for d in diffs]
3. Sum: cumulative = sum(diffs)
```

---


## Time Limit

You have approximately **15 minutes** per condition. Work at your own pace - it's fine if you don't finish everything, but try to get as far as you can.
