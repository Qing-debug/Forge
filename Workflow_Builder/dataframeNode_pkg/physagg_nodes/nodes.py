import numpy as np
import pandas as pd
from ryven.node_env import *
from ..nodes import DataFrameNodeBase, myDataFrame



class PhysAggNodeBase(DataFrameNodeBase):
    """Base class for physiological aggregation nodes.

    Provides shared configuration for groupby key mappings, extra filters,
    and window mode (full window vs. before-start time windowing).
    Subclasses only need to define ``title`` and ``_doUpdate()``.

    Two inputs: Target DF (input 0) receives new columns; Exposure DF (input 1)
    provides the source data to aggregate.
    """

    init_inputs = [
        NodeInputType(label='Target DF'),
        NodeInputType(label='Exposure DF'),
    ]
    init_outputs = [
        NodeOutputType(label='Target DF'),
    ]

    def __init__(self, params):
        super().__init__(params)
        self.aggregation_name: str | None = None
        self.groupby_key_mappings: list[tuple[str, str]] = []  # (target_col, exposure_col) pairs
        self.extra_filters: list[tuple[str, str]] = []  # (exposure_col, value) pairs
        self.window_mode: str = 'full'  # 'full' or 'before_start'
        self.time_window: int = 60  # seconds, used only in 'before_start' mode
        self.timestamp_column: str = 'Unity_Timestamp'
        self.target_match_column: str | None = None  # e.g. 'Scene_Name'
        self.exposure_match_column: str | None = None  # e.g. 'Shown_Scene'

    def _get_base_state(self) -> dict:
        """Serialize shared aggregation config fields."""
        return {
            'aggregation_name': self.aggregation_name,
            'groupby_key_mappings': [list(t) for t in self.groupby_key_mappings],
            'extra_filters': [list(t) for t in self.extra_filters],
            'window_mode': self.window_mode,
            'time_window': self.time_window,
            'timestamp_column': self.timestamp_column,
            'target_match_column': self.target_match_column,
            'exposure_match_column': self.exposure_match_column,
        }

    def _set_base_state(self, data: dict):
        """Restore shared aggregation config fields."""
        self.aggregation_name = data.get('aggregation_name')
        self.groupby_key_mappings = [tuple(t) for t in data.get('groupby_key_mappings', [])]
        self.extra_filters = [tuple(t) for t in data.get('extra_filters', [])]
        self.window_mode = data.get('window_mode', 'full')
        self.time_window = data.get('time_window', 60)
        self.timestamp_column = data.get('timestamp_column', 'Unity_Timestamp')
        self.target_match_column = data.get('target_match_column')
        self.exposure_match_column = data.get('exposure_match_column')

    def _isBaseConfigured(self) -> bool:
        """Check whether shared aggregation fields are valid."""
        if not self.aggregation_name or not self.groupby_key_mappings:
            return False
        if self.window_mode == 'before_start':
            if not self.target_match_column or not self.exposure_match_column:
                return False
        return True

    def _getExposureGroup(self, row: pd.Series, exposure_df: pd.DataFrame) -> pd.DataFrame:
        """Filter exposure data to the rows matching a single target row.

        Applies groupby key mappings, extra filters, and (if window_mode is
        'before_start') restricts to a time window ending at the earliest
        timestamp of the matched scene.
        """
        mask = pd.Series(True, index=exposure_df.index)
        for target_col, exposure_col in self.groupby_key_mappings:
            mask = mask & (exposure_df[exposure_col] == row[target_col])
        for exposure_col, value in self.extra_filters:
            col_dtype = exposure_df[exposure_col].dtype
            try:
                typed_value = col_dtype.type(value)
            except (ValueError, TypeError):
                typed_value = value
            mask = mask & (exposure_df[exposure_col] == typed_value)
        group = exposure_df[mask]
        if self.window_mode == 'before_start' and len(group) > 0:
            scene_mask = group[self.exposure_match_column] == row[self.target_match_column]
            scene_group = group[scene_mask]
            if len(scene_group) > 0:
                start_time = scene_group[self.timestamp_column].min()
                group = group[
                    (group[self.timestamp_column] <= start_time) &
                    (group[self.timestamp_column] >= start_time - pd.Timedelta(seconds=self.time_window))
                ]
        return group


class PhysStatsAggNode(PhysAggNodeBase):
    """Computes descriptive statistics (median/mean/std/min/max) for configured
    columns from exposure data and merges results into the target DataFrame.
    """

    title = 'Phys: Stats Aggregation'

    def __init__(self, params):
        super().__init__(params)
        # Each dict: {source_column, output_label, lower_bound?, upper_bound?, filter_value?}
        self.column_configs: list[dict] = []
        self.stats_to_compute: list[str] = ['median', 'mean', 'std', 'min', 'max']

    def get_state(self) -> dict:
        return {
            **self._get_base_state(),
            'column_configs': self.column_configs,
            'stats_to_compute': self.stats_to_compute,
        }

    def set_state(self, data: dict, version):
        self._set_base_state(data)
        self.column_configs = data.get('column_configs', [])
        self.stats_to_compute = data.get('stats_to_compute', ['median', 'mean', 'std', 'min', 'max'])

    def isConfigured(self) -> bool:
        if not self._isBaseConfigured():
            return False
        return bool(self.column_configs) and bool(self.stats_to_compute)

    def _doUpdate(self):
        target_df = self.input(0).payload
        exposure_df = self.input(1).payload

        def _compute_for_row(row):
            group = self._getExposureGroup(row, exposure_df)
            results = {}
            for cfg in self.column_configs:
                col = cfg['source_column']
                label = cfg['output_label']
                data = group[col].copy()
                lb = cfg.get('lower_bound')
                ub = cfg.get('upper_bound')
                fv = cfg.get('filter_value')
                # Strict inequality (excluding boundary values) to match dan_script.py
                if lb is not None:
                    data = data[data > lb]
                if ub is not None:
                    data = data[data < ub]
                if fv is not None:
                    data = data[data != fv]
                if len(data) > 0:
                    stat_funcs = {
                        'median': data.median(), 'mean': data.mean(),
                        'std': data.std(), 'min': data.min(), 'max': data.max(),
                    }
                else:
                    stat_funcs = {s: np.nan for s in ['median', 'mean', 'std', 'min', 'max']}
                for stat in self.stats_to_compute:
                    col_name = f'{self.aggregation_name}_{stat.capitalize()}_{label}'
                    results[col_name] = stat_funcs[stat]
            return pd.Series(results)

        new_cols = target_df.apply(_compute_for_row, axis=1)
        target_df = pd.concat([target_df, new_cols], axis=1)
        self.set_output_val(0, myDataFrame(target_df))


class PhysRmssdAggNode(PhysAggNodeBase):
    """Computes RMSSD (root mean square of successive differences) of RR
    intervals from exposure data for each target row.

    RR intervals outside [lower_bound, upper_bound] are excluded before
    computing RMSSD - typical physiologically valid range is 200-2000 ms.
    """

    title = 'Phys: RMSSD Aggregation'

    def __init__(self, params):
        super().__init__(params)
        self.rr_column: str = 'Polar_RR_Interval'
        self.lower_bound: float = 200  # typical physiologically valid RR lower bound (ms)
        self.upper_bound: float = 2000  # typical physiologically valid RR upper bound (ms)
        self.output_label: str = 'RR_RMSSD'

    def get_state(self) -> dict:
        return {
            **self._get_base_state(),
            'rr_column': self.rr_column,
            'lower_bound': self.lower_bound,
            'upper_bound': self.upper_bound,
            'output_label': self.output_label,
        }

    def set_state(self, data: dict, version):
        self._set_base_state(data)
        self.rr_column = data.get('rr_column', 'Polar_RR_Interval')
        self.lower_bound = data.get('lower_bound', 200)
        self.upper_bound = data.get('upper_bound', 2000)
        self.output_label = data.get('output_label', 'RR_RMSSD')

    def isConfigured(self) -> bool:
        if not self._isBaseConfigured():
            return False
        return bool(self.rr_column) and bool(self.output_label)

    def _doUpdate(self):
        target_df = self.input(0).payload
        exposure_df = self.input(1).payload
        out_col = f'{self.aggregation_name}_{self.output_label}'

        def _compute_rmssd(row):
            group = self._getExposureGroup(row, exposure_df)
            rr = group[self.rr_column]
            rr = rr[(rr > self.lower_bound) & (rr < self.upper_bound)]
            if len(rr) > 1:
                return np.sqrt(np.mean(np.diff(rr.values) ** 2))
            return np.nan

        target_df[out_col] = target_df.apply(_compute_rmssd, axis=1)
        self.set_output_val(0, myDataFrame(target_df))


class PhysCumulativeAggNode(PhysAggNodeBase):
    """Computes cumulative sum of positive successive differences for
    configured columns - used for measures like cumulative EDA.
    """

    title = 'Phys: Cumulative Aggregation'

    def __init__(self, params):
        super().__init__(params)
        # Each dict: {source_column, output_label, use_abs (bool)}
        self.column_configs: list[dict] = []

    def get_state(self) -> dict:
        return {
            **self._get_base_state(),
            'column_configs': self.column_configs,
        }

    def set_state(self, data: dict, version):
        self._set_base_state(data)
        self.column_configs = data.get('column_configs', [])

    def isConfigured(self) -> bool:
        if not self._isBaseConfigured():
            return False
        return bool(self.column_configs)

    def _doUpdate(self):
        target_df = self.input(0).payload
        exposure_df = self.input(1).payload

        def _compute_for_row(row):
            group = self._getExposureGroup(row, exposure_df)
            results = {}
            for cfg in self.column_configs:
                col = cfg['source_column']
                label = cfg['output_label']
                use_abs = cfg.get('use_abs', False)
                out_col = f'{self.aggregation_name}_{label}'
                if len(group) > 1:
                    col_data = np.abs(group[col].values) if use_abs else group[col].values
                    diffs = col_data[1:] - col_data[:-1]
                    diffs[diffs < 0] = 0
                    results[out_col] = np.sum(diffs)
                else:
                    results[out_col] = np.nan
            return pd.Series(results)

        new_cols = target_df.apply(_compute_for_row, axis=1)
        target_df = pd.concat([target_df, new_cols], axis=1)
        self.set_output_val(0, myDataFrame(target_df))
