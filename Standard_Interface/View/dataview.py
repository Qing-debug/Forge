from typing import override
import typing
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from pandastable import Table
from returns.result import Success
import pandas as pd
if typing.TYPE_CHECKING: #datapresenter used for type annotation but it leads to circular import runtime error without this. This lets us keep the benefits of type annotation
    from Forge.Standard_Interface.Presenter import datapresenter
from Forge.Standard_Interface.View import dataframe_ui_class


class DataView:
    _singleton = None
    _singleton_exist = False

    @override
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super().__new__(cls)
            return cls._singleton
        return cls._singleton

    @override
    def __init__(self):
        if not self.__class__._singleton_exist:
            self.presenter = None

            self.root = tk.Tk()
            self.df_name_container = None

            self.pandas_table_frame_left = None
            self.pandas_table_left = None
            self.pandas_table_frame_right = None
            self.pandas_table_right = None

            self.curr_selected_table = tk.StringVar()
            self.curr_selected_table.set("left")


            self.__class__._singleton_exist = True

    def setup(self, presenter: 'datapresenter.DataPresenter'):

        self.presenter = presenter
        self.root.title("My Window")
        self.root.geometry("1400x1000")

        #creating and populating toolbar
        toolbar = ViewToolbar(self.root, view = self, presenter = self.presenter, bd=1, relief=tk.RAISED)
        toolbar.setup()
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.df_name_container = tk.Listbox(self.root, width = 50)
        self.df_name_container.pack()
        self.df_name_container.bind("<<ListboxSelect>>", self._onSelectInDFNameContainer)

        tk.Radiobutton(self.root, text = "Left Frame", variable = self.curr_selected_table, value = "left").pack()
        tk.Radiobutton(self.root, text = "Right Frame", variable=self.curr_selected_table, value= "right").pack()

        pandas_table_parent_frame = tk.Frame(self.root, bg = "yellow")
        pandas_table_parent_frame.pack()
        self.pandas_table_frame_left = tk.Frame(pandas_table_parent_frame, bg = "red")
        self.pandas_table_frame_left.pack(side=tk.LEFT)
        self.pandas_table_frame_right = tk.Frame(pandas_table_parent_frame, bg = "blue")
        self.pandas_table_frame_right.pack(side=tk.RIGHT)
        print("Setup successfully completed")

    def start(self):
        if self.presenter is None:
            print("Required reference to presenter object is missing.")
            return
        self.root.mainloop()

    def updateDFNameContainer(self, new_DF_name_container: list[str]):
        self.df_name_container.delete(0, tk.END)
        for name in new_DF_name_container:
            self.df_name_container.insert(tk.END, name)
        return Success("DF container successfully updated") #success path

    def _onSelectInDFNameContainer(self, event):
        selection = event.widget.curselection()

        #if nothing is chosen, then don't do anything
        if not selection:
            return

        selected_index = selection[0]
        df_name = event.widget.get(selected_index)
        self.presenter.getSelectedDataframeAndLoadOnView(df_name)

    #Refactor this. It looks like alot of duplicate code, surely there's a better way to do this
    def loadSelectedDF(self, identifier: str, df: pd.DataFrame):
        print(self.curr_selected_table.get())
        if self.curr_selected_table.get() == "left":
            if self.pandas_table_left is not None:
                self.pandas_table_left.destroy()

            self.pandas_table_left = dataframe_ui_class.DataFrameWidget(self, self.pandas_table_frame_left, identifier, self.presenter, df)
            self.pandas_table_left.setup()
            self.pandas_table_left.pack()

        elif self.curr_selected_table.get() == "right":
            if self.pandas_table_right is not None:
                self.pandas_table_right.destroy()

            self.pandas_table_right = dataframe_ui_class.DataFrameWidget(self, self.pandas_table_frame_right, identifier, self.presenter, df)
            self.pandas_table_right.setup()
            self.pandas_table_right.pack()

    def getDFNameContainer(self):
        return self.df_name_container

    #Used to update the tables so changes are reflected instantly
    def redrawTables(self):
        if self.pandas_table_left is not None:
            self.pandas_table_left.updateTable()
        if self.pandas_table_right is not None:
            self.pandas_table_right.updateTable()


class ViewToolbar(tk.Frame):
    def __init__(self, master = None, view = None, presenter = None, cnf={}, **kw):
        super().__init__(master, cnf, **kw)
        self.view = view
        self.presenter = presenter

        #setup by calling setup
        self.concat_df_dialog = None
        self.save_df_dialog = None

    def setup(self):
        self.concat_df_dialog = ConcatDFDialog(self.view, self.presenter)
        self.save_df_dialog = SaveDataframeDialog(self.view, self.presenter)

        load_csv_btn = tk.Button(self, text="Load CSV", command=self._onButtonClickPickAndLoadFile)
        load_csv_btn.pack(side=tk.LEFT, padx=2, pady=2)

        concat_df_btn = tk.Button(self, text="Concat DFs", command=self._openConcatDFDialog)
        concat_df_btn.pack(side=tk.LEFT, padx=2, pady=2)

        save_df_btn = tk.Button(self, text="Save DF", command=self._saveDFAsCSV)
        save_df_btn.pack(side=tk.LEFT, padx=2, pady=2)

    def _onButtonClickPickAndLoadFile(self):
        file_path_str = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        file_name = file_path_str[file_path_str.rfind('/') + 1: file_path_str.rfind('.')]
        self.presenter.loadDataframeEntryFromFilePathAndUpdateView(file_path_str, file_name)

    def _openConcatDFDialog(self):
        self.concat_df_dialog.openConcatDFDialog()

    def _saveDFAsCSV(self):
        self.save_df_dialog.openSaveDFDialog()


class ConcatDFDialog:
    #leave empty for now, will populate later on when I have a clearer idea of how things should look
    def __init__(self, view: 'dataview.DataView', presenter: 'datapresenter.DataPresenter'):
        self.view = view
        self.presenter = presenter

        #probably need to reset this when we close the dialog so class is ready to be used again
        self.concat_df_dialog = None
        self.names_of_df_to_concat = []

        self.selected_df_to_concat_container = None

    def _add_or_remove_chosen_df(self, event):
        selection = event.widget.curselection()
        #if nothing is chosen, then don't do anything
        if not selection:
            return

        selected_index = selection[0]
        df_name = event.widget.get(selected_index)

        if df_name not in self.names_of_df_to_concat:
            self.names_of_df_to_concat.append(df_name)
        else:
            self.names_of_df_to_concat.remove(df_name)

        event.widget.selection_clear(selected_index)


        #rerender part of openConcatDFDialog that shows the content of the set.
        for widget in self.selected_df_to_concat_container.winfo_children():
            widget.destroy()

        tk.Label(self.selected_df_to_concat_container, text="Selected Dataframes To Concatenate:").pack(side=tk.LEFT,
                                                                                                        padx=5)
        tk.Label(self.selected_df_to_concat_container, text=str(self.names_of_df_to_concat)).pack(side=tk.LEFT, padx=5)

    def _onConcatDialogCloseCleanup(self):
        self.concat_df_dialog.destroy()
        self.names_of_df_to_concat.clear()

    def openConcatDFDialog(self):
        def validateAndApply(concat_df_name: str, join: str, axis: str, ignore_index: str):
            missing_items = []
            #validate and perform error checking in terms of user input
            if not concat_df_name:
                missing_items.append("Name for concatted DF")

            if len(self.names_of_df_to_concat) < 2:
                missing_items.append("Select Least Two Dataframes")

            if not join:
                missing_items.append("Join Value")

            if not axis:
                missing_items.append("Axis Value")

            if not ignore_index:
                missing_items.append("Ignore Index Value")

            if missing_items:
                error_text = "⚠ Missing: " + ", ".join(missing_items)
                error_label.config(text=error_text)
                error_label.pack(pady=5)  # Ensure it is visible
                return

            error_label.pack_forget()

            #build kwargs
            concat_param = {"join": join, "axis": axis, "ignore_index": ignore_index}
            concat_df = self.presenter.concatDataframes(self.names_of_df_to_concat, concat_param)
            # self.onConcatDialogCloseCleanup() #
            #might need to open up a new dialog for user to verify if they want to keep or get rid of the concatted df
            self._open_concat_df_preview_window(concat_df_name, concat_df)

        self.concat_df_dialog = tk.Toplevel()
        self.concat_df_dialog.title("Concatenate Dataframes")
        self.concat_df_dialog.geometry("700x500")

        self.concat_df_dialog.protocol("WM_DELETE_WINDOW", self._onConcatDialogCloseCleanup)


        main_form_container = tk.Frame(self.concat_df_dialog)
        main_form_container.pack()


        df_name_container = tk.Listbox(main_form_container)
        for item in self.view.getDFNameContainer().get(0, tk.END):
            df_name_container.insert(tk.END, item)
        df_name_container.pack()

        df_name_container.bind('<<ListboxSelect>>', lambda event: self._add_or_remove_chosen_df(event))

        tk.Label(main_form_container, text = "Left click to add to list of dfs to concat. Left click again to remove from list.")
        self.selected_df_to_concat_container = tk.Frame(main_form_container)
        self.selected_df_to_concat_container.pack()
        tk.Label(self.selected_df_to_concat_container, text = "Selected Dataframes To Concatenate:").pack(side = tk.LEFT, padx=5)
        tk.Label(self.selected_df_to_concat_container, text = str(self.names_of_df_to_concat)).pack(side = tk.LEFT, padx=5) #this needs to be rerendered everytime we click on the listbox.

        parameter_container = tk.Frame(main_form_container)
        parameter_container.pack()

        tk.Label(parameter_container, text="Name: ").grid(row=0, column=0)
        concat_df_name_entry = tk.Entry(parameter_container)
        concat_df_name_entry.grid(row=0, column=1)

        tk.Label(parameter_container, text = "Join: ").grid(row = 1, column = 0)
        join_param_combobox = ttk.Combobox(parameter_container, state = 'readonly', values = ["inner", "outer"])
        join_param_combobox.grid(row = 1, column = 1)

        tk.Label(parameter_container, text = "Axis: ").grid(row = 2, column = 0)
        axis_param_combobox = ttk.Combobox(parameter_container, state = 'readonly', values = ["0", "1"])
        axis_param_combobox.grid(row= 2, column=1)

        tk.Label(parameter_container, text = "Ignore Index: ").grid(row = 3, column = 0)
        ignore_index_combobox = ttk.Combobox(parameter_container, state = 'readonly', values = ["True", "False"])
        ignore_index_combobox.grid(row = 3, column = 1)

        tk.Button(main_form_container, text = "Apply", command = lambda: validateAndApply(concat_df_name_entry.get(), join_param_combobox.get(), axis_param_combobox.get(), ignore_index_combobox.get())).pack()
        error_label = tk.Label(main_form_container, text="", fg="red", font=("Arial", 9, "bold"))

    def _open_concat_df_preview_window(self, concat_df_name: str, concat_df: pd.DataFrame):
        def on_keep():
            print(f"Keeping dataframe: {concat_df_name}")

            # Assuming you want to add it to the view:
            self.presenter.loadDataframeEntryFromPandasDFAndUpdateView(concat_df, concat_df_name)

            preview_window.destroy()
            self._onConcatDialogCloseCleanup()

        def on_discard():
            print("Discarding merge result")
            preview_window.destroy()
            # We do NOT close the main merge tool, so user can try different settings


        # 1. Create the window as a child of the merge dialog
        preview_window = tk.Toplevel(self.concat_df_dialog)
        preview_window.title(f"Preview Concat Result: {concat_df_name}")
        preview_window.geometry("700x700")

        # 2. Make it modal (User must interact with this window before clicking anything else)
        preview_window.grab_set()

        # 3. Label
        tk.Label(preview_window, text="Review the concatted data. Click 'Keep' to save to memory.",
                 font=("Arial", 10, "bold"), pady=10).pack()

        # 4. Show DataFrame using PandaStable
        table_frame = tk.Frame(preview_window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        pt = Table(table_frame, dataframe=concat_df, showstatusbar=True)
        pt.show()

        # 5. Buttons Container
        btn_frame = tk.Frame(preview_window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Keep / Save", command=on_keep, bg="#ddffdd", width=15).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Discard", command=on_discard, bg="#ffdddd", width=15).pack(side=tk.LEFT, padx=10)


class SaveDataframeDialog:
    def __init__(self, view: 'dataview.DataView', presenter: 'datapresenter.DataPresenter'):
        self.view = view
        self.presenter = presenter


    def openSaveDFDialog(self):


        def on_confirm_save():
            selection = select_df_listbox.curselection()
            print("This is what im selecting:", selection)
            if not selection:
                msg_label.config(text="⚠ Please select a DataFrame first.")
                return


            df_name = select_df_listbox.get(selection[0])


            file_path = filedialog.asksaveasfilename(
                parent=dialog_window,
                defaultextension=".csv",
                initialfile=f"{df_name}.csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save DataFrame as..."
            )

            self.presenter.saveDataframeAsCSV(df_name, file_path)
            dialog_window.destroy()


        """
        Opens a dialog populated with names from the main view's listbox.
        Allows user to select one and save it.
        """

        # 1. Setup the Dialog Window
        dialog_window = tk.Toplevel()
        dialog_window.title("Save DataFrame")
        dialog_window.geometry("400x400")
        dialog_window.grab_set()  # Make window modal (blocks interaction with main window)

        tk.Label(dialog_window, text="Select a DataFrame to save:", font=("Arial", 10, "bold")).pack(pady=10)

        # 2. Create the Listbox Container
        list_frame = tk.Frame(dialog_window)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)

        # We create a local listbox for this dialog
        select_df_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=("Arial", 10))
        scrollbar.config(command=select_df_listbox.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        select_df_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 3. Populate Listbox from the Main View
        # We access the main view's listbox helper method to get the widget, then retrieve items
        main_listbox_items = self.view.getDFNameContainer().get(0, tk.END)

        for name in main_listbox_items:
            select_df_listbox.insert(tk.END, name)

        # Feedback Label
        msg_label = tk.Label(dialog_window, text="", fg="red")
        msg_label.pack(pady=5)

        # 5. Buttons
        btn_frame = tk.Frame(dialog_window)
        btn_frame.pack(pady=15, fill=tk.X)

        tk.Button(btn_frame, text="Save as CSV", command=on_confirm_save, bg="#e1f5fe", width=15).pack(side=tk.RIGHT,
                                                                                                       padx=20)
        tk.Button(btn_frame, text="Cancel", command=dialog_window.destroy, width=10).pack(side=tk.RIGHT)







































