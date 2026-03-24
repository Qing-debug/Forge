import pandas as pd
from ryven.node_env import *
from ..dtype_utils import toNumpyDtype
from ..nodes import DataFrameNodeBase, myDataFrame


class ReplaceValueNode(DataFrameNodeBase):
    """Replaces values in a single column using a user-defined mapping.

    Mode 'specific': replaces exactly one value.
    Mode 'all': replaces every unique value and casts the column to a target dtype.
    """

    title = 'Replace Value'
    init_inputs = [NodeInputType()]
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.mode: str = 'specific'
        self.column_header: str | None = None
        self.replacement_type: str | None = None
        self.mappings: list[dict[str, str]] = []

    def get_state(self) -> dict:
        return {
            'mode': self.mode,
            'column_header': self.column_header,
            'replacement_type': self.replacement_type,
            'mappings': self.mappings,
        }

    def set_state(self, data: dict, version):
        self.mode = data.get('mode', 'specific')
        self.column_header = data.get('column_header')
        self.replacement_type = data.get('replacement_type')
        self.mappings = data.get('mappings', [])

    def isConfigured(self) -> bool:
        if not self.column_header or not self.mappings:
            return False
        mode = self.mode or 'specific'
        if mode == 'specific':
            return len(self.mappings) == 1
        if mode == 'all':
            return (
                len(self.mappings) >= 1
                and self.replacement_type in ('string', 'integer', 'float')
            )
        return False

    def _doUpdate(self):
        df = self.input(0).payload
        data = myDataFrame(self._replaceValue(df))
        self.set_output_val(0, data)

    def _replaceValue(self, df: pd.DataFrame) -> pd.DataFrame:
        type_converted_replacement_map = {}
        if self.mode == 'specific':
            row = self.mappings[0]
            current_value, new_value = row.get('old'), row.get('new')
            current_value = df[self.column_header].dtype.type(current_value)
            new_value = df[self.column_header].dtype.type(new_value)
            type_converted_replacement_map.update({current_value: new_value})
        elif self.mode == 'all':
            # TODO: Validate that mappings cover every unique value in the column (exact 1:1).
            #  Currently a user can provide partial mappings in 'all' mode, which defeats
            #  the purpose of choosing a replacement_type - unmapped values keep their
            #  original type, resulting in a mixed-type (object dtype) column.
            for row in self.mappings:
                current_value, new_value = row.get('old'), row.get('new')
                current_value = df[self.column_header].dtype.type(current_value)
                new_value = toNumpyDtype(new_value, self.replacement_type)
                type_converted_replacement_map.update({current_value: new_value})

        series = df[self.column_header].replace(type_converted_replacement_map)
        df[self.column_header] = series
        return df


class ComputeColumnNode(DataFrameNodeBase):
    """Creates a new column by evaluating a formula via df.eval().

    Config: new_column (output column name), formula (pandas eval expression).
    """

    title = 'Compute Column'
    init_inputs = [NodeInputType()]
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.new_column: str | None = None
        self.formula: str | None = None

    def get_state(self) -> dict:
        return {
            'new_column': self.new_column,
            'formula': self.formula,
        }

    def set_state(self, data: dict, version):
        self.new_column = data.get('new_column')
        self.formula = data.get('formula')

    def isConfigured(self) -> bool:
        return bool(self.new_column and self.formula)

    def _doUpdate(self):
        df = self.input(0).payload
        expression = f"{self.new_column}={self.formula}"
        df = df.eval(expression, engine='python')
        self.set_output_val(0, myDataFrame(df))



class SortByColumnNode(DataFrameNodeBase):
    """Sorts the input DataFrame by one or more columns."""

    title = 'Sort by Column'
    init_inputs = [NodeInputType()]
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.sort_columns: list[str] = []
        self.ascending_list: list[bool] = []
        self.ignore_index: bool = False

    def get_state(self) -> dict:
        return {
            'sort_columns': self.sort_columns,
            'ascending_list': self.ascending_list,
            'ignore_index': self.ignore_index,
        }

    def set_state(self, data: dict, version):
        self.sort_columns = data.get('sort_columns', [])
        self.ascending_list = data.get('ascending_list', [])
        self.ignore_index = data.get('ignore_index', False)

    def isConfigured(self) -> bool:
        if not self.sort_columns:
            return False
        if self.ascending_list:
            if len(self.ascending_list) != len(self.sort_columns):
                return False
            if not all(isinstance(v, bool) for v in self.ascending_list):
                return False
        return True

    def _doUpdate(self):
        df = self.input(0).payload
        df = self.sortByColumn(df)
        data = myDataFrame(df)
        self.set_output_val(0, data)

    def sortByColumn(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values(by = self.sort_columns, ascending = self.ascending_list, ignore_index= self.ignore_index)

class RenameColumnNode(DataFrameNodeBase):
    """Renames one or more columns using a user-defined old-to-new mapping."""

    title = 'Rename Column'
    init_inputs = [NodeInputType()]
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.rename_mappings: list[dict[str, str]] = []  # e.g. [{'old': 'col1', 'new': 'col1_renamed'}].

    def get_state(self) -> dict:
        return {'rename_mappings': self.rename_mappings}

    def set_state(self, data: dict, version):
        self.rename_mappings = data.get('rename_mappings', [])

    def isConfigured(self) -> bool:
        if not self.rename_mappings:
            return False
        return all(isinstance(m, dict) and m.get('old') and m.get('new') for m in self.rename_mappings)

    def _doUpdate(self):
        df = self.input(0).payload #payload written to return a copy of df so we can do in place modifcations without worry
        data = myDataFrame(self.renameColumn(df)) #payload
        self.set_output_val(0, data)

    def renameColumn(self, df) -> pd.DataFrame:
        rename_map = {}
        for row in self.rename_mappings:
            value_to_be_replaced, val_to_replace_with = row.get("old"), row.get("new")
            rename_map.update({value_to_be_replaced:val_to_replace_with})

        df.rename(columns=rename_map, errors="raise", inplace=True)
        return df


class ReorderColumnNode(DataFrameNodeBase):
    """Repositions selected columns to appear immediately after an anchor column."""

    title = 'Reorder Column'
    init_inputs = [NodeInputType()]
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.anchor_column: str | None = None
        self.columns_to_move: list[str] = []

    def get_state(self) -> dict:
        return {
            'anchor_column': self.anchor_column,
            'columns_to_move': self.columns_to_move,
        }

    def set_state(self, data: dict, version):
        self.anchor_column = data.get('anchor_column')
        self.columns_to_move = data.get('columns_to_move', [])

    def isConfigured(self) -> bool:
        return bool(self.anchor_column and self.columns_to_move)

    def _doUpdate(self):
        df = self.input(0).payload
        df = self.reorderColumns(df)
        data = myDataFrame(df)
        self.set_output_val(0, data)

    def reorderColumns(self, df: pd.DataFrame) -> pd.DataFrame:
        df_headers = df.columns

        static_headers = []
        for header in df_headers:
            if header not in self.columns_to_move:
                static_headers.append(header)

        anchor_index = static_headers.index(self.anchor_column)
        new_order = static_headers[:anchor_index + 1] + self.columns_to_move + static_headers[anchor_index + 1:]
        return df[new_order]

class MergeNode(DataFrameNodeBase):
    """Merges two dataframes via pd.merge().

    Two input ports (left=0, right=1). Config: how (join type),
    merge_conditions (column pairs), suffix_left/suffix_right.
    """

    title = 'Merge'
    init_inputs = [NodeInputType(), NodeInputType()]
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.how: str | None = None
        self.merge_conditions: list[tuple[str, str]] = []
        self.suffix_left: str = '_left'
        self.suffix_right: str = '_right'

    def get_state(self) -> dict:
        return {
            'how': self.how,
            'merge_conditions': [list(t) for t in self.merge_conditions],
            'suffix_left': self.suffix_left,
            'suffix_right': self.suffix_right,
        }

    def set_state(self, data: dict, version):
        self.how = data.get('how')
        self.merge_conditions = [tuple(t) for t in data.get('merge_conditions', [])]
        self.suffix_left = data.get('suffix_left', '_left')
        self.suffix_right = data.get('suffix_right', '_right')

    def isConfigured(self) -> bool:
        if self.how not in ('inner', 'outer', 'left', 'right'):
            return False
        if not self.merge_conditions:
            return False
        for entry in self.merge_conditions:
            if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                return False
            if not entry[0] or not entry[1]:
                return False
        if not self.suffix_left or not self.suffix_right:
            return False
        if self.suffix_left == self.suffix_right:
            return False
        return True

    def _doUpdate(self):
        left_df = self.input(0).payload
        right_df = self.input(1).payload
        merged_df = self._merge(left_df, right_df)
        self.set_output_val(0, myDataFrame(merged_df))

    def _merge(self, left_df: pd.DataFrame, right_df: pd.DataFrame) -> pd.DataFrame:
        left_cols = [pair[0] for pair in self.merge_conditions]
        right_cols = [pair[1] for pair in self.merge_conditions]

        if left_cols == right_cols:
            return pd.merge(
                left_df, right_df,
                how=self.how, on=left_cols,
                suffixes=(self.suffix_left, self.suffix_right),
            )
        else:
            return pd.merge(
                left_df, right_df,
                how=self.how, left_on=left_cols, right_on=right_cols,
                suffixes=(self.suffix_left, self.suffix_right),
            )


class ConcatNode(DataFrameNodeBase):
    """Concatenates up to 6 input DataFrames along the configured axis."""

    title = 'Concat'
    init_inputs = [
        NodeInputType(),
        NodeInputType(),
        NodeInputType(),
        NodeInputType(),
        NodeInputType(),
        NodeInputType(),
    ]
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.axis: str = '0'
        self.join: str = 'outer'
        self.ignore_index: bool = False
        self.keys: str | None = None

    def get_state(self) -> dict:
        return {
            'axis': self.axis,
            'join': self.join,
            'ignore_index': self.ignore_index,
            'keys': self.keys,
        }

    def set_state(self, data: dict, version):
        self.axis = data.get('axis', '0')
        self.join = data.get('join', 'outer')
        self.ignore_index = data.get('ignore_index', False)
        self.keys = data.get('keys')

    def isConfigured(self) -> bool:
        if self.axis not in ('0', '1'):
            return False
        return self.join in ('inner', 'outer')

    def _doUpdate(self):
        data = []

        for x in range(6):
            port_data = self.input(x)
            if port_data is not None:
                data.append(port_data.payload)
        df = self.concatDFs(data)
        self.set_output_val(0, myDataFrame(df))

    def concatDFs(self, dfs_to_concat: list[pd.DataFrame]):
        concat_df = pd.concat(objs = dfs_to_concat, axis = int(self.axis), join = self.join, ignore_index= self.ignore_index)
        return concat_df


class LoadCSVNode(DataFrameNodeBase):
    """Configuration-only node.

    No inputs - this is a source node. Triggered by the Run button (inp=-1).
    Currently does not load a CSV or emit a dataframe here.
    """

    title = 'Load CSV'
    init_inputs = []
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.file_path: str | None = None

    def get_state(self) -> dict:
        return {'file_path': self.file_path}

    def set_state(self, data: dict, version):
        self.file_path = data.get('file_path')

    def isConfigured(self) -> bool:
        return bool(self.file_path)

    def _doUpdate(self):
        df = pd.read_csv(self.file_path)
        data = myDataFrame(df)
        self.set_output_val(0, data)

class LoadMultiCSVNode(DataFrameNodeBase):
    """Source node that loads multiple CSV files and concatenates them (axis=0).

    No inputs - this is a source node. The user selects multiple CSV files
    via a file browser; at runtime the node reads and concatenates them.
    """

    title = 'Load Multi CSV'
    init_inputs = []
    init_outputs = [NodeOutputType()]

    def __init__(self, params):
        super().__init__(params)
        self.file_paths: list[str] = []

    def get_state(self) -> dict:
        return {'file_paths': self.file_paths}

    def set_state(self, data: dict, version):
        self.file_paths = data.get('file_paths', [])

    def isConfigured(self) -> bool:
        return bool(self.file_paths)

    def _doUpdate(self):
        dfs = [pd.read_csv(fp) for fp in self.file_paths]
        df = pd.concat(dfs, axis=0, ignore_index=True)
        self.set_output_val(0, myDataFrame(df))


class ExportCSVNode(DataFrameNodeBase):
    """Sink node that exports the input dataframe to a CSV file.

    One input port, no outputs. The user configures the save path via a
    file-save dialog; at runtime the node writes the dataframe with
    df.to_csv(path, index=False).
    """

    title = 'Export CSV'
    init_inputs = [NodeInputType()]
    init_outputs = []

    def __init__(self, params):
        super().__init__(params)
        self.file_path: str | None = None

    def get_state(self) -> dict:
        return {'file_path': self.file_path}

    def set_state(self, data: dict, version):
        self.file_path = data.get('file_path')

    def isConfigured(self) -> bool:
        return bool(self.file_path)

    def _doUpdate(self):
        df = self.input(0).payload
        df.to_csv(self.file_path, index=False)


class PrintNode(DataFrameNodeBase):
    """Sink node that prints the input dataframe to the console.

    No configuration required - always considered configured.
    Triggered by the Run button (inp=-1), pulls data from upstream via self.input().
    """

    title = 'Print DataFrame'
    init_inputs = [NodeInputType()]
    init_outputs = []

    def isConfigured(self) -> bool:
        return True

    def _doUpdate(self):
        data = self.input(0)
        df = data.payload
        if df is not None:
            if isinstance(df, pd.DataFrame):
                print(f'\n--- {self.title} (node #{self.global_id}) ---')
                print(df.to_string())
                print(f'--- shape: {df.shape} ---\n')
            else:
                print(f'\n--- {self.title} (node #{self.global_id}) ---')
                print(df)
                print('--- (not a DataFrame) ---\n')
