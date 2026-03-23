import tkinter as tk
from tkinter import ttk

from pandastable import Table
import typing

if typing.TYPE_CHECKING: # dataview used for type annotation but it leads to circular import runtime error without this. This lets us keep the benefits of type annotation
    pass
if typing.TYPE_CHECKING: #datapresenter used for type annotation but it leads to circular import runtime error without this. This lets us keep the benefits of type annotation
    from Presenter import datapresenter

class AggregateDialog:
    def __init__(self, associated_dataframe_widget):
        self.associated_dataframe_widget = associated_dataframe_widget

        #will be setup later
        self.identifier = None
        self.df = None
        self.presenter = None


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

        aggregate_dialog = tk.Toplevel()
        aggregate_dialog.title("Aggregate Data")
        aggregate_dialog.geometry("600x400")

        column_headers = self.df.columns.tolist()

        # --- LEFT SIDE: Column List ---
        list_frame = ttk.LabelFrame(aggregate_dialog, text="Available Columns")
        list_frame.pack(side="left", fill="y", padx=10, pady=10)
        col_listbox = tk.Listbox(list_frame, height=15)

        for col in column_headers:
            col_listbox.insert(tk.END, col)
        col_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        # --- RIGHT SIDE: Formula Bar ---
        right_frame = ttk.Frame(aggregate_dialog)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ttk.Label(right_frame, text="Type your formula here:").pack(anchor="w")

        aggregate_df_name = tk.Entry(right_frame)
        aggregate_df_name.pack(fill="x", pady=5)

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
        calc_btn = ttk.Button(right_frame, text="Create Column Based Off formula", command = lambda: self._calculate(formula_text, aggregate_dialog, result_label, aggregate_df_name.get(), error_label))
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
    def _calculate(self, formula_text: tk.Text, aggregate_dialog: tk.Toplevel, result_label: ttk.Label, aggregate_df_name: str, error_label: ttk.Label):

        raw_formula = formula_text.get("1.0", tk.END).strip()
        raw_name = aggregate_df_name.strip()

        # 2. Validation Logic
        if not raw_name:
            error_label.config(text="Error: Please enter a name for the new DataFrame.")
            return  # Stop execution

        if not raw_formula:
            error_label.config(text="Error: Formula field cannot be empty.")
            return  # Stop execution

        # 3. If validation passes, clear the error label
        error_label.config(text="")


        #validation check - aggregate_df_name msut be non-empty and formula_text must be non-empty + a valid mathematical expression, point out these things on the
        #aggregate dialog through an error label. Only call presenter.withinDataframeAggregation if the aforementioned things are valid.

        result_label.config(text=f"Python will execute: {raw_formula}") #maybe put this on the keep/save as/discard dialog so users can see what expression was evaluated

        print(f"Raw Formula: {raw_formula}")

        #-----------------------------------code for the keep/save/as/discard-----------------------------------
        data = self.presenter.withinDataframeAggregation(self.identifier, raw_formula)

        child = tk.Toplevel(aggregate_dialog)
        child.title("Child Dialog")
        child.geometry("1000x1000")

        child.transient(aggregate_dialog)

        # 2. Add widgets to child
        tk.Label(child, text="I am the child!").pack(pady=10)
        tk.Button(child, text="Close", command=child.destroy).pack()

        child.grab_set()

        container = tk.Frame(child)
        container.pack()
        table = Table(container, dataframe=data, showstatusbar=True)
        table.show()
        # -----------------------------------keep/save as/discard dialog-----------------------------------


    # def _open_aggregated_df_preview_window(self, merged_df: pd.DataFrame, new_df_name: str):




