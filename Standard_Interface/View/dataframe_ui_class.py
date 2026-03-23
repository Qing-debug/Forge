import tkinter as tk
from tkinter import ttk
from Forge.Standard_Interface.Presenter import datapresenter
from Forge.Standard_Interface.Shared_Contracts.shared_contracts import ReplacementValueTypes
from pandastable import Table
import pandas as pd
import sympy as sp
from typing import Any
import sympy.core.numbers as sp_numbers
import typing
if typing.TYPE_CHECKING: # dataview used for type annotation but it leads to circular import runtime error without this. This lets us keep the benefits of type annotation
    from Forge.Standard_Interface.View import dataview
if typing.TYPE_CHECKING: #datapresenter used for type annotation but it leads to circular import runtime error without this. This lets us keep the benefits of type annotation
    from Forge.Presenter import datapresenter


#not too sure how to properly name the class. It's not really a widget since it provides functionality only but it binds it's internal workings to the widget that called it.
class DataFrameWidget(tk.Frame):
    def __init__(self, view: 'dataview.DataView', parent_frame: tk.Frame, identifier: str, presenter: 'datapresenter.DataPresenter', df: pd.DataFrame):
        super().__init__(parent_frame)
        self.view = view
        self.identifier = identifier
        self.presenter = presenter

        # Table frame
        self.table_frame = tk.Frame(self)
        self.table = None

        self.toolbar_frame = tk.Frame(self)
        self.value_replacement_button = tk.Button(self.toolbar_frame, text= "Replace Value", command = self._on_click_replace_value_button)
        self.merge_button = tk.Button(self.toolbar_frame, text="Merge", command = self._on_click_merge_button)
        self.aggregate_button = tk.Button(self.toolbar_frame, text = "Aggregate data", command = self._on_click_aggregate_button)
        self.sort_column_and_reset_index_button = tk.Button(self.toolbar_frame, text="Sort by Column", command=self._on_click_sort_column_and_reset_index_button)
        self.rename_column_header_button = tk.Button(self.toolbar_frame, text="Rename Columns", command=self._on_click_rename_column_header_button)
        self.reorder_columns_button = tk.Button(self.toolbar_frame, text="Reorder Columns", command=self._on_click_reorder_columns_button)

        self.replace_value_dialog = None
        self.merge_value_dialog = None
        self.aggregate_dialog = None
        self.sort_column_and_reset_index_dialog = None
        self.rename_column_header_dialog = None
        self.reorder_columns_dialog = None

    # sets up the instance inner state
    def setup(self):
        self.toolbar_frame.pack(fill=tk.X, padx=5, pady=5)

        self.value_replacement_button.pack(side=tk.LEFT, padx=2)
        self.merge_button.pack(side=tk.LEFT, padx=2)
        self.aggregate_button.pack(side = tk.LEFT, padx= 2)
        self.sort_column_and_reset_index_button.pack(side=tk.LEFT, padx=2)
        self.rename_column_header_button.pack(side=tk.LEFT, padx=2)
        self.reorder_columns_button.pack(side=tk.LEFT, padx=2)

        self.table_frame.pack(fill=tk.BOTH, expand=True)
        self._load_dataframe()

        #setup ui utility class
        self.replace_value_dialog = ReplaceValueDialog(self)
        self.merge_value_dialog = MergeDFDialog(self, self.view, self.presenter)
        self.aggregate_dialog = AggregateDialog(self)
        self.sort_column_and_reset_index_dialog = SortByColumnDialog(self)
        self.rename_column_header_dialog = RenameColumnHeaderDialog(self)
        self.reorder_columns_dialog = ReorderColumnsDialog(self)

    def _load_dataframe(self):
        if self.table is None:
            self.table = Table(self.table_frame, dataframe=self.df, width=600, height=600, showstatusbar=True)
            self.table.show()

    def _on_click_replace_value_button(self):
        if not self.replace_value_dialog:
            print("no reference to the replace_value_dialog object. Terminating operation.")
            return
        self.replace_value_dialog.open_replace_value_dialog()

    def _on_click_merge_button(self):
        if not self.merge_value_dialog:
            print("no reference to the merge_dialog object. Terminating operation.")
            return
        self.merge_value_dialog.openMergeDFDialog()

    def _on_click_aggregate_button(self):
        if not self.aggregate_dialog:
            print("no reference to the aggregate_dialog object. Terminating operation.")
            return
        self.aggregate_dialog.openAggregateDialog()

    def _on_click_sort_column_and_reset_index_button(self):
        if not self.sort_column_and_reset_index_dialog:
            print("no reference to the sort_reset_dialog object. Terminating operation.")
            return
        self.sort_column_and_reset_index_dialog.openSortAndResetIndexDialog()

    def _on_click_rename_column_header_button(self):
        if not self.rename_column_header_dialog:
            print("no reference to the rename_column_header_dialog object. Terminating operation.")
            return
        self.rename_column_header_dialog.openRenameColumnHeaderDialog()

    def _on_click_reorder_columns_button(self):
        if not self.reorder_columns_dialog:
            print("no reference to the reorder_columns_dialog object. Terminating operation.")
            return
        self.reorder_columns_dialog.openReorderColumnsDialog()

    def updateTable(self):
        if self.table is not None:
            self.table.destroy()

        # Recreate table with fresh DataFrame
        self.table = Table(self.table_frame, dataframe=self.df, width=600, height=600, showstatusbar=True)
        self.table.show()
        self.table.autoResizeColumns()



    @property
    def df(self):
        res = self.presenter.getDataFrame(self.identifier)
        if res is None:
            raise DataFrameNotFoundError(f"pandas dataframe associated to '{self.identifier}' was not found in memory")
        _, df = res
        return df


class ReplaceValueDialog:
    def __init__(self, associated_dataframe_widget: DataFrameWidget):
        self.associated_dataframe_widget = associated_dataframe_widget

        #needs to be setup and cleaned up everytime after _open_replace_value_dialog method is called.
        self.identifier = None
        self.df = None
        self.presenter = None
        self.rendered_widgets = [] #keep track of rendered widgets to facilitate ability to swap modes
        self.use_non_default_behaviour = None
        self.main_form_container = None
        self.replace_value_dialog = None

    def _on_dialog_close_cleanup(self):

        self.replace_value_dialog.destroy() #close window

        #reset state
        self.identifier = None
        self.df = None
        self.presenter = None
        self.rendered_widgets = []
        self.use_non_default_behaviour = None
        self.main_form_container = None
        self.replace_value_dialog = None

    def open_replace_value_dialog(self):
        #setup instance state
        self.identifier, self.df = self.associated_dataframe_widget.presenter.getDataFrame(self.associated_dataframe_widget.identifier)
        self.presenter = self.associated_dataframe_widget.presenter
        self.use_non_default_behaviour = tk.BooleanVar(value=False)

        #create window
        self.replace_value_dialog = tk.Toplevel()
        self.replace_value_dialog.title("Replace Value")

        #setup cleaning up logic when window closes
        self.replace_value_dialog.protocol("WM_DELETE_WINDOW", self._on_dialog_close_cleanup)

        #create frame containing unchanging UI elements
        header_container = tk.Frame(self.replace_value_dialog, bg="red")
        header_container.pack()

        #add UI checkbutton used to select between two potential modes (each one has their own way of renderin things)
        checkbox_frame = tk.Frame(header_container)
        checkbox_frame.pack(pady=5, fill=tk.X)

        tk.Checkbutton(
            checkbox_frame,
            text="Replace All Values In A Given Column",
            variable=self.use_non_default_behaviour,
            command=lambda: self._on_toggle_non_default_behaviour()
        ).pack(anchor=tk.CENTER)

        help_label = tk.Label(
            checkbox_frame,
            text="(Unchecked: replace all occurrences of a specific value in chosen column but will be automatically converted to the type of values in that column | Checked: replace all unique values in a column with values that are of the chosen type)",
            fg="gray",
            font=("Arial", 9),
            wraplength=500,
            justify=tk.CENTER
        )
        help_label.pack(anchor=tk.CENTER)

        self.main_form_container = tk.Frame(self.replace_value_dialog) #potentially make main_form_container an attribute but need to see how we use it first
        self.main_form_container.pack()

        self._default_render()

    def _default_render(self):
        single_value_form = tk.Frame(self.main_form_container)
        single_value_form.pack()

        tk.Label(single_value_form, text="Select Column:").grid(row=0, column=0, padx=5, pady=5)
        column_headers_dropdown = ttk.Combobox(single_value_form, state='readonly')
        column_headers = self.df.columns.tolist()
        column_headers_dropdown['values'] = column_headers
        column_headers_dropdown.grid(row=0, column=1, padx=5, pady=5)

        current_entry_label = tk.Label(single_value_form, text="current Value:")
        current_entry_label.grid(row=1, column=0, padx=5, pady=5)
        current_entry = tk.Entry(single_value_form)
        current_entry.grid(row=1, column=1, padx=5, pady=5)

        new_entry_label = tk.Label(single_value_form, text="New Value:")
        new_entry_label.grid(row=2, column=0, padx=5, pady=5)
        new_entry = tk.Entry(single_value_form)
        new_entry.grid(row=2, column=1, padx=5, pady=5)

        self.rendered_widgets.append(single_value_form)

        apply_changes_button = tk.Button(single_value_form, text="Apply",
                                         command=lambda: self.replace_values_in_column(column_headers_dropdown.get(),
                                                                                 [(current_entry, new_entry)]))
        apply_changes_button.grid(row=3, column=0, columnspan=2, pady=10)
        self.rendered_widgets.append(apply_changes_button)


    def replace_values_in_column(self, selected_column_name: 'str', entry_pairs: list[tuple[tk.Entry, tk.Entry]], selected_replacement_type:'str' = None):
        replacement_map = {}
        for curr_entry, new_entry in entry_pairs:
            curr_val, new_val = curr_entry.get(), new_entry.get()
            replacement_map.update({curr_val: new_val})
        self.associated_dataframe_widget.presenter.replaceValueInColumn(self.associated_dataframe_widget.identifier,
                                                                        selected_column_name, replacement_map, selected_replacement_type)

    def _on_toggle_non_default_behaviour(self):
        if self.rendered_widgets: # abusing python scoping to get access to rendered_widgets
            for widget in self.rendered_widgets:
                widget.destroy()

        self._non_default_render() if self.use_non_default_behaviour.get() else self._default_render()

    def _non_default_render(self):
        # options_container houses the dropdowns for selecting the column we are going to modify the values in and the dropbox that selects what values we will change it into
        options_container = tk.Frame(self.main_form_container, bg="blue")
        options_container.pack()

        self.rendered_widgets.append(options_container)

        # render column header selection dropdown
        tk.Label(options_container, text="Select Column:").grid(row=0, column=0, padx=5, pady=5)
        column_headers = self.df.columns.tolist()
        column_headers_dropdown = ttk.Combobox(options_container, state='readonly')
        column_headers_dropdown['values'] = column_headers
        column_headers_dropdown.grid(row=0, column=1, padx=5, pady=5)

        # render dropdown that allows us to select the new type of replacement values
        tk.Label(options_container, text="Replacement Type:").grid(row=1, column=0, padx=5, pady=5)
        selected_replacement_value_type = tk.StringVar()
        replacement_value_type_dropdown = ttk.Combobox(options_container, state='readonly',
                                                       textvariable=selected_replacement_value_type)
        replacement_value_type_dropdown['values'] = [replacement_type.value for replacement_type in
                                                     ReplacementValueTypes]
        replacement_value_type_dropdown.grid(row=1, column=1, padx=5, pady=5)

        column_headers_dropdown.bind('<<ComboboxSelected>>', lambda event: self.on_column_headers_dropdown_select_value(event, replacement_value_type_dropdown))

        self.rendered_widgets.append(column_headers_dropdown)

    def on_column_headers_dropdown_select_value(self, event, replacement_value_type_dropdown: ttk.Combobox):
        selected_column_header_name = event.widget.get()
        self._render_based_on_selected_column_header(selected_column_header_name, replacement_value_type_dropdown)

    def _render_based_on_selected_column_header(self, selected_column_name: str, replacement_value_type_dropdown: ttk.Combobox):

        #clear previously rendered dynamic_pairs_parent_container (if it exists) in main_form_container before populating it again
        for child in self.main_form_container.winfo_children():
            if child._name == "dynamic_pairs_parent_container":
                child.destroy()

        dynamic_pairs_parent_container = tk.Frame(self.main_form_container, name="dynamic_pairs_parent_container")
        dynamic_pairs_parent_container.pack()
        self.rendered_widgets.append(dynamic_pairs_parent_container)

        # renders scrollable region
        canvas = tk.Canvas(dynamic_pairs_parent_container)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(dynamic_pairs_parent_container, orient='vertical', command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        dynamic_pairs_form = tk.Frame(canvas)
        canvas.create_window((0, 0), window=dynamic_pairs_form, anchor='nw')

        row, col = 0, 0

        dynamically_generated_curr_and_new_entries = []

        for uniq_val in self.df[selected_column_name].unique().tolist():
            current_entry_label = tk.Label(dynamic_pairs_form, text="current Value:")
            current_entry_label.grid(row=row, column=col, padx=5, pady=5)
            current_entry = tk.Entry(dynamic_pairs_form)
            current_entry.insert(0, str(uniq_val))
            current_entry.grid(row=row, column=col + 1, padx=5, pady=5)

            new_entry_label = tk.Label(dynamic_pairs_form, text="New Value:")
            new_entry_label.grid(row=row + 1, column=col, padx=5, pady=5)
            new_entry = tk.Entry(dynamic_pairs_form)
            new_entry.grid(row=row + 1, column=col + 1, padx=5, pady=5)

            dynamically_generated_curr_and_new_entries.append((current_entry, new_entry))

            row += 2

        apply_changes_button = tk.Button(dynamic_pairs_form, text="Apply", command= lambda: self._validate_and_apply(selected_column_name, replacement_value_type_dropdown, dynamically_generated_curr_and_new_entries, error_label, dynamic_pairs_form, canvas))
        apply_changes_button.grid(row=row, column=col, columnspan=2, pady=10)

        error_label = tk.Label(dynamic_pairs_form, text="", fg="red")
        error_label.grid(row=row + 1, column=col, columnspan=2, pady=5)
        error_label.grid_remove()

        dynamic_pairs_form.update_idletasks()  # forces tk to compute actual size of dynamic_pairs_containers based off its components
        canvas.configure(scrollregion=canvas.bbox("all"))  # makes it so we can only scroll such that we can only view the rendered contents inside dynamic_pairs_containers

    def _validate_and_apply(self, selected_column_name: str, replacement_value_type_dropdown: ttk.Combobox, entry_pairs: list[tuple[tk.Entry, tk.Entry]], error_label, dynamic_pairs_form: tk.Frame, canvas: tk.Canvas):
        # Reset any previous error styling
        replacement_value_type_dropdown.configure(style='TCombobox')
        selected_replacement_type = replacement_value_type_dropdown.get()

        # Check if replacement type is selected
        if not selected_replacement_type:
            # Highlight the dropdown in red
            style = ttk.Style()
            style.configure('Error.TCombobox', fieldbackground='#ffcccc', background='#ffcccc')
            replacement_value_type_dropdown.configure(style='Error.TCombobox')

            error_label.config(text="⚠ Please select a replacement type")
            error_label.grid()  # ensures it's visible on the same line


            dynamic_pairs_form.update_idletasks()  # forces tk to compute actual size of dynamic_pairs_containers if the case where we reveal the error_label
            canvas.configure(scrollregion=canvas.bbox(
                "all"))  # makes it so we can only scroll such that we can only view the rendered contents inside dynamic_pairs_containers

            return

        self.replace_values_in_column(selected_column_name, entry_pairs, selected_replacement_type)

class MergeDFDialog:
    def __init__(self, associated_dataframe_widget: DataFrameWidget, view: 'dataview.DataView', presenter: 'datapresenter.DataPresenter'):
        self.associated_dataframe_widget = associated_dataframe_widget
        self.view = view
        self.presenter = presenter

        self.left_df_name = None
        self.right_df_name = None

        self.main_form_container = None
        self.canvas_for_rendering_conditions_container_content = None
        self.conditions_container = None
        self.merge_df_dialog = None

        #needs to be reset when windows closes to clear all previously chosen conditions
        self.merge_conditions = []

    @staticmethod
    def _build_merge_kwargs(df_names: tuple[str, str], suffixes: tuple[str, str], merge_method: str,
                            columns_to_merge_on: list[tuple[str, str]]) -> dict[str, str | tuple[str,str] | list[str]]:

        merge_parameters = {"left": df_names[0], "right": df_names[1], "how": merge_method, "suffixes": suffixes}

        can_use_on_merge_parameter = True

        for condition in columns_to_merge_on:
            if condition[0] != condition[1]:
                can_use_on_merge_parameter = False
                break

        if can_use_on_merge_parameter:
            on_keys = [keys[0] for keys in columns_to_merge_on]
            merge_parameters.update({"on": on_keys})
            print(f"on_keys{on_keys}")
        else:
            left_on_keys = [keys[0] for keys in columns_to_merge_on]
            right_on_keys = [keys[1] for keys in columns_to_merge_on]
            print(f"left_on: {left_on_keys}\nright_on: {right_on_keys}")

            merge_parameters.update({"left_on": left_on_keys, "right_on": right_on_keys})

        return merge_parameters

    def _onDialogCloseCleanup(self):
        self.merge_df_dialog.destroy()
        self.merge_conditions.clear()


    def openMergeDFDialog(self):
        self.left_df_name = self.associated_dataframe_widget.identifier

        self.merge_df_dialog = tk.Toplevel()
        self.merge_df_dialog.title("merge df")
        self.merge_df_dialog.geometry("700x500")

        #setup cleaning up logic when window closes
        self.merge_df_dialog.protocol("WM_DELETE_WINDOW", self._onDialogCloseCleanup) #lambda functions only allow one-line expressions (not statements)

        self.main_form_container = tk.Frame(self.merge_df_dialog)
        self.main_form_container.pack()

        tk.Label(self.main_form_container, text="select right table to merge with").pack()

        df_name_container = tk.Listbox(self.main_form_container)
        for item in self.view.getDFNameContainer().get(0, tk.END):
            df_name_container.insert(tk.END, item)
        df_name_container.pack()
        df_name_container.bind('<<ListboxSelect>>', lambda event: self._onClickDFName(event, df_name_container))

    def _onClickDFName(self, event: tk.Event, df_name_container: tk.Listbox):
        selection = df_name_container.curselection()
        if not selection:
            return

        selected_index = selection[0]
        df_name = event.widget.get(selected_index)
        self.right_df_name = df_name
        #completely delete everything in main_form_container so we can rerender things in it
        for child in self.main_form_container.winfo_children():
            child.destroy()

        self._renderMergeOptions()

    def _renderMergeOptions(self):
        def validationAndApply(name_of_new_df: str, target_df_names: tuple[str, str], suffixes: tuple[str, str], merge_method: str, columns_to_merge_on: list[tuple[str, str]]):
            missing_items = []
            # --- 1. Check Name ---
            if not name_of_new_df:
                missing_items.append("DataFrame Name")

            # --- 2. Check Merge Method ---
            if not merge_method:
                missing_items.append("Merge Method")

            # --- 2. check suffixes aren't empty  ---

            if not suffixes[0] or not suffixes[1]:
                missing_items.append("Enter suffixes")

            # --- 3. Check Conditions ---

            if not columns_to_merge_on:
                missing_items.append("Merge Conditions")

            # --- 4. Update Error Label ---
            if missing_items:
                error_text = "⚠ Missing: " + ", ".join(missing_items)
                error_label.config(text=error_text)
                error_label.pack(pady=5)  # Ensure it is visible
                return

            # --- Success ---

            error_label.pack_forget()
            merge_parameters = self._build_merge_kwargs(target_df_names, suffixes, merge_method, columns_to_merge_on)

            merged_df = self.presenter.mergeDataframes(merge_parameters)

            self._open_merged_df_preview_window(merged_df, merged_df_name_entry.get())
            # self._onDialogCloseCleanup() might not want ot do this yet since we need to render a new windows to show the merged dataframe for the user to decide if they want to keep or discard it


        name_frame = tk.Frame(self.main_form_container)
        name_frame.pack(pady=5)
        tk.Label(name_frame, text="Name of merged df:").pack(side=tk.LEFT, padx=5)
        merged_df_name_entry = tk.Entry(name_frame)
        merged_df_name_entry.pack(side=tk.LEFT, padx=5)

        suffix_frame = tk.Frame(self.main_form_container)
        suffix_frame.pack(pady=5)
        tk.Label(suffix_frame, text = "Enter desired suffixes").grid(row=0, column=0)
        left_df_suffix = tk.Entry(suffix_frame)
        left_df_suffix.insert(0, "_left")
        left_df_suffix.grid(row=0, column=1, padx=3)
        right_df_suffix = tk.Entry(suffix_frame)
        right_df_suffix.insert(0, "_right")
        right_df_suffix.grid(row=0, column=2, padx=3)

        merge_method_frame = tk.Frame(self.main_form_container)
        merge_method_frame.pack(pady=5)
        tk.Label(merge_method_frame, text="Choose desired merge method").grid(row=0, column=0)
        merge_methods_options = ttk.Combobox(merge_method_frame, values = ["inner", "outer", "left", "right"], state = "readonly")
        merge_methods_options.grid(row=0, column=1)


        merge_on_frame = tk.Frame(self.main_form_container)
        merge_on_frame.pack(pady=5)
        tk.Label(merge_on_frame, text="Select columns to merge on:").grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        tk.Label(merge_on_frame, text=f"Left: {self.left_df_name}").grid(row=1, column=0, padx=5)
        tk.Label(merge_on_frame, text=f"Right: {self.right_df_name}").grid(row=1, column=1, padx=5)

        header_columns_in_left_df = self.presenter.getDataFrame(self.left_df_name)[1].columns.tolist()
        header_columns_in_right_df = self.presenter.getDataFrame(self.right_df_name)[1].columns.tolist()

        left_merge_column_combobox = ttk.Combobox(merge_on_frame, state="readonly", values=header_columns_in_left_df)
        left_merge_column_combobox.grid(row=2, column=0, padx=5, pady=5)
        right_merge_column_combobox = ttk.Combobox(merge_on_frame, state="readonly", values=header_columns_in_right_df)
        right_merge_column_combobox.grid(row=2, column=1, padx=5, pady=5)
        add_condition_button = tk.Button(merge_on_frame, text="Add conditions", command = lambda: self._addMergeCondition(left_merge_column_combobox, right_merge_column_combobox))
        add_condition_button.grid(row=2, column=2, padx=5, pady=5)

        rendered_conditions_region = tk.Frame(merge_on_frame)
        rendered_conditions_region.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky='ew')
        self.canvas_for_rendering_conditions_container_content = tk.Canvas(rendered_conditions_region, height=150)
        self.canvas_for_rendering_conditions_container_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(rendered_conditions_region, orient='vertical', command=self.canvas_for_rendering_conditions_container_content.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_for_rendering_conditions_container_content.configure(yscrollcommand=scrollbar.set)
        self.conditions_container = tk.Frame(self.canvas_for_rendering_conditions_container_content, bg = "red")
        self.conditions_container.pack(pady=5, fill=tk.X)
        self.canvas_for_rendering_conditions_container_content.create_window((0, 0), window=self.conditions_container, anchor='nw')
        # Bind canvas width to update the embedded frame width
        self.canvas_for_rendering_conditions_container_content.bind('<Configure>', lambda event: self._onCanvasConfigure(event))
        self._renderConditionsList()
        self.conditions_container.update_idletasks()

        apply_button = tk.Button(self.main_form_container, text="Apply Merge", command = lambda: validationAndApply(merged_df_name_entry.get(),
                                                                                                                    (self.left_df_name, self.right_df_name),
                                                                                                                      (left_df_suffix.get(), right_df_suffix.get()),
                                                                                                                      merge_methods_options.get(),
                                                                                                                      self.merge_conditions))
        apply_button.pack()
        error_label = tk.Label(self.main_form_container, text="", fg="red", font=("Arial", 9, "bold"))

    def _onCanvasConfigure(self, event):
        self.canvas_for_rendering_conditions_container_content.itemconfig(
            self.canvas_for_rendering_conditions_container_content.find_withtag("all")[0], width=event.width)

    def _addMergeCondition(self, left_combobox: ttk.Combobox, right_combobox: ttk.Combobox):
        left_val = left_combobox.get()
        right_val = right_combobox.get()
        if left_val and right_val:
            self.merge_conditions.append((left_val, right_val))
            self._renderConditionsList()
        print(self.merge_conditions)

    def _removeMergeCondition(self, index: int):
        if 0 <= index < len(self.merge_conditions):
            self.merge_conditions.pop(index)
            self._renderConditionsList()

    def _renderConditionsList(self):
        for widget in self.conditions_container.winfo_children():
            widget.destroy()

        tk.Label(self.conditions_container, text="Merge Conditions:").pack()

        for i, (left_col, right_col) in enumerate(self.merge_conditions):
            frame = tk.Frame(self.conditions_container)
            frame.pack(fill=tk.X)
            tk.Label(frame, text=f"{left_col} = {right_col}").pack(side=tk.LEFT, padx=5)
            tk.Button(frame, text="Delete", command=lambda idx=i: self._removeMergeCondition(idx)).pack(side=tk.RIGHT, padx=5) #this is pretty neat, button is created with an anonymous callback function with the parameter idx default initialised some index in the merge list.

        self.conditions_container.update_idletasks()

        # Update canvas width to fit content
        required_width = self.conditions_container.winfo_reqwidth() #get largest width
        self.canvas_for_rendering_conditions_container_content.configure(width=required_width)
        self.canvas_for_rendering_conditions_container_content.configure(scrollregion=self.canvas_for_rendering_conditions_container_content.bbox("all"))

    def _open_merged_df_preview_window(self, merged_df: pd.DataFrame, new_df_name: str):
        def on_keep():
            # e.g., self.presenter.load_dataframe_object(merged_df, new_df_name)
            print(f"Keeping dataframe: {new_df_name}")


            self.presenter.loadDataframeEntryFromPandasDFAndUpdateView(merged_df, new_df_name)

            preview_window.destroy()
            self._onDialogCloseCleanup()  # Close the main merge tool on success

        def on_discard():
            print("Discarding merge result")
            preview_window.destroy()
            # We do NOT close the main merge tool, so user can try different settings


        # 1. Create the window as a child of the merge dialog
        preview_window = tk.Toplevel(self.merge_df_dialog)
        preview_window.title(f"Preview Merge Result: {new_df_name}")
        preview_window.geometry("700x500")

        # 2. Make it modal (User must interact with this window before clicking anything else)
        preview_window.grab_set()

        # 3. Label
        tk.Label(preview_window, text="Review the merged data. Click 'Keep' to save to memory.",
                 font=("Arial", 10, "bold"), pady=10).pack()

        # 4. Show DataFrame using PandaStable
        table_frame = tk.Frame(preview_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        pt = Table(table_frame, dataframe=merged_df, showstatusbar=True)
        pt.show()

        # 5. Buttons Container
        btn_frame = tk.Frame(preview_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Keep / Save", command=on_keep, bg="#ddffdd", width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Discard", command=on_discard, bg="#ffdddd", width=15).pack(side=tk.LEFT, padx=10)

class AggregateDialog:
    def __init__(self, associated_dataframe_widget):
        self.associated_dataframe_widget = associated_dataframe_widget

        #will be setup later
        self.identifier = None
        self.df = None
        self.presenter = None

        self.aggregate_dialog = None


    def _on_dialog_close_cleanup(self):

        # self.replace_value_dialog.destroy() #close window

        self.identifier = None
        self.df = None
        self.presenter = None




    def _setup(self):
        self.identifier, self.df = self.associated_dataframe_widget.presenter.getDataFrame(self.associated_dataframe_widget.identifier)
        self.presenter = self.associated_dataframe_widget.presenter

    def openAggregateDialog(self):
        self._setup() #called just in case the identifier changes or df changes within the associated_dataframe_widget - don't see why it would at thus point in time.

        self.aggregate_dialog = tk.Toplevel()
        self.aggregate_dialog.title("Aggregate Data")
        self.aggregate_dialog.geometry("600x400")

        column_headers = self.df.columns.tolist()

        # --- LEFT SIDE: Column List ---
        list_frame = ttk.LabelFrame(self.aggregate_dialog, text="Available Columns")
        list_frame.pack(side="left", fill="y", padx=10, pady=10)
        col_listbox = tk.Listbox(list_frame, height=15)

        for col in column_headers:
            col_listbox.insert(tk.END, col)
        col_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # --- RIGHT SIDE: Formula Bar ---
        right_frame = ttk.Frame(self.aggregate_dialog)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Name of new column:").pack(anchor="w")

        aggregated_column_name = tk.Entry(right_frame)
        aggregated_column_name.pack(fill="x", pady=5)

        ttk.Label(right_frame, text="Type your formula here:").pack(anchor="w")

        # The Text Widget (The Formula Bar)
        formula_text = tk.Text(right_frame, height=5, font=("Arial", 12))
        formula_text.pack(fill="x", pady=5)


        # DEFINE THE "TOKEN" STYLE (The Visual Trick)
        # This makes the text look like a bubble (Light Blue background)
        formula_text.tag_config("token", background="#d1e7dd", foreground="#0f5132")

        # Initially empty, red text for visibility
        error_label = ttk.Label(right_frame, text="", foreground="red", wraplength=280)
        error_label.pack(pady=5)

        # Calculate Button
        calc_btn = ttk.Button(right_frame, text="Create Column Based Off formula", command = lambda: self._calculate(column_headers, formula_text, result_label, aggregated_column_name.get(), error_label))
        calc_btn.pack(pady=10)

        result_label = ttk.Label(
            right_frame,
            text="Result: ",
            font=("Arial", 10, "bold"),
            justify="left"  # Aligns text to the left when it wraps
        )

        result_label.pack(anchor="w", fill="x")

        help_text = "Tip: Double-click a column on the left to insert it.\nYou can also type numbers and math symbols (+ - * /)."
        ttk.Label(right_frame, text=help_text, foreground="grey").pack(anchor="w", pady=20)

        #bindings
        col_listbox.bind("<Double-Button-1>", lambda event: self._insertToken(col_listbox, formula_text))
        formula_text.bind("<BackSpace>", lambda event: self._on_backspace(formula_text))
        right_frame.bind("<Configure>", lambda event: self._adjust_wraplength(event, result_label))

    def _on_backspace(self, formula_text: tk.Text):
        tags_before = formula_text.tag_names("insert-1c")
        if "token" in tags_before:
            token_range = formula_text.tag_prevrange("token", "insert")
            start, end = token_range
            formula_text.delete(start, end)
            return "break" #must return this to prevent default behaviour from occuring after we get rid of the sequence of characters that hav the "token" tag attached to them.
        return None

    def _adjust_wraplength(self, event, result_label: ttk.Label):
        result_label.config(wraplength=event.width - 20)

    def _insertToken(self, col_listbox: tk.Listbox, formula_text: tk.Text):
        # 1. Get selected column
        selection = col_listbox.curselection()
        if not selection:
            return
        col_name = col_listbox.get(selection[0])

        token_text = f" {col_name} "

        formula_text.insert(tk.INSERT, token_text)

        end_index = formula_text.index("insert")
        start_index = f"{end_index}-{len(token_text)}c"
        formula_text.tag_add("token", start_index, end_index)

        formula_text.focus()

    #TODO: add validation to ensure the string is a valid mathematical expression
    def _calculate(self, col_headers: list[str], formula_text: tk.Text, result_label: ttk.Label, aggregate_df_name: str, error_label: ttk.Label):

        error_list = []

        mathematical_formula_for_aggregated_column = formula_text.get("1.0", tk.END).strip()
        aggregated_column_name = aggregate_df_name.strip()

        if not aggregated_column_name:
            error_list.append("Name For New Column")

        if not mathematical_formula_for_aggregated_column:
            error_list.append("Formula Field")

        if error_list:
            error_text = "⚠ Missing: " + ", ".join(error_list)
            error_label.config(text = f"{error_text}")
            return
        else:
            error_label.config(text="")

        symbols = {}
        for col_header in col_headers:
            symbols.update({str(col_header): sp.symbols(col_header)})
        isValidMathematicalFormula = self._isValidMathematicalFormula(mathematical_formula_for_aggregated_column, symbols)
        if not isValidMathematicalFormula:
            error_label.config(text="Error: Failed To Evaluate Mathematical Formula")
            return

        aggregated_df = self.presenter.withinDataframeAggregation(self.identifier, aggregated_column_name, mathematical_formula_for_aggregated_column)
        self._open_aggregated_df_preview_window(aggregated_df)

    def _open_aggregated_df_preview_window(self, aggregated_df: pd.DataFrame):
        # --- Action Callbacks ---
        def on_overwrite():
            print(f"Overwriting data for: {self.identifier}")
            self.presenter.overwriteDFInExistingDataframeEntry(aggregated_df, self.identifier)
            preview_window.destroy()
            self.aggregate_dialog.destroy()

        def on_save_as_new():
            new_name = new_df_name_entry.get().strip()
            if not new_name:
                # Simple visual feedback for empty name
                new_df_name_entry.config(bg="#ffcccc")
                return

            print(f"Saving new dataframe as: {new_name}")
            self.presenter.loadDataframeEntryFromPandasDFAndUpdateView(aggregated_df, new_name)
            preview_window.destroy()
            self.aggregate_dialog.destroy()  # Close the tool on success

        def on_discard():
            print("Discarding changes")
            preview_window.destroy()

        preview_window = tk.Toplevel(self.aggregate_dialog)
        preview_window.title(f"Preview Aggregation Result")
        preview_window.geometry("800x600")

        # Make it modal (blocks interaction with other windows until closed)
        preview_window.transient(self.aggregate_dialog)
        preview_window.grab_set()

        # --- Header ---
        tk.Label(preview_window,
                 text="Review the aggregated data below.",
                 font=("Arial", 11, "bold"), pady=10).pack()

        # --- Table Preview ---
        table_frame = tk.Frame(preview_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        pt = Table(table_frame, dataframe=aggregated_df, showstatusbar=True)
        pt.show()

        # --- Controls Area ---
        controls_frame = tk.Frame(preview_window, bg="#f0f0f0", bd=1, relief=tk.SUNKEN)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        # "Save as New" Name Entry
        tk.Label(controls_frame, text="New DF Name (if saving as new):", bg="#f0f0f0").pack(side=tk.LEFT, padx=5,
                                                                                            pady=10)
        new_df_name_entry = tk.Entry(controls_frame, width=80)
        new_df_name_entry.insert(0, f"{self.identifier}_agg")
        new_df_name_entry.pack(side=tk.LEFT, padx=5, pady=10)


        # --- Buttons ---
        btn_container = tk.Frame(preview_window)
        btn_container.pack(pady=10, fill=tk.X)

        # Centering frame for buttons
        center_frame = tk.Frame(btn_container)
        center_frame.pack(anchor=tk.CENTER)

        # Button 1: Overwrite
        tk.Button(center_frame, text="Overwrite Existing DF",
                  command=on_overwrite,
                  bg="#ffcc80", width=20).pack(side=tk.LEFT, padx=10)

        # Button 2: Save as New
        tk.Button(center_frame, text="Save As New DF",
                  command=on_save_as_new,
                  bg="#90ee90", width=20).pack(side=tk.LEFT, padx=10)

        # Button 3: Discard / Delete
        tk.Button(center_frame, text="Discard / Delete",
                  command=on_discard,
                  bg="#ffab91", width=20).pack(side=tk.LEFT, padx=10)


    @staticmethod
    def _isValidMathematicalFormula(expression: str, symbols: dict[str, Any]):
        try:
            global_dict = {'Integer': sp_numbers.Integer, 'Float': sp_numbers.Float}
            sp.parse_expr(expression, local_dict=symbols, global_dict = global_dict)
            print("Successfully parsed string mathematical expression")
            return True
        except (SyntaxError, ValueError, TypeError, NameError) as e:
            # if e is along the lines of "name 'Integer' is not defined", check whether that key exist in our global dict.
            # If not, run exec('from sympy import *', global_dict), look at the entry in that global_dict with the same key,
            # and add it to our global_dict. sp.parse_expr does some conversions behind the scenes that modifies our expr before
            # it runs eval_expr, hence if those strings are not in our global_dict (local_dict is only for mapping column header
            # to their series counterpart), then the evaluation fails.
            print(f"Exception raised during parsing of mathematical expression: {e}")
            return False

class SortByColumnDialog:
    def __init__(self, associated_dataframe_widget: DataFrameWidget):
        self.associated_dataframe_widget = associated_dataframe_widget

        # Will be setup later
        self.identifier = None
        self.df = None
        self.presenter = None

        self.sort_reset_dialog = None
        self.sort_columns_widgets = []  # Track dynamically added column selection rows

    def _on_dialog_close_cleanup(self):
        if self.sort_reset_dialog:
            self.sort_reset_dialog.destroy()

        # Reset state
        self.identifier = None
        self.df = None
        self.presenter = None
        self.sort_reset_dialog = None
        self.sort_columns_widgets = []

    def _setup(self):
        self.identifier, self.df = self.associated_dataframe_widget.presenter.getDataFrame(self.associated_dataframe_widget.identifier)
        self.presenter = self.associated_dataframe_widget.presenter

    def _open_sorted_by_column_preview_window(self, sorted_df: pd.DataFrame):
        # --- Action Callbacks ---
        def on_overwrite():
            print(f"Overwriting data for: {self.identifier}")
            self.presenter.overwriteDFInExistingDataframeEntry(sorted_df, self.identifier)
            preview_window.destroy()
            self._on_dialog_close_cleanup()

        def on_save_as_new():
            new_name = new_df_name_entry.get().strip()
            if not new_name:
                # Simple visual feedback for empty name
                new_df_name_entry.config(bg="#ffcccc")
                return

            print(f"Saving new dataframe as: {new_name}")
            self.presenter.loadDataframeEntryFromPandasDFAndUpdateView(sorted_df, new_name)
            preview_window.destroy()
            self._on_dialog_close_cleanup()

        def on_discard():
            print("Discarding changes")
            preview_window.destroy()

        preview_window = tk.Toplevel(self.sort_reset_dialog)
        preview_window.title(f"Preview Sort Result")
        preview_window.geometry("800x600")

        # Make it modal (blocks interaction with other windows until closed)
        preview_window.transient(self.sort_reset_dialog)
        preview_window.grab_set()

        # --- Header ---
        tk.Label(preview_window,
                 text="Review the sorted data below.",
                 font=("Arial", 11, "bold"), pady=10).pack()

        # --- Table Preview ---
        table_frame = tk.Frame(preview_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        pt = Table(table_frame, dataframe=sorted_df, showstatusbar=True)
        pt.show()

        # --- Controls Area ---
        controls_frame = tk.Frame(preview_window, bg="#f0f0f0", bd=1, relief=tk.SUNKEN)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        # "Save as New" Name Entry
        tk.Label(controls_frame, text="New DF Name (if saving as new):", bg="#f0f0f0").pack(side=tk.LEFT, padx=5,
                                                                                            pady=10)
        new_df_name_entry = tk.Entry(controls_frame, width=80)
        new_df_name_entry.insert(0, f"{self.identifier}_sorted")
        new_df_name_entry.pack(side=tk.LEFT, padx=5, pady=10)

        # --- Buttons ---
        btn_container = tk.Frame(preview_window)
        btn_container.pack(pady=10, fill=tk.X)

        # Centering frame for buttons
        center_frame = tk.Frame(btn_container)
        center_frame.pack(anchor=tk.CENTER)

        # Button 1: Overwrite
        tk.Button(center_frame, text="Overwrite Existing DF",
                  command=on_overwrite,
                  bg="#ffcc80", width=20).pack(side=tk.LEFT, padx=10)

        # Button 2: Save as New
        tk.Button(center_frame, text="Save As New DF",
                  command=on_save_as_new,
                  bg="#90ee90", width=20).pack(side=tk.LEFT, padx=10)

        # Button 3: Discard / Delete
        tk.Button(center_frame, text="Discard / Delete",
                  command=on_discard,
                  bg="#ffab91", width=20).pack(side=tk.LEFT, padx=10)

    def openSortAndResetIndexDialog(self):
        def _add_sort_column():
            """Add a new column selection row for sorting"""
            column_headers = self.df.columns.tolist()

            row_frame = tk.Frame(sort_columns_container)
            row_frame.pack(fill=tk.X, pady=2)

            # Column number label
            col_num_label = ttk.Label(row_frame, text=f"{len(self.sort_columns_widgets) + 1}.", width=3)
            col_num_label.pack(side=tk.LEFT, padx=(0, 5))

            # Column dropdown
            column_combo = ttk.Combobox(row_frame, state='readonly', width=25, values = column_headers)
            if column_headers:
                column_combo.current(0)
            column_combo.pack(side=tk.LEFT, padx=5)

            # Ascending checkbox
            ascending_var = tk.BooleanVar(value=True)
            ascending_checkbox = ttk.Checkbutton(
                row_frame,
                text="Ascending",
                variable=ascending_var
            )
            ascending_checkbox.pack(side=tk.LEFT, padx=5)

            # Store references
            self.sort_columns_widgets.append({
                'frame': row_frame,
                'column_combo': column_combo,
                'ascending_var': ascending_var
            })
        def _remove_sort_column():
            """Remove the last column selection row"""
            if len(self.sort_columns_widgets) > 1:  # Keep at least one
                widget_dict = self.sort_columns_widgets.pop()
                widget_dict['frame'].destroy()
            else:
                status_label.config(text="Must have at least one column to sort by")
        def _apply_sort_and_reset():
            """Collect parameters and call presenter"""
            # Collect sort parameters
            sort_by_columns = []
            ascending_list = []

            for widget_dict in self.sort_columns_widgets:
                column = widget_dict['column_combo'].get()
                ascending = widget_dict['ascending_var'].get()

                if column:
                    sort_by_columns.append(column)
                    ascending_list.append(ascending)

            if not sort_by_columns:
                status_label.config(text="Please select at least one column to sort by")
                return

            # Collect reset_index parameters
            should_ignore_index = ignore_index.get()

            # Display what would be called
            print("=" * 50)
            print("Sort & Reset Index Operation")
            print("=" * 50)
            print(f"DataFrame: {self.identifier}")
            print(f"sort_values(by={sort_by_columns}, ascending={ascending_list})")
            print(f"reset_index(ignore_index={should_ignore_index})")

            # Call presenter to perform the sort operation
            sorted_df = self.presenter.sortByColumn(self.identifier, sort_by_columns, ascending_list, should_ignore_index)

            if sorted_df is None:
                status_label.config(text="Error: Sort operation failed")
                return

            # Open preview window with the sorted dataframe
            self._open_sorted_by_column_preview_window(sorted_df)

            status_label.config(text="")


        self._setup()

        self.sort_reset_dialog = tk.Toplevel()
        self.sort_reset_dialog.title("Sort & Reset Index")
        self.sort_reset_dialog.geometry("500x450")

        # Setup cleanup logic when window closes
        self.sort_reset_dialog.protocol("WM_DELETE_WINDOW", self._on_dialog_close_cleanup)

        # Main container
        main_container = tk.Frame(self.sort_reset_dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- SORT SECTION ---
        sort_frame = ttk.LabelFrame(main_container, text="Sort Values", padding=10)
        sort_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Instructions
        ttk.Label(sort_frame, text="Select column(s) to sort by:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(0, 5))

        # Scrollable container for sort columns
        canvas_frame = tk.Frame(sort_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, height=150)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        sort_columns_container = tk.Frame(canvas)

        sort_columns_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=sort_columns_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add/Remove column buttons
        button_frame = tk.Frame(sort_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(button_frame, text="+ Add Column", command=_add_sort_column).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="- Remove Last", command=_remove_sort_column).pack(side=tk.LEFT, padx=2)

        # --- RESET INDEX SECTION ---
        reset_frame = ttk.LabelFrame(main_container, text="Reset Index", padding=10)
        reset_frame.pack(fill=tk.X, pady=(0, 10))

        # drop parameter
        ignore_index = tk.BooleanVar(value=True)
        drop_checkbox = ttk.Checkbutton(
            reset_frame,
            text="reset index",
            variable=ignore_index
        )
        drop_checkbox.pack(anchor="w", pady=2)

        # --- ACTION BUTTONS ---
        action_frame = tk.Frame(main_container)
        action_frame.pack(fill=tk.X)

        ttk.Button(
            action_frame,
            text="Apply Sort & Reset Index",
            command=_apply_sort_and_reset
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="Cancel",
            command=self._on_dialog_close_cleanup
        ).pack(side=tk.LEFT, padx=5)

        # Error/Status label
        status_label = ttk.Label(main_container, text="", foreground="red")
        status_label.pack(pady=5)

        # Add first sort column by default
        _add_sort_column()

#main functionality seems to work. but at this point, it should only be collecting the data nd then sending it to the presenter. We need to see where it stores all the data to be sent to the backend. Also, another issue si taht somehow, the changes are going through despite us not having a backend written for it so
# this is implemented in an illegal way.
class RenameColumnHeaderDialog:
    def __init__(self, associated_dataframe_widget: DataFrameWidget):
        self.associated_dataframe_widget = associated_dataframe_widget

        # Will be setup later
        self.identifier = None
        self.df = None
        self.presenter = None

        self.rename_dialog = None
        self.rename_widgets = []  # Track dynamically added rename rows

    def _on_dialog_close_cleanup(self):
        if self.rename_dialog:
            self.rename_dialog.destroy()

        # Reset state
        self.identifier = None
        self.df = None
        self.presenter = None
        self.rename_dialog = None
        self.rename_widgets = []

    def _setup(self):
        self.identifier, self.df = self.associated_dataframe_widget.presenter.getDataFrame(self.associated_dataframe_widget.identifier)
        self.presenter = self.associated_dataframe_widget.presenter

    def openRenameColumnHeaderDialog(self):
        def _add_rename_row():
            """Add a new row for renaming a column"""
            column_headers = self.df.columns.tolist()

            row_frame = tk.Frame(rename_columns_container)
            row_frame.pack(fill=tk.X, pady=2)

            # Row number label
            row_num_label = ttk.Label(row_frame, text=f"{len(self.rename_widgets) + 1}.", width=3)
            row_num_label.pack(side=tk.LEFT, padx=(0, 5))

            # Search/Column dropdown with autocomplete
            ttk.Label(row_frame, text="Column:").pack(side=tk.LEFT, padx=(0, 5))
            column_combo = ttk.Combobox(row_frame, state='normal', width=25, values=column_headers)
            if column_headers:
                column_combo.current(0)
            column_combo.pack(side=tk.LEFT, padx=5)

            # Arrow label
            ttk.Label(row_frame, text="→").pack(side=tk.LEFT, padx=5)

            # New name entry
            ttk.Label(row_frame, text="New Name:").pack(side=tk.LEFT, padx=(0, 5))
            new_name_entry = ttk.Entry(row_frame, width=25)
            new_name_entry.pack(side=tk.LEFT, padx=5)

            # Delete button for this row
            delete_button = ttk.Button(
                row_frame,
                text="✕",
                width=3,
                command=lambda: _remove_specific_row(row_frame)
            )
            delete_button.pack(side=tk.LEFT, padx=5)

            # Store references
            self.rename_widgets.append({
                'frame': row_frame,
                'column_combo': column_combo,
                'new_name_entry': new_name_entry
            })
        def _remove_specific_row(row_frame):
            """Remove a specific rename row"""
            # Find the widget dict that matches this frame
            for i, widget_dict in enumerate(self.rename_widgets):
                if widget_dict['frame'] == row_frame:
                    self.rename_widgets.pop(i)
                    row_frame.destroy()
                    _update_row_numbers()
                    break
        def _update_row_numbers():
            """Update the row numbers after deletion"""
            for i, widget_dict in enumerate(self.rename_widgets):
                # Find the label widget in the frame
                for child in widget_dict['frame'].winfo_children():
                    if isinstance(child, ttk.Label) and child.cget('width') == 3:
                        child.config(text=f"{i + 1}.")
                        break
        def _apply_rename():
            """Collect parameters and call presenter"""
            # Collect rename mappings
            rename_mapping = {}

            for widget_dict in self.rename_widgets:
                old_name = widget_dict['column_combo'].get()
                new_name = widget_dict['new_name_entry'].get().strip()

                if not old_name or not new_name:
                    status_label.config(text=f"Error: Missing new name detected '{new_name}'")
                    return

                if old_name and new_name:
                    # Check for duplicate new names
                    if new_name in rename_mapping.values():
                        status_label.config(text=f"Error: Duplicate new name '{new_name}'")
                        return

                    rename_mapping[old_name] = new_name

            if not rename_mapping:
                status_label.config(text="Please add at least one column to rename")
                return

            self.presenter.renameColumnHeaders(self.identifier, rename_mapping)

            status_label.config(text="")

            self._on_dialog_close_cleanup()


        self._setup()

        self.rename_dialog = tk.Toplevel()
        self.rename_dialog.title("Rename Column Headers")
        self.rename_dialog.geometry("700x500")

        # Setup cleanup logic when window closes
        self.rename_dialog.protocol("WM_DELETE_WINDOW", self._on_dialog_close_cleanup)

        # Main container
        main_container = tk.Frame(self.rename_dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- HEADER SECTION ---
        header_frame = tk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            header_frame,
            text="Rename Column Headers",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="Search for columns and assign new names. You can rename multiple columns at once.",
            font=("Arial", 9),
            foreground="gray"
        ).pack(anchor="w", pady=(5, 0))

        # --- RENAME SECTION ---
        rename_frame = ttk.LabelFrame(main_container, text="Column Renames", padding=10)
        rename_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Instructions
        ttk.Label(
            rename_frame,
            text="Select columns to rename and enter new names:",
            font=("Arial", 9, "bold")
        ).pack(anchor="w", pady=(0, 5))

        # Scrollable container for rename rows
        canvas_frame = tk.Frame(rename_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, height=250)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        rename_columns_container = tk.Frame(canvas)

        rename_columns_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=rename_columns_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add/Remove column buttons
        button_frame = tk.Frame(rename_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(button_frame, text="+ Add Column Rename", command=_add_rename_row).pack(side=tk.LEFT, padx=2)

        # --- ACTION BUTTONS ---
        action_frame = tk.Frame(main_container)
        action_frame.pack(fill=tk.X)

        ttk.Button(
            action_frame,
            text="Apply Renames",
            command=_apply_rename
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            action_frame,
            text="Cancel",
            command=self._on_dialog_close_cleanup
        ).pack(side=tk.LEFT, padx=5)

        # Error/Status label
        status_label = ttk.Label(main_container, text="", foreground="red")
        status_label.pack(pady=5)

        # Add first rename row by default
        _add_rename_row()

class ReorderColumnsDialog:
    def __init__(self, associated_dataframe_widget: DataFrameWidget):
        self.associated_dataframe_widget = associated_dataframe_widget

        # Will be setup later
        self.identifier = None
        self.df = None
        self.presenter = None

        self.reorder_dialog = None
        self.columns_to_move: list[str] = []  # accumulates chosen columns to move

    def _on_dialog_close_cleanup(self):
        if self.reorder_dialog:
            self.reorder_dialog.destroy()

        self.identifier = None
        self.df = None
        self.presenter = None
        self.reorder_dialog = None
        self.columns_to_move = []

    def _setup(self):
        self.identifier, self.df = self.associated_dataframe_widget.presenter.getDataFrame(
            self.associated_dataframe_widget.identifier
        )
        self.presenter = self.associated_dataframe_widget.presenter

    def openReorderColumnsDialog(self):
        def _add_column_to_move():
            selected = col_to_add_combo.get()
            if not selected:
                return
            if selected in self.columns_to_move:
                status_label.config(text=f"⚠ '{selected}' is already in the list.")
                return
            self.columns_to_move.append(selected)
            status_label.config(text="")
            _refresh_columns_to_move_list()
        def _remove_column_from_move(col_name: str):
            if col_name in self.columns_to_move:
                self.columns_to_move.remove(col_name)
                status_label.config(text="")
                _refresh_columns_to_move_list()
        def _refresh_columns_to_move_list():
            for widget in columns_list_container.winfo_children():
                widget.destroy()

            if not self.columns_to_move:
                ttk.Label(columns_list_container, text="(no columns added yet)", foreground="gray").pack(anchor="w", padx=5)
            else:
                for i, col in enumerate(self.columns_to_move):
                    row = tk.Frame(columns_list_container)
                    row.pack(fill=tk.X, pady=1)
                    ttk.Label(row, text=f"{i + 1}. {col}", width=35).pack(side=tk.LEFT, padx=5)
                    ttk.Button(
                        row, text="✕", width=3,
                        command=lambda c=col: _remove_column_from_move(c)
                    ).pack(side=tk.LEFT)

            columns_list_container.update_idletasks()
            list_canvas.configure(scrollregion=list_canvas.bbox("all"))
        def _apply_reorder():
            anchor = anchor_combo.get()

            # --- Validation ---
            errors = []
            if not anchor:
                errors.append("Anchor column must be selected.")
            if not self.columns_to_move:
                errors.append("At least one column to move must be added.")
            if anchor and anchor in self.columns_to_move:
                errors.append("Anchor column cannot also be in the columns-to-move list.")

            if errors:
                status_label.config(text="⚠ " + "  |  ".join(errors))
                return

            status_label.config(text="")

            reordered_df = self.presenter.reorderColumns(self.identifier, anchor, self.columns_to_move)
            if reordered_df is None:
                status_label.config(text="⚠ Reorder operation failed.")
                return

            self._open_reorder_preview_window(reordered_df)

        self._setup()

        self.reorder_dialog = tk.Toplevel()
        self.reorder_dialog.title("Reorder Columns")
        self.reorder_dialog.geometry("600x500")
        self.reorder_dialog.protocol("WM_DELETE_WINDOW", self._on_dialog_close_cleanup)

        column_headers = self.df.columns.tolist()

        main_container = tk.Frame(self.reorder_dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- HEADER ---
        ttk.Label(
            main_container,
            text="Reorder Columns",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        ttk.Label(
            main_container,
            text="Select an anchor column and the columns you want to place after it.",
            font=("Arial", 9),
            foreground="gray"
        ).pack(anchor="w", pady=(3, 10))

        # --- ANCHOR COLUMN ---
        anchor_frame = ttk.LabelFrame(main_container, text="Anchor Column", padding=10)
        anchor_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(anchor_frame, text="Place selected columns after:").pack(anchor="w", pady=(0, 4))
        anchor_combo = ttk.Combobox(anchor_frame, state="readonly", values=column_headers, width=35)
        anchor_combo.pack(anchor="w")

        # --- COLUMNS TO MOVE ---
        move_frame = ttk.LabelFrame(main_container, text="Columns to Move", padding=10)
        move_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(move_frame, text="Select a column and click 'Add':").pack(anchor="w", pady=(0, 4))

        add_row = tk.Frame(move_frame)
        add_row.pack(fill=tk.X)

        col_to_add_combo = ttk.Combobox(add_row, state="readonly", values=column_headers, width=30)
        col_to_add_combo.pack(side=tk.LEFT, padx=(0, 5))


        ttk.Button(add_row, text="+ Add", command=_add_column_to_move).pack(side=tk.LEFT)

        # Scrollable list of columns_to_move
        list_canvas_frame = tk.Frame(move_frame)
        list_canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        list_canvas = tk.Canvas(list_canvas_frame, height=150)
        list_scrollbar = ttk.Scrollbar(list_canvas_frame, orient="vertical", command=list_canvas.yview)
        columns_list_container = tk.Frame(list_canvas)

        columns_list_container.bind(
            "<Configure>",
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
        )
        list_canvas.create_window((0, 0), window=columns_list_container, anchor="nw")
        list_canvas.configure(yscrollcommand=list_scrollbar.set)

        list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        _refresh_columns_to_move_list()

        # --- ACTION BUTTONS ---
        action_frame = tk.Frame(main_container)
        action_frame.pack(fill=tk.X, pady=(0, 2))

        ttk.Button(action_frame, text="Apply Reorder", command=_apply_reorder).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel", command=self._on_dialog_close_cleanup).pack(side=tk.LEFT, padx=5)

        status_label = ttk.Label(main_container, text="", foreground="red", wraplength=560)
        status_label.pack(anchor="w", pady=2)

    def _open_reorder_preview_window(self, reordered_df: pd.DataFrame):
        def on_overwrite():
            self.presenter.overwriteDFInExistingDataframeEntry(reordered_df, self.identifier)
            preview_window.destroy()
            self._on_dialog_close_cleanup()

        def on_save_as_new():
            new_name = new_df_name_entry.get().strip()
            if not new_name:
                new_df_name_entry.config(background="#ffcccc")
                return
            self.presenter.loadDataframeEntryFromPandasDFAndUpdateView(reordered_df, new_name)
            preview_window.destroy()
            self._on_dialog_close_cleanup()

        def on_discard():
            preview_window.destroy()

        preview_window = tk.Toplevel(self.reorder_dialog)
        preview_window.title("Preview Reordered Columns")
        preview_window.geometry("800x600")
        preview_window.transient(self.reorder_dialog)
        preview_window.grab_set()

        tk.Label(preview_window, text="Review the reordered columns below.",
                 font=("Arial", 11, "bold"), pady=10).pack()

        table_frame = tk.Frame(preview_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        pt = Table(table_frame, dataframe=reordered_df, showstatusbar=True)
        pt.show()

        controls_frame = tk.Frame(preview_window, bg="#f0f0f0", bd=1, relief=tk.SUNKEN)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(controls_frame, text="New DF Name (if saving as new):", bg="#f0f0f0").pack(side=tk.LEFT, padx=5, pady=10)
        new_df_name_entry = tk.Entry(controls_frame, width=40)
        new_df_name_entry.insert(0, f"{self.identifier}_reordered")
        new_df_name_entry.pack(side=tk.LEFT, padx=5, pady=10)

        btn_container = tk.Frame(preview_window)
        btn_container.pack(pady=10)

        tk.Button(btn_container, text="Overwrite Existing DF", command=on_overwrite, bg="#ffcc80", width=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_container, text="Save As New DF", command=on_save_as_new, bg="#90ee90", width=20).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_container, text="Discard / Delete", command=on_discard, bg="#ffab91", width=20).pack(side=tk.LEFT, padx=10)

class DataFrameNotFoundError(Exception):
    """Raised when a DataFrame cannot be found in the model."""
    pass


