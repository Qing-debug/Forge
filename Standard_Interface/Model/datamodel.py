from logging import exception

import pandas as pd
from typing import override
from returns.result import Failure, Success, Result
from dataclasses import dataclass



@dataclass
class DataFrameEntry:
    df: pd.DataFrame
    name: str

class DataModel:
    _singleton = None
    _singleton_exist = False

    @override
    def __new__(cls, *args, **kwargs):
        if not cls._singleton_exist:
            cls._singleton = super().__new__(cls)
            return cls._singleton
        return cls._singleton

    @override
    def __init__(self):
        if not self.__class__._singleton_exist:
            self.loaded_dataframes: list[DataFrameEntry] = []
            self.__class__._singleton_exist = True

    def loadDataframeEntryFromFilePath(self, file_path_str: str, file_name: str) -> Result[str, str]:
        try:
            df = pd.read_csv(file_path_str)
            print("Successfully created dataframe")
        except FileNotFoundError as e:
            return Failure(e)

        add_df_to_memory_res = self._add_df_to_memory(df, file_name)
        return add_df_to_memory_res

    def loadDataframeEntryFromPandasDF(self, df: pd.DataFrame, df_name: str) -> Success[str]:
        add_df_to_memory_res = self._add_df_to_memory(df, df_name)
        return add_df_to_memory_res

    def _add_df_to_memory(self, df: pd.DataFrame, df_name: str) -> Success[str]:
        df_entry = DataFrameEntry(df, df_name)
        self.loaded_dataframes.append(df_entry)
        return Success("Successfully added dataframe to memory")

    def getDataframesInMemory(self) -> list[DataFrameEntry]:
        return self.loaded_dataframes

    def getSelectedDataframe(self, df_name: str) -> tuple[str, pd.DataFrame] | None:
        for df_entry in self.loaded_dataframes:
            if df_entry.name == df_name:
                return df_entry.name, df_entry.df

        return None

    def overwriteDFInExistingDataframeEntry(self, df: pd.DataFrame, df_name: str) -> Result[str, str]:
        def getDataFrameEntry(name: str):
            for entry in self.loaded_dataframes:
                if entry.name == name:
                    return entry
            return None

        df_entry = getDataFrameEntry(df_name)
        if df_entry is None:
            return Failure(f"Unable to locate DF Entry with the given name:{df_name} ")
        print(f"I'm in model's overwrite function: current DF = f{id(df_entry.df)}, new DF = f{id(df)}")
        df_entry.df = df
        return Success(f"Successfully replaced dataframe in existing DF entry with new dataframe")

    def replaceValueInColumn(self, df: pd.DataFrame, col_header: 'str', replacement_map: dict) -> Result[str, str]:
        column_with_new_values = df[col_header].copy()
        column_with_new_values.replace(replacement_map, inplace = True)

        old_values = [old_value for old_value, _ in list(replacement_map.items())]
        #checks if all values were replaced with their corresponding values
        for old_value in old_values:
            mask = df[col_header] == old_value
            filtered = df[mask]
            indexes = filtered.index
            for index in indexes:
                replaced_value = column_with_new_values.loc[index]
                # if check to see if replacing actually occurred
                if old_value == replaced_value:
                    return Failure("Failed to replace value. Original Dataframe not affected. terminating operation now.")
        df[col_header] = column_with_new_values
        return Success("Successfully replaced all specified values with new values")

    def mergeDataframes(self, merge_parameters: dict) -> pd.DataFrame:
        merged_df = pd.merge(**merge_parameters)
        return merged_df

    def concatDataframes(self, dfs_to_concat: list[pd.DataFrame], concat_parameters: dict) -> pd.DataFrame:
        return pd.concat(objs = dfs_to_concat, **concat_parameters)

    def withinDataframeAggregation(self, df: pd.DataFrame, mathematical_expression: str) -> pd.DataFrame:
        return df.eval(mathematical_expression, engine='python')

    def saveDataframeAsCSV(self, df: pd.DataFrame, file_path: str) -> Result[str, str]:
        try:
            df.to_csv(file_path, index=False)
        except PermissionError as e:
            return Failure(e)
        except FileNotFoundError as e:
            return Failure(e)
        except Exception as e:
            return Failure(e)

        return Success("Successfully Saved Dataframe")

    def sortByColumn(self, df: pd.DataFrame, columns_to_sort_by: list[str], lexigraphic_sort_per_column: list[bool], ignore_index: bool) -> Result[pd.DataFrame, str]:

        sorted_df = None
        try:
            sorted_df = df.sort_values(by = columns_to_sort_by, ascending= lexigraphic_sort_per_column, ignore_index = ignore_index)
        except KeyError as e:
            return Failure("Specified column to sort by does not exist.")
        except TypeError as e:
            return Failure("Unable to sort column due to data types not suitable for comparison operator")

        return Success(sorted_df)

    def renameColumnHeaders(self, df: pd.DataFrame, rename_mapping: dict[str, str]) -> Result[str,str]:
        try:
            df.rename(columns = rename_mapping, errors = "raise", inplace = True)
        except KeyError as e:
            return Failure(e)
        except Exception as e:
            return Failure(e)

        return Success("Sucessfully renamed column(s)")


    def reorderColumns(self, df: pd.DataFrame, anchor_column: str, columns_to_move: list[str]):
        df_headers = df.columns

        static_headers = []
        for header in df_headers:
            if header not in columns_to_move:
                static_headers.append(header)

        anchor_index = static_headers.index(anchor_column)
        new_order = static_headers[:anchor_index + 1] + columns_to_move + static_headers[anchor_index + 1:]
        return df[new_order]















