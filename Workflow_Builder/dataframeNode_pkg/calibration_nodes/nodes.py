import numpy as np
import pandas as pd
from ryven.node_env import *
from ..nodes import DataFrameNodeBase, myDataFrame


class CalibPupilDilationNode(DataFrameNodeBase):
    """Maps pupil dilation calibration medians from Data DF onto Target DF.

    For each grayscale value, filters Data DF to matching rows, looks up
    left/right median pupil dilation per participant, and adds them as new
    columns on Target DF (e.g. Calibration_PupilDilation_Left_128).
    """

    title = 'Calib: Pupil Dilation'
    init_inputs = [
        NodeInputType(label='Target DF'),
        NodeInputType(label='Data DF'),
    ]
    init_outputs = [
        NodeOutputType(label='Target DF'),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.merge_key_col: str | None = None
        self.shown_gray_col: str | None = None
        self.left_median_col: str | None = None
        self.right_median_col: str | None = None
        self.grayscale_values: list[int | float] = []  # Grayscale values to include in calibration.

    def get_state(self) -> dict:
        return {
            'merge_key_col': self.merge_key_col,
            'shown_gray_col': self.shown_gray_col,
            'left_median_col': self.left_median_col,
            'right_median_col': self.right_median_col,
            'grayscale_values': self.grayscale_values,
        }

    def set_state(self, data: dict, version):
        self.merge_key_col = data.get('merge_key_col')
        self.shown_gray_col = data.get('shown_gray_col')
        self.left_median_col = data.get('left_median_col')
        self.right_median_col = data.get('right_median_col')
        self.grayscale_values = data.get('grayscale_values', [])

    def isConfigured(self) -> bool:
        return bool(
            self.merge_key_col
            and self.shown_gray_col
            and self.left_median_col
            and self.right_median_col
            and self.grayscale_values
        )

    def _doUpdate(self):
        target_df = self.input(0).payload
        data_df = self.input(1).payload
        target_df = self._mapPupilDilationMedians(target_df, data_df)
        self.set_output_val(0, myDataFrame(target_df))

    def _mapPupilDilationMedians(self, target_df: pd.DataFrame, data_df: pd.DataFrame) -> pd.DataFrame:
        for value in self.grayscale_values:
            filtered_data = data_df[data_df[self.shown_gray_col] == value]
            median_dict = filtered_data.set_index(self.merge_key_col)[
                [self.left_median_col, self.right_median_col]].to_dict()

            col_left = f'Calibration_PupilDilation_Left_{value}'
            col_right = f'Calibration_PupilDilation_Right_{value}'

            target_df.loc[:, col_left] = target_df[self.merge_key_col].map(
                median_dict[self.left_median_col])
            target_df.loc[:, col_right] = target_df[self.merge_key_col].map(
                median_dict[self.right_median_col])

        return target_df


class CalibGroupbyStatsNode(DataFrameNodeBase):
    """Computes grouped aggregate statistics from Data DF and merges onto Target DF.

    Groups Data DF by a key column, computes configured stats (median/mean/std)
    for each metric column, and left-joins the results onto Target DF.
    """

    title = 'Calib: Groupby Stats'
    init_inputs = [
        NodeInputType(label='Target DF'),
        NodeInputType(label='Data DF'),
    ]
    init_outputs = [
        NodeOutputType(label='Target DF'),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.groupby_key: str | None = None
        self.metrics: list[tuple[str, tuple[str, str, str], tuple[str, str,str]]] = []

    def get_state(self) -> dict:
        return {
            'groupby_key': self.groupby_key,
            'metrics': [
                [val_col, list(stats), list(out_cols)]
                for val_col, stats, out_cols in self.metrics
            ],
        }

    def set_state(self, data: dict, version):
        self.groupby_key = data.get('groupby_key')
        self.metrics = [
            (entry[0], tuple(entry[1]), tuple(entry[2]))
            for entry in data.get('metrics', [])
        ]

    def isConfigured(self) -> bool:
        if not self.groupby_key or not self.metrics:
            return False
        for entry in self.metrics:
            if not isinstance(entry, (list, tuple)) or len(entry) != 3:
                return False
            value_col, stats, out_cols = entry
            if not value_col:
                return False
            if not isinstance(stats, (list, tuple)) or not stats:
                return False
            if not isinstance(out_cols, (list, tuple)) or not out_cols:
                return False
            if len(stats) != len(out_cols):
                return False
            if not all(c for c in out_cols):
                return False
            if not all(isinstance(s, str) and s in ('median', 'mean', 'std') for s in stats):
                return False
        return True

    def _doUpdate(self):
        target_df = self.input(0).payload
        data_df = self.input(1).payload
        final_df = self._computeStats(target_df,data_df)
        data = myDataFrame(final_df)
        self.set_output_val(0, data)

    def _computeStats(self, target_df: pd.DataFrame, data_df: pd.DataFrame) -> pd.DataFrame:
        for value_col, stats, out_cols in self.metrics:
            agg_spec = {}
            for stat, output_col in zip(stats, out_cols):
                agg_spec[output_col] = (value_col, stat)

            df_computed_stats = data_df.groupby(self.groupby_key).agg(**agg_spec)
            target_df = target_df.merge(
                df_computed_stats,
                left_on=self.groupby_key, right_index=True, how='left',
            )

        return target_df



class CalibThresholdFilterNode(DataFrameNodeBase):
    """Filters DataFrame rows by numeric threshold conditions with AND/OR logic.

    Each condition is (column, operator, value). Multiple conditions are
    chained with AND/OR connectors. Rows not meeting the combined condition
    are removed. Used to discard physiologically implausible values.
    """

    title = 'Calib: Threshold Filter'
    init_inputs = [
        NodeInputType(),
    ]
    init_outputs = [
        NodeOutputType(),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.conditions: list[tuple[str, str, int | float]] = []
        self.connectors: list[str] = []

    def get_state(self) -> dict:
        return {
            'conditions': [list(t) for t in self.conditions],
            'connectors': self.connectors,
        }

    def set_state(self, data: dict, version):
        self.conditions = [tuple(t) for t in data.get('conditions', [])]
        self.connectors = data.get('connectors', [])

    def isConfigured(self) -> bool:
        if not self.conditions:
            return False
        connectors = self.connectors or []
        if len(connectors) != len(self.conditions) - 1:
            return False
        for entry in self.conditions:
            if not isinstance(entry, (list, tuple)) or len(entry) != 3:
                return False
            col, op, val = entry
            if not col:
                return False
            if op not in ('>', '>=', '<', '<=', '==', '!='):
                return False
            if not isinstance(val, (int, float)):
                return False
        if not all(c in ('AND', 'OR') for c in connectors):
            return False
        return True

    def _doUpdate(self):
        df = self.input(0).payload
        mask = self._buildMask(df, self.conditions[0])
        for i, connector in enumerate(self.connectors):
            next_mask = self._buildMask(df, self.conditions[i + 1])
            if connector == 'AND':
                mask = mask & next_mask
            else:
                mask = mask | next_mask
        self.set_output_val(0, myDataFrame(df[mask]))

    @staticmethod
    def _buildMask(df, condition):
        col, op, val = condition
        ops = {
            '>': df[col] > val,
            '>=': df[col] >= val,
            '<': df[col] < val,
            '<=': df[col] <= val,
            '==': df[col] == val,
            '!=': df[col] != val,
        }
        return ops[op]




class CalibRmssdNode(DataFrameNodeBase):
    """Computes RMSSD (heart rate variability) per participant group and merges onto Target DF.

    For each group in Data DF, computes sqrt(mean(diff(rr_intervals)^2)).
    Maps the result onto Target DF as a new column using the groupby key.

    Config:
    - groupby_key: column name to group on (also used as merge key on target DF)
    - data_column: column containing the RR interval values
    - output_column_name: name for the computed RMSSD output column
    """

    title = 'Calib: Compute RMSSD'
    init_inputs = [
        NodeInputType(label='Target DF'),
        NodeInputType(label='Data DF'),
    ]
    init_outputs = [
        NodeOutputType(label='Target DF'),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.groupby_key: str | None = None
        self.data_column: str | None = None
        self.output_column_name: str | None = None

    def get_state(self) -> dict:
        return {
            'groupby_key': self.groupby_key,
            'data_column': self.data_column,
            'output_column_name': self.output_column_name,
        }

    def set_state(self, data: dict, version):
        self.groupby_key = data.get('groupby_key')
        self.data_column = data.get('data_column')
        self.output_column_name = data.get('output_column_name')

    def isConfigured(self) -> bool:
        return bool(self.groupby_key and self.data_column and self.output_column_name)

    def _doUpdate(self):
        target_df = self.input(0).payload
        data_df = self.input(1).payload
        rmssd_map = {}
        for key, group in data_df.groupby(self.groupby_key):
            vals = group[self.data_column].values
            if len(vals) > 1:
                rmssd_map[key] = np.sqrt(np.mean(np.diff(vals) ** 2))
            else:
                rmssd_map[key] = np.nan
        target_df[self.output_column_name] = target_df[self.groupby_key].map(rmssd_map)
        self.set_output_val(0, myDataFrame(target_df))


class CalibRelativeThresholdNode(DataFrameNodeBase):
    """Iteratively removes RR interval outliers using an age-dependent threshold.

    Groups Data DF by participant, computes threshold = -age/3 + 45, then
    repeatedly removes values whose percentage deviation from the neighbor
    average exceeds that threshold. Outputs the cleaned Data DF.

    Note: Only uses Data DF (input 1). Target DF (input 0) is declared for
    wiring consistency with other calibration nodes but is not read.
    """

    title = 'Calib: Relative Threshold Filter'
    init_inputs = [
        NodeInputType(label='Target DF'),
        NodeInputType(label='Data DF'),
    ]
    init_outputs = [
        NodeOutputType(label='Target DF'),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.groupby_column: str | None = None
        self.age_column: str | None = None
        self.rr_interval_column: str | None = None
        self.max_iterations: int = 20

    def get_state(self) -> dict:
        return {
            'groupby_column': self.groupby_column,
            'age_column': self.age_column,
            'rr_interval_column': self.rr_interval_column,
            'max_iterations': self.max_iterations,
        }

    def set_state(self, data: dict, version):
        self.groupby_column = data.get('groupby_column')
        self.age_column = data.get('age_column')
        self.rr_interval_column = data.get('rr_interval_column')
        self.max_iterations = data.get('max_iterations', 20)

    def isConfigured(self) -> bool:
        if not self.groupby_column or not self.age_column or not self.rr_interval_column:
            return False
        return isinstance(self.max_iterations, int) and self.max_iterations >= 1

    def _doUpdate(self):
        data_df = self.input(1).payload
        parts = []
        for key, group in data_df.groupby(self.groupby_column):
            age = group[self.age_column].iloc[0]
            parts.append(self._applyRelativeThreshold(group, age))
        result = pd.concat(parts) if parts else pd.DataFrame()
        self.set_output_val(0, myDataFrame(result))

    def _applyRelativeThreshold(self, data, age):
        # Age-dependent threshold: younger participants get stricter (higher)
        # thresholds. Formula from the original VR experiment analysis pipeline.
        threshold = -age / 3 + 45
        col = self.rr_interval_column
        for _ in range(self.max_iterations):
            removed = []
            for i in range(1, len(data) - 1):
                curr = data.iloc[i][col]
                prev = data.iloc[i - 1][col]
                nxt = data.iloc[i + 1][col]
                # Remove if the percentage deviation from the neighbor average exceeds threshold
                if (abs(curr - (prev + nxt) / 2) / curr) * 100 > threshold:
                    removed.append(i)
            if not removed:
                break
            data = data.drop(data.index[removed])
        return data
