from qtpy.QtCore import Qt
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..gui_utils import (
    BaseConfigDialog,
    _addComboInput,
    _addLineInput,
    _addTextInput,
    _parseLines,
    _parseBoolList,
)


class ReplaceValueDialog(BaseConfigDialog):
    dialog_title = 'Replace Value Configuration'
    extra_width = 200

    def _setupUi(self):
        # Help note
        help_text = QLabel(
            'Mode 1 (Specific): Replace exactly one value in a column - '
            'use for targeted fixes (e.g., fix a typo, remap a sentinel).\n'
            'Mode 2 (All): Replace every unique value in a column with a '
            'complete mapping and set the column data type - use for '
            'recoding an entire column (e.g., mapping codes to labels).'
        )
        help_text.setWordWrap(True)
        self._layout.addWidget(help_text)

        # Mode selector
        current_mode = getattr(self.node, 'mode', 'specific') or 'specific'
        mode_display = 'Specific' if current_mode == 'specific' else 'All'
        self.mode_combo = _addComboInput(
            self._layout, 'Mode:', ['Specific', 'All'],
            current_value=mode_display, default='Specific',
        )
        self.mode_combo.currentIndexChanged.connect(self._onModeChanged)

        # Column (shared by both modes)
        self.column_input = _addLineInput(self._layout, 'Column Name:', self.node.column_header)

        # --- Mode 1 ("Specific") widgets ---
        self._mode1_group = QWidget()
        mode1_layout = QVBoxLayout(self._mode1_group)
        mode1_layout.setContentsMargins(0, 0, 0, 0)

        old_val = ''
        new_val = ''
        if self.node.mappings and current_mode == 'specific':
            old_val = self.node.mappings[0].get('old', '')
            new_val = self.node.mappings[0].get('new', '')
        self.old_value_input = _addLineInput(mode1_layout, 'Old Value:', old_val)
        self.new_value_input = _addLineInput(mode1_layout, 'New Value:', new_val)
        self._layout.addWidget(self._mode1_group)

        # --- Mode 2 ("All") widgets ---
        self._mode2_group = QWidget()
        mode2_layout = QVBoxLayout(self._mode2_group)
        mode2_layout.setContentsMargins(0, 0, 0, 0)

        self.replacement_type_combo = _addComboInput(
            mode2_layout, 'Column Data Type (all data in column will be cast to this type):',
            [('string (text)', 'string'), ('integer (whole number)', 'integer'), ('float (decimal)', 'float')],
            current_value=self.node.replacement_type, default='string',
        )

        mode2_layout.addWidget(QLabel('Mappings (old → new):'))
        self.mapping_table = QTableWidget(0, 2)
        self.mapping_table.setHorizontalHeaderLabels(['Old Value', 'New Value'])
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        mode2_layout.addWidget(self.mapping_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addMappingRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeMappingRow)
        btn_layout.addWidget(remove_btn)
        mode2_layout.addLayout(btn_layout)

        self._layout.addWidget(self._mode2_group)

        # Populate Mode 2 table from saved mappings
        if self.node.mappings and current_mode == 'all':
            for m in self.node.mappings:
                row = self.mapping_table.rowCount()
                self._addMappingRow()
                self.mapping_table.item(row, 0).setText(m.get('old', ''))
                self.mapping_table.item(row, 1).setText(m.get('new', ''))
        elif current_mode == 'all':
            self._addMappingRow()

        # Set initial visibility
        self._onModeChanged()

    def _onModeChanged(self):
        is_specific = self.mode_combo.currentText() == 'Specific'
        self._mode1_group.setVisible(is_specific)
        self._mode2_group.setVisible(not is_specific)

    def _addMappingRow(self):
        row = self.mapping_table.rowCount()
        self.mapping_table.insertRow(row)
        self.mapping_table.setItem(row, 0, QTableWidgetItem(''))
        self.mapping_table.setItem(row, 1, QTableWidgetItem(''))

    def _removeMappingRow(self):
        row = self.mapping_table.currentRow()
        if row >= 0:
            self.mapping_table.removeRow(row)

    def _onSave(self):
        self._clearErrorStyles()

        column = self.column_input.text().strip()
        if not column:
            self._setErrorStyle(self.column_input)
            self.status_label.setText('Error: Column name is required')
            return

        is_specific = self.mode_combo.currentText() == 'Specific'

        if is_specific:
            old_val = self.old_value_input.text().strip()
            if not old_val:
                self._setErrorStyle(self.old_value_input)
                self.status_label.setText('Error: Old value is required')
                return
            new_val = self.new_value_input.text().strip()
            if not new_val:
                self._setErrorStyle(self.new_value_input)
                self.status_label.setText('Error: New value is required')
                return

            self.node.mode = 'specific'
            self.node.column_header = column
            self.node.mappings = [{'old': old_val, 'new': new_val}]
            self.node.replacement_type = None
            self.accept()
        else:
            # Mode 2 ("All")
            row_count = self.mapping_table.rowCount()
            if row_count == 0:
                self.status_label.setText(
                    'Error: At least one mapping row is required'
                )
                return

            mappings = []
            for row in range(row_count):
                old_item = self.mapping_table.item(row, 0)
                new_item = self.mapping_table.item(row, 1)
                old_val = old_item.text().strip() if old_item else ''
                new_val = new_item.text().strip() if new_item else ''
                if not old_val:
                    self.mapping_table.selectRow(row)
                    self.status_label.setText(
                        f'Error: Row {row + 1}: old value is required'
                    )
                    return
                if not new_val:
                    self.mapping_table.selectRow(row)
                    self.status_label.setText(
                        f'Error: Row {row + 1}: new value is required'
                    )
                    return
                mappings.append({'old': old_val, 'new': new_val})

            # Check for duplicate old values
            old_vals = [m['old'] for m in mappings]
            if len(old_vals) != len(set(old_vals)):
                self.status_label.setText('Error: Duplicate old values in mappings')
                return

            self.node.mode = 'all'
            self.node.column_header = column
            self.node.mappings = mappings
            self.node.replacement_type = self.replacement_type_combo.currentData()
            self.accept()


class ComputeColumnDialog(BaseConfigDialog):
    dialog_title = 'Compute Column Configuration'
    extra_width = 100

    def _setupUi(self):
        self.new_column_input = _addLineInput(
            self._layout, 'New Column Name:', self.node.new_column
        )
        self.formula_input = _addLineInput(
            self._layout, 'Formula:', self.node.formula, "col_a + col_b"
        )

    def _onSave(self):
        new_column = self.new_column_input.text().strip()
        if not new_column:
            self.status_label.setText('Error: New column name is required')
            return

        formula = self.formula_input.text().strip()
        if not formula:
            self.status_label.setText('Error: Formula is required')
            return

        self.node.new_column = new_column
        self.node.formula = formula
        self.accept()


class SortByColumnDialog(BaseConfigDialog):
    dialog_title = 'Sort by Column Configuration'
    extra_width = 100

    def _setupUi(self):
        self.sort_table = QTableWidget(0, 2)
        self.sort_table.setHorizontalHeaderLabels(['Column Name', 'Direction'])
        header = self.sort_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.sort_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addSortRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeSortRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        # Repopulate from saved data
        if self.node.sort_columns:
            ascending_list = self.node.ascending_list or []
            for i, col in enumerate(self.node.sort_columns):
                self._addSortRow()
                self.sort_table.item(i, 0).setText(col)
                direction_combo = self.sort_table.cellWidget(i, 1)
                if i < len(ascending_list) and not ascending_list[i]:
                    direction_combo.setCurrentText('Descending')
        else:
            self._addSortRow()

        self.ignore_index_checkbox = QCheckBox('Reset Index')
        self.ignore_index_checkbox.setChecked(bool(self.node.ignore_index))
        self._layout.addWidget(self.ignore_index_checkbox)

    def _addSortRow(self):
        row = self.sort_table.rowCount()
        self.sort_table.insertRow(row)
        self.sort_table.setItem(row, 0, QTableWidgetItem(''))
        direction_combo = QComboBox()
        direction_combo.setEditable(False)
        direction_combo.addItems(['Ascending', 'Descending'])
        self.sort_table.setCellWidget(row, 1, direction_combo)

    def _removeSortRow(self):
        row = self.sort_table.currentRow()
        if row >= 0:
            self.sort_table.removeRow(row)

    def _onSave(self):
        self._clearErrorStyles()

        row_count = self.sort_table.rowCount()
        if row_count == 0:
            self.status_label.setText('Error: At least one sort column is required')
            return

        sort_columns = []
        ascending_list = []
        for row in range(row_count):
            col_item = self.sort_table.item(row, 0)
            col_name = col_item.text().strip() if col_item else ''
            if not col_name:
                self.sort_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: column name is required'
                )
                return
            sort_columns.append(col_name)
            direction_combo = self.sort_table.cellWidget(row, 1)
            ascending_list.append(direction_combo.currentText() == 'Ascending')

        if len(set(sort_columns)) != len(sort_columns):
            self.status_label.setText('Error: Duplicate column names')
            return

        self.node.sort_columns = sort_columns
        self.node.ascending_list = ascending_list
        self.node.ignore_index = self.ignore_index_checkbox.isChecked()
        self.accept()


class RenameColumnDialog(BaseConfigDialog):
    dialog_title = 'Rename Column Configuration'
    extra_width = 100

    def _setupUi(self):
        note = QLabel('Each row renames one column: old column -> new column')
        note.setWordWrap(True)
        self._layout.addWidget(note)

        self.rename_table = QTableWidget(0, 2)
        self.rename_table.setHorizontalHeaderLabels(['Old Column Name', 'New Column Name'])
        header = self.rename_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.rename_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addRenameRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeRenameRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        if self.node.rename_mappings:
            for mapping in self.node.rename_mappings:
                old_name = mapping.get('old', '') if isinstance(mapping, dict) else ''
                new_name = mapping.get('new', '') if isinstance(mapping, dict) else ''
                self._addRenameRow(str(old_name), str(new_name))
        else:
            self._addRenameRow()

    def _addRenameRow(self, old_name='', new_name=''):
        row = self.rename_table.rowCount()
        self.rename_table.insertRow(row)
        self.rename_table.setItem(row, 0, QTableWidgetItem(old_name))
        self.rename_table.setItem(row, 1, QTableWidgetItem(new_name))

    def _removeRenameRow(self):
        row = self.rename_table.currentRow()
        if row >= 0:
            self.rename_table.removeRow(row)

    def _onSave(self):
        row_count = self.rename_table.rowCount()
        if row_count == 0:
            self.status_label.setText('Error: At least one rename row is required')
            return

        mappings = []
        old_names = set()
        new_names = set()
        for row in range(row_count):
            old_item = self.rename_table.item(row, 0)
            new_item = self.rename_table.item(row, 1)
            old_name = old_item.text().strip() if old_item else ''
            new_name = new_item.text().strip() if new_item else ''

            if not old_name:
                self.rename_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: old column name is required'
                )
                return
            if not new_name:
                self.rename_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: new column name is required'
                )
                return

            if old_name in old_names:
                self.status_label.setText(f"Error: Duplicate old name '{old_name}'")
                return
            if new_name in new_names:
                self.status_label.setText(f"Error: Duplicate new name '{new_name}'")
                return
            mappings.append({'old': old_name, 'new': new_name})
            old_names.add(old_name)
            new_names.add(new_name)

        self.node.rename_mappings = mappings
        self.accept()


class ReorderColumnDialog(BaseConfigDialog):
    dialog_title = 'Reorder Column Configuration'
    extra_width = 100

    def _setupUi(self):
        self.anchor_input = _addLineInput(
            self._layout, 'Anchor Column:', self.node.anchor_column
        )

        note = QLabel('Columns listed below will be placed immediately after the anchor column, in order.')
        note.setWordWrap(True)
        self._layout.addWidget(note)

        self.columns_table = QTableWidget(0, 1)
        self.columns_table.setHorizontalHeaderLabels(['Column to Move'])
        header = self.columns_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.columns_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        if self.node.columns_to_move:
            for col in self.node.columns_to_move:
                row = self.columns_table.rowCount()
                self._addRow()
                self.columns_table.item(row, 0).setText(col)
        else:
            self._addRow()

    def _addRow(self):
        row = self.columns_table.rowCount()
        self.columns_table.insertRow(row)
        self.columns_table.setItem(row, 0, QTableWidgetItem(''))

    def _removeRow(self):
        row = self.columns_table.currentRow()
        if row >= 0:
            self.columns_table.removeRow(row)

    def _onSave(self):
        self._clearErrorStyles()

        anchor = self.anchor_input.text().strip()
        if not anchor:
            self._setErrorStyle(self.anchor_input)
            self.status_label.setText('Error: Anchor column is required')
            return

        row_count = self.columns_table.rowCount()
        if row_count == 0:
            self.status_label.setText('Error: At least one column to move is required')
            return

        columns_to_move = []
        for row in range(row_count):
            item = self.columns_table.item(row, 0)
            col = item.text().strip() if item else ''
            if not col:
                self.columns_table.selectRow(row)
                self.status_label.setText(f'Error: Row {row + 1}: column name is required')
                return
            if col == anchor:
                self.columns_table.selectRow(row)
                self.status_label.setText(f'Error: Row {row + 1}: anchor column cannot be in columns to move')
                return
            if col in columns_to_move:
                self.columns_table.selectRow(row)
                self.status_label.setText(f'Error: Row {row + 1}: duplicate column "{col}"')
                return
            columns_to_move.append(col)

        self.node.anchor_column = anchor
        self.node.columns_to_move = columns_to_move
        self.accept()


class MergeDialog(BaseConfigDialog):
    dialog_title = 'Merge Configuration'
    extra_width = 200

    def _setupUi(self):
        self.how_combo = _addComboInput(
            self._layout, 'How:', [
                ('inner (only matching rows)', 'inner'),
                ('outer (all rows from both)', 'outer'),
                ('left (all rows from left)', 'left'),
                ('right (all rows from right)', 'right'),
            ],
            current_value=self.node.how, default='inner',
        )

        # Merge conditions table
        note = QLabel(
            'Each row is a join key pair; all rows are applied together. '
            'If both sides use the same column name, type it in both fields.'
        )
        note.setWordWrap(True)
        self._layout.addWidget(note)

        self.conditions_table = QTableWidget(0, 2)
        self.conditions_table.setHorizontalHeaderLabels(['Left Column', 'Right Column'])
        header = self.conditions_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.conditions_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addConditionRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeConditionRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        # Repopulate from saved merge_conditions
        if self.node.merge_conditions:
            for left_col, right_col in self.node.merge_conditions:
                row = self.conditions_table.rowCount()
                self._addConditionRow()
                self.conditions_table.item(row, 0).setText(left_col)
                self.conditions_table.item(row, 1).setText(right_col)
        else:
            self._addConditionRow()

        # Suffixes
        self.suffix_left_input = _addLineInput(
            self._layout, 'Left Suffix:', self.node.suffix_left
        )
        self.suffix_right_input = _addLineInput(
            self._layout, 'Right Suffix:', self.node.suffix_right
        )
        suffix_note = QLabel('Added to overlapping column names to avoid conflicts')
        suffix_note.setStyleSheet('QLabel { color: #666; font-style: italic; }')
        suffix_note.setWordWrap(True)
        self._layout.addWidget(suffix_note)

    def _addConditionRow(self):
        row = self.conditions_table.rowCount()
        self.conditions_table.insertRow(row)
        self.conditions_table.setItem(row, 0, QTableWidgetItem(''))
        self.conditions_table.setItem(row, 1, QTableWidgetItem(''))

    def _removeConditionRow(self):
        row = self.conditions_table.currentRow()
        if row >= 0:
            self.conditions_table.removeRow(row)

    def _onSave(self):
        self._clearErrorStyles()

        how = self.how_combo.currentData()

        # Validate merge conditions
        row_count = self.conditions_table.rowCount()
        if row_count == 0:
            self.status_label.setText(
                'Error: At least one join key pair is required'
            )
            return

        merge_conditions = []
        for row in range(row_count):
            left_item = self.conditions_table.item(row, 0)
            right_item = self.conditions_table.item(row, 1)
            left_col = left_item.text().strip() if left_item else ''
            right_col = right_item.text().strip() if right_item else ''
            if not left_col:
                self.conditions_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: left column is required'
                )
                return
            if not right_col:
                self.conditions_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: right column is required'
                )
                return
            merge_conditions.append((left_col, right_col))

        # Validate suffixes
        suffix_left = self.suffix_left_input.text().strip()
        if not suffix_left:
            self._setErrorStyle(self.suffix_left_input)
            self.status_label.setText('Error: Left suffix cannot be empty')
            return
        suffix_right = self.suffix_right_input.text().strip()
        if not suffix_right:
            self._setErrorStyle(self.suffix_right_input)
            self.status_label.setText('Error: Right suffix cannot be empty')
            return
        if suffix_left == suffix_right:
            self._setErrorStyle(self.suffix_left_input)
            self._setErrorStyle(self.suffix_right_input)
            self.status_label.setText(
                'Error: Left and right suffixes cannot be the same'
            )
            return

        self.node.how = how
        self.node.merge_conditions = merge_conditions
        self.node.suffix_left = suffix_left
        self.node.suffix_right = suffix_right
        self.accept()


class ConcatDialog(BaseConfigDialog):
    dialog_title = 'Concat Configuration'

    def _setupUi(self):
        self.axis_combo = _addComboInput(
            self._layout, 'Axis:',
            [('0 (stack rows)', '0'), ('1 (stack columns)', '1')],
            current_value=self.node.axis, default='0',
        )
        self.join_combo = _addComboInput(
            self._layout, 'Join:',
            [('inner (only shared columns)', 'inner'), ('outer (all columns)', 'outer')],
            current_value=self.node.join, default='outer',
        )
        self.ignore_index_checkbox = QCheckBox('Reset Index')
        self.ignore_index_checkbox.setChecked(bool(self.node.ignore_index))
        self._layout.addWidget(self.ignore_index_checkbox)
        self.keys_input = _addLineInput(
            self._layout, 'Keys (optional, label each source dataframe):', self.node.keys
        )

    def _onSave(self):
        self.node.axis = self.axis_combo.currentData()
        self.node.join = self.join_combo.currentData()
        self.node.ignore_index = self.ignore_index_checkbox.isChecked()
        keys = self.keys_input.text().strip()
        self.node.keys = keys if keys else None
        self.accept()


class LoadCSVDialog(BaseConfigDialog):
    dialog_title = 'Load CSV Configuration'

    def _setupUi(self):
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('File Path:'))
        self.file_path_input = QLineEdit()
        if self.node.file_path:
            self.file_path_input.setText(self.node.file_path)
        path_layout.addWidget(self.file_path_input)
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self._browseFile)
        path_layout.addWidget(browse_btn)
        self._layout.addLayout(path_layout)

    def _browseFile(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Select CSV File', '', 'CSV Files (*.csv)'
        )
        if file_path:
            self.file_path_input.setText(file_path)

    def _onSave(self):
        file_path = self.file_path_input.text().strip()
        if not file_path:
            self.status_label.setText('Error: File path is required')
            return

        self.node.file_path = file_path
        self.accept()


class LoadMultiCSVDialog(BaseConfigDialog):
    dialog_title = 'Load Multi CSV Configuration'
    extra_width = 200

    def _setupUi(self):
        self._layout.addWidget(QLabel('Selected CSV Files:'))

        self.file_list = QTableWidget(0, 1)
        self.file_list.setHorizontalHeaderLabels(['File Path'])
        header = self.file_list.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.file_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Files')
        add_btn.clicked.connect(self._browseFiles)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Selected')
        remove_btn.clicked.connect(self._removeSelected)
        btn_layout.addWidget(remove_btn)
        clear_btn = QPushButton('Clear All')
        clear_btn.clicked.connect(self._clearAll)
        btn_layout.addWidget(clear_btn)
        self._layout.addLayout(btn_layout)

        self.count_label = QLabel('')
        self._layout.addWidget(self.count_label)

        # Repopulate from saved file paths
        if self.node.file_paths:
            for fp in self.node.file_paths:
                row = self.file_list.rowCount()
                self.file_list.insertRow(row)
                item = QTableWidgetItem(fp)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.file_list.setItem(row, 0, item)
            self._updateCount()

    def _browseFiles(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 'Select CSV Files', '', 'CSV Files (*.csv)'
        )
        if file_paths:
            # Avoid duplicates
            existing = set()
            for r in range(self.file_list.rowCount()):
                item = self.file_list.item(r, 0)
                if item:
                    existing.add(item.text())
            for fp in file_paths:
                if fp not in existing:
                    row = self.file_list.rowCount()
                    self.file_list.insertRow(row)
                    item = QTableWidgetItem(fp)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.file_list.setItem(row, 0, item)
            self._updateCount()

    def _removeSelected(self):
        row = self.file_list.currentRow()
        if row >= 0:
            self.file_list.removeRow(row)
            self._updateCount()

    def _clearAll(self):
        self.file_list.setRowCount(0)
        self._updateCount()

    def _updateCount(self):
        count = self.file_list.rowCount()
        self.count_label.setText(f'{count} file(s) selected')

    def _onSave(self):
        row_count = self.file_list.rowCount()
        if row_count == 0:
            self.status_label.setText('Error: At least one CSV file is required')
            return

        file_paths = []
        for row in range(row_count):
            item = self.file_list.item(row, 0)
            fp = item.text().strip() if item else ''
            if not fp:
                self.status_label.setText(f'Error: Row {row + 1}: empty file path')
                return
            file_paths.append(fp)

        self.node.file_paths = file_paths
        self.accept()


class ExportCSVDialog(BaseConfigDialog):
    dialog_title = 'Export CSV Configuration'

    def _setupUi(self):
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel('File Path:'))
        self.file_path_input = QLineEdit()
        if self.node.file_path:
            self.file_path_input.setText(self.node.file_path)
        path_layout.addWidget(self.file_path_input)
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self._browseFile)
        path_layout.addWidget(browse_btn)
        self._layout.addLayout(path_layout)

    def _browseFile(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Save CSV File', '', 'CSV Files (*.csv)'
        )
        if file_path:
            self.file_path_input.setText(file_path)

    def _onSave(self):
        file_path = self.file_path_input.text().strip()
        if not file_path:
            self.status_label.setText('Error: File path is required')
            return

        if not file_path.lower().endswith('.csv'):
            file_path += '.csv'

        self.node.file_path = file_path
        self.accept()
