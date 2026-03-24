# Workflow Builder

A Ryven-based visual workflow builder for pandas DataFrame operations, physiological data calibration, and time-series aggregation. Provides a pull-based node system for loading, transforming, and exporting tabular data without writing code.

## Prerequisites

- **Python 3.10+**
- Required packages:

```
pip install ryven pyside6 qtpy pandas numpy
```

## Setup

1. Clone this repository.
2. Install the dependencies listed above.
3. Launch Ryven:

```bash
python Workflow_Builder/main.py
```

4. In the Ryven window, import the node package:
   - Right-click on the canvas and select **Import Nodes**
   - Browse to `Workflow_Builder/dataframeNode_pkg/` and select it

The launcher (`Workflow_Builder/main.py`) automatically configures Ryven to use **exec-flow** mode, which is required for this package's pull-based execution model.

## Available Nodes

### DataFrame Nodes

| Node | Description |
|------|-------------|
| **Load CSV** | Source node. Loads a single CSV file into a DataFrame. |
| **Load Multi CSV** | Source node. Loads multiple CSV files and concatenates them row-wise. |
| **Export CSV** | Sink node. Saves the input DataFrame to a CSV file. |
| **Replace Value** | Replaces values in a column. Supports single-value or full-column remapping with dtype casting. |
| **Compute Column** | Creates a new column by evaluating a pandas expression (e.g., `col_a + col_b`). |
| **Sort by Column** | Sorts by one or more columns with configurable ascending/descending order. |
| **Rename Column** | Renames one or more columns via an old-to-new mapping. |
| **Reorder Column** | Repositions selected columns to appear immediately after an anchor column. |
| **Merge** | Merges two DataFrames via `pd.merge()` with configurable join type and key pairs. |
| **Concat** | Concatenates up to 6 DataFrames along rows or columns. |

### Calibration Nodes

Designed for VR experiment physiological data cleaning and calibration.

| Node | Description |
|------|-------------|
| **Calib Pupil Dilation** | Maps median pupil dilation per grayscale level from calibration data onto a target DataFrame. |
| **Calib Groupby Stats** | Computes grouped statistics (median/mean/std) from raw data and merges results onto a target DataFrame. |
| **Calib Threshold Filter** | Removes rows by numeric threshold conditions with AND/OR chaining. |
| **Calib RMSSD** | Computes RMSSD (heart rate variability) per group and maps it onto a target DataFrame. |
| **Calib Relative Threshold** | Performs age-dependent iterative outlier removal on RR interval data. |

### Physiological Aggregation Nodes

Aggregate time-series physiological exposure data into per-condition statistics.

| Node | Description |
|------|-------------|
| **Phys Stats Agg** | Computes median, mean, std, min, and max for configured exposure columns per matched condition. |
| **Phys RMSSD Agg** | Computes RMSSD from matched exposure RR intervals per target row. |
| **Phys Cumulative Agg** | Computes cumulative sum of positive successive differences (e.g., EDA arousal accumulation). |

## How to Use

### Execution Model

The Workflow Builder uses a **pull-based** execution model:

1. **Build your pipeline** by placing nodes on the canvas and wiring them together (output port to input port).
2. **Configure** each node by clicking the **Configure** button and filling in the required fields (column names, formulas, file paths, etc.).
3. **Run** by clicking the **Run** button on any node. The node automatically pulls data from its upstream chain — if an upstream node hasn't run yet, it executes first, recursively.
4. **Caching** prevents redundant computation. Once a node runs, it caches its result. The status indicator shows whether a node is cached or will recompute.
5. **Reset Cache** clears a node's cached result (and all downstream nodes), forcing recomputation on the next run.
6. **Preview** opens a read-only table view of a node's input and output DataFrames.

### Typical Workflow

```
Load CSV  ──→  Sort by Column  ──→  Compute Column  ──→  Export CSV
(source)       (transform)          (transform)          (sink)
```

- **Source nodes** (Load CSV, Load Multi CSV) have no inputs — they produce data.
- **Transform nodes** take one or more DataFrames in and output a modified DataFrame.
- **Sink nodes** (Export CSV) take a DataFrame in and write it to disk.

For a complete step-by-step tutorial using the included test data, see [Walkthrough Tutorial](Workflow_Builder/dataframeNode_pkg/docs/WALKTHROUGH.md).

## Package Structure

```
Workflow_Builder/
├── main.py                       # Ryven launcher (configures exec-flow mode)
└── dataframeNode_pkg/
    ├── nodes.py                  # Base classes and node registration
    ├── gui.py                    # GUI registration for all nodes
    ├── gui_utils.py              # Shared GUI utilities and widgets
    ├── dtype_utils.py            # Type conversion helpers
    ├── dataframe_nodes/          # General DataFrame operation nodes
    │   ├── nodes.py
    │   └── gui_dialogs.py
    ├── calibration_nodes/        # Calibration pipeline nodes
    │   ├── nodes.py
    │   └── gui_dialogs.py
    ├── physagg_nodes/            # Physiological aggregation nodes
    │   ├── nodes.py
    │   └── gui_dialogs.py
    ├── docs/
    │   ├── WALKTHROUGH.md        # Step-by-step tutorial with synthetic data
    │   └── PHYSAGG_NODES.md      # In-depth physagg node reference
    └── test/                     # Synthetic test data and example workflow
        ├── example_workflow.json
        ├── participants.csv
        ├── calibration_data.csv
        ├── calibration_data_raw.csv
        ├── exposure_data.csv
        ├── aggregated_data.csv
        └── scores.csv
```

## Further Reading

- [Walkthrough Tutorial](Workflow_Builder/dataframeNode_pkg/docs/WALKTHROUGH.md) — build a complete calibration and aggregation pipeline step-by-step using the included synthetic test data.
- [PhysAgg Nodes Reference](Workflow_Builder/dataframeNode_pkg/docs/PHYSAGG_NODES.md) — detailed documentation for the physiological aggregation nodes, including windowing modes and use cases.
