import pandas as pd
from pandas import DataFrame
from pathlib import Path
from Forge.Standard_Interface.Model import datamodel
from Forge.Standard_Interface.View import dataview
from typing import override
from returns.pipeline import is_successful
from Forge.Standard_Interface.Shared_Contracts.shared_contracts import to_numpy_dtype
from returns.result import Result


class DataPresenter:
    _singleton = None
    _singleton_exist = False

    @override
    def __new__(cls, model: datamodel.DataModel, view: "dataview.DataView"):
        if not cls._singleton_exist:
            cls._singleton = super().__new__(cls)
            return cls._singleton
        return cls._singleton

    @override
    def __init__(self, model: datamodel.DataModel, view: dataview.DataView):
        if not self.__class__._singleton_exist:
            self.model = model
            self.view = view
            self.__class__._singleton_exist = True

    def loadDataframeEntryFromFilePathAndUpdateView(self, file_path_str: str, file_name: str):
        if not isinstance(file_path_str, str):
            print("invalid file path type.")
            return

        load_data_in_memory_res = self.model.loadDataframeEntryFromFilePath(file_path_str, file_name)
        if not is_successful(load_data_in_memory_res):
            print(load_data_in_memory_res.failure())
            return
        print(load_data_in_memory_res.unwrap())

        self.view.updateDFNameContainer([df.name for df in self.model.getDataframesInMemory()])

    def loadDataframeEntryFromPandasDFAndUpdateView(self, df: pd.DataFrame, df_name: str):
        if not isinstance(df, pd.DataFrame):
            print("type of passed in value for df parameter is invalid.")
            return
        load_data_in_memory_res = self.model.loadDataframeEntryFromPandasDF(df, df_name)
        print(load_data_in_memory_res.unwrap())

        self.view.updateDFNameContainer([df.name for df in self.model.getDataframesInMemory()])

    def getSelectedDataframeAndLoadOnView(self, df_name: str):
        res = self.model.getSelectedDataframe(df_name)
        if res is None:
            print("Unable to find (and thus load) selected dataframe in memory")
            return
        name, df = res
        self.view.loadSelectedDF(name, df)

    def getDataFrame(self, df_name: str) -> tuple[str, pd.DataFrame] | None:
        res = self.model.getSelectedDataframe(df_name)
        if res is None:
            print(f"Unable to find dataframe with name: {df_name}")
            return None
        name, df = res
        return name, df


    def overwriteDFInExistingDataframeEntry(self, df: pd.DataFrame, df_name: str):
        overwrite_res = self.model.overwriteDFInExistingDataframeEntry(df, df_name)
        self.view.redrawTables()
        if not is_successful(overwrite_res):
            print(overwrite_res.failure())
            return
        print(overwrite_res.unwrap())


    def replaceValueInColumn(self, identifier: str, col_header: str, replacement_map: dict, selected_type_for_new_value: str | None) -> Result[str, str]:
        res = self.model.getSelectedDataframe(identifier)
        if res is None:
            print(f"Unable to find dataframe with name: {identifier}. Terminating value replacement operaton")
            return None

        _, df = res

        unique_values = df[col_header].unique()
        type_converted_replacement_map = {}

        #create replacement map for single replacement
        if len(replacement_map) == 1:
            current_value, new_value = list(replacement_map.items())[0]
            current_value = df[col_header].dtype.type(current_value)
            new_value = df[col_header].dtype.type(new_value) #convert new_value to underlying type of the values in the targeted column so they match
            type_converted_replacement_map.update({current_value: new_value})

        #create replacement map for full replacement of all values in the targeted column
        elif len(replacement_map) == len(unique_values):
            for current_value, new_value in list(replacement_map.items()):
                current_value = df[col_header].dtype.type(current_value)
                new_value = to_numpy_dtype(new_value, selected_type_for_new_value)
                type_converted_replacement_map.update({current_value: new_value})


        replace_value_in_column_res = self.model.replaceValueInColumn(df, col_header, type_converted_replacement_map)
        if is_successful(replace_value_in_column_res):
            # self.getSelectedDataframeAndLoadOnView(identifier) #reload view so user can see updated table
            self.view.redrawTables()
            print(replace_value_in_column_res.unwrap())
        else:
            print(replace_value_in_column_res.failure())

    #we enforce user input checks so there's little need to double check the values. Though if you ever do need to, you could use a recursive solution to ensure all strings are non-empty
    def mergeDataframes(self, merge_parameters: dict) -> DataFrame | None:

        res_left = self.model.getSelectedDataframe(merge_parameters["left"])
        res_right = self.model.getSelectedDataframe(merge_parameters["right"])
        if not res_left:
            print(f"Unable to find dataframe entry with name: {merge_parameters["left"]}. Terminating merge operation")
            return None
        elif not res_right:
            print(f"Unable to find dataframe entry with name: {merge_parameters["right"]}. Terminating merge operation")
            return None

        _, left_df = res_left
        _, right_df = res_right

        merge_parameters.update(left = left_df, right = right_df, )
        merged_df = self.model.mergeDataframes(merge_parameters)
        return merged_df

    def concatDataframes(self, names_of_df_to_concat: list[str], concat_parameters: dict) -> pd.DataFrame | None:
        dfs_to_concat = []
        for df_name in names_of_df_to_concat:
            res = self.model.getSelectedDataframe(df_name)
            if res is None:
                print(f"Unable to find dataframe with name: {df_name}. Terminating concat operation")
                return None
            _, df = res
            dfs_to_concat.append(df)

        concat_parameters.update(axis = int(concat_parameters["axis"]))
        concat_parameters.update(ignore_index = True if concat_parameters["ignore_index"] == "True" else False)

        if len(dfs_to_concat) < 2:
            print("Less than 2 Dataframes received, cannot concat")
            return None

        print(f"concatting these dfs:{names_of_df_to_concat}")
        print(f"calling concat with these parameters {concat_parameters}")

        return self.model.concatDataframes(dfs_to_concat, concat_parameters)

    #return a windows rendering the new dataframe so user can double check the validity -
    #offer 3 choices: replace existing dataframe, save as new (must provide option to change
    #the name - enforce it cannot be the same name as others), or delete so we don't keep the
    #new data at all
    def withinDataframeAggregation(self, identifier: str, new_column_name, mathematical_expression: str) -> pd.DataFrame | None:
        final_expression = new_column_name + "=" + mathematical_expression
        # _, df = self.model.getSelectedDataframe(identifier)
        res = self.model.getSelectedDataframe(identifier)
        if res is None:
            print(f"Unable to find dataframe with name: {identifier}. Terminating within dataframe aggregation")
            return None
        _, df = res
        aggregated_df = self.model.withinDataframeAggregation(df, final_expression)
        return aggregated_df

    def saveDataframeAsCSV(self, identifier: str, file_path: str):
        if not file_path or not identifier:
            print("file path or df identifier is empty. Terminating save operation.")
            return

        res = self.model.getSelectedDataframe(identifier)
        if res is None:
            print("Unable to find (and thus load) selected dataframe in memory")
            return
        name, df = res

        # validate path up to the actual full path exists
        path_obj = Path(file_path)
        parent_directory = path_obj.parent
        if not parent_directory.exists():
            print("Invalid File Path")

        res = self.model.saveDataframeAsCSV(df, file_path)
        if not is_successful(res):
            print(res.failure())
        else:
            print(res.unwrap())

    def sortByColumn(self, identifier: str, columns_to_sort_by: list[str], lexigraphic_sort_per_column: list[bool], ignore_index: bool) -> pd.DataFrame | None :
        if not columns_to_sort_by or not lexigraphic_sort_per_column or type(ignore_index) is not bool:
            print("Malformed parameters passed into sortByColumn. Terminating operation.")
            return

        if len(columns_to_sort_by) != len(lexigraphic_sort_per_column):
            print("Number of columns to sort and number of specified lexigraphic sort is unequal. Terminating sortByColumn Operation.")
            return

        res = self.model.getSelectedDataframe(identifier)
        if res is None:
            print(f"Unable to find dataframe with name: {identifier}. Terminating within dataframe aggregation")
            return None
        _, df = res

        sort_res = self.model.sortByColumn(df, columns_to_sort_by, lexigraphic_sort_per_column, ignore_index)

        if not is_successful(sort_res):
            print(sort_res.failure())
            return None

        return sort_res.unwrap()

    def renameColumnHeaders(self, identifier: str, rename_mapping: dict[str, str]):

        if len(rename_mapping) == 0:
            print("no (key,val) pair detected. Terminating column renaming operation")
            return None

        for key, val in list(rename_mapping.items()):
            if type(key) is not str or type(val) is not str:
                print("Detected a (key,val) pair to be a non-string. Terminating column renaming operation.")
                return None

            if not key or not val:
                print("Detected a (key,val) pair to be an empty string. Terminating column renaming operation.")
                return None

        res = self.model.getSelectedDataframe(identifier)
        if res is None:
            print(f"Unable to find dataframe with name: {identifier}. Terminating within dataframe aggregation")
            return None
        _, df = res

        res = self.model.renameColumnHeaders(df, rename_mapping)
        if not is_successful(res):
            print(res.failure())
            return None

        print(res.unwrap())
        self.view.redrawTables()
        return None

    #to be implemented
    def reorderColumns(self, identifier: str, anchor_column: str, columns_to_move: list[str]):

        res = self.model.getSelectedDataframe(identifier)
        if res is None:
            print(f"Unable to find dataframe with name: {identifier}. Terminating within dataframe aggregation")
            return None
        _, df = res

        df_headers = df.columns
        if anchor_column not in df_headers:
            print("anchor_column does not exist in dataframe. Terminating reorder column operation.")

        for col in columns_to_move:
            if col not in df_headers:
                print(f"The column {col} does not exist in the dataframe. Terminating reorder column operation")
                return None

        if anchor_column in columns_to_move:
            print("Anchor column cannot be part of the columns you want to move around. Terminating reorder column operation")
            return None


        if anchor_column == "" or len(columns_to_move) == 0:
            print("Anchor column or columns_to_place must be nonempty. Terminating reorder column operation")
            return None

        return self.model.reorderColumns(df, anchor_column, columns_to_move)











































