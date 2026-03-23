from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
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
)


class CalibPupilDilationDialog(BaseConfigDialog):
    dialog_title = 'Calibration: Pupil Dilation Configuration'

    def _setupUi(self):
        # Collapsible help note
        self.help_button = QPushButton('Show Help')
        self.help_button.setFlat(True)
        self.help_button.setStyleSheet('QPushButton { color: #3498db; text-decoration: underline; }')
        self.help_button.clicked.connect(self._toggleHelp)
        self._layout.addWidget(self.help_button)

        self.help_label = QLabel(
            'How this works: For each value in the category list, this node '
            'filters the Data DF to rows where the category column equals that '
            'value. It then uses the merge key column to look up the two '
            'specified value columns and maps them onto the Target DF as new '
            'columns (e.g. Calibration_PupilDilation_Left_128). The merge key '
            'column is used both to index the filtered data and to align rows '
            'with the Target DF.'
        )
        self.help_label.setWordWrap(True)
        self.help_label.setStyleSheet('QLabel { color: #666; font-style: italic; }')
        self.help_label.setVisible(False)
        self._layout.addWidget(self.help_label)

        self.merge_key_input = _addLineInput(
            self._layout, 'Merge Key Column:', self.node.merge_key_col,
        )
        self.shown_gray_input = _addLineInput(
            self._layout, 'Category Column:', self.node.shown_gray_col,
        )
        self.left_median_input = _addLineInput(
            self._layout, 'Left Value Column:', self.node.left_median_col,
        )
        self.right_median_input = _addLineInput(
            self._layout, 'Right Value Column:', self.node.right_median_col,
        )
        gray_text = ''
        if self.node.grayscale_values:
            gray_text = '\n'.join(str(v) for v in self.node.grayscale_values)
        self.grayscale_input = _addTextInput(
            self._layout,
            'Grayscale Values (one integer per line):',
            gray_text,
            '0\n16\n32\n48',
        )

    def _toggleHelp(self):
        visible = self.help_label.isVisible()
        self.help_label.setVisible(not visible)
        self.help_button.setText('Hide Help' if not visible else 'Show Help')

    def _onSave(self):
        merge_key = self.merge_key_input.text().strip()
        if not merge_key:
            self.status_label.setText('Error: Merge key column is required')
            return
        shown_gray = self.shown_gray_input.text().strip()
        if not shown_gray:
            self.status_label.setText('Error: Shown grayscale column is required')
            return
        left_median = self.left_median_input.text().strip()
        if not left_median:
            self.status_label.setText('Error: Left median column is required')
            return
        right_median = self.right_median_input.text().strip()
        if not right_median:
            self.status_label.setText('Error: Right median column is required')
            return

        # Parse grayscale values
        lines = _parseLines(self.grayscale_input.toPlainText())
        if not lines:
            self.status_label.setText('Error: At least one grayscale value is required')
            return
        values = []
        seen = set()
        for line in lines:
            try:
                v = int(line)
            except ValueError:
                self.status_label.setText(f'Error: Invalid integer: {line!r}')
                return
            if v not in seen:
                values.append(v)
                seen.add(v)
        if not values:
            self.status_label.setText('Error: At least one grayscale value is required')
            return

        self.node.merge_key_col = merge_key
        self.node.shown_gray_col = shown_gray
        self.node.left_median_col = left_median
        self.node.right_median_col = right_median
        self.node.grayscale_values = values
        self.accept()


_STAT_ORDER = ('median', 'mean', 'std')
_STAT_LABELS = {'median': 'Median', 'mean': 'Mean', 'std': 'Std'}
# Table columns: value_col, median_cb, median_out, mean_cb, mean_out, std_cb, std_out
_COL_VALUE = 0
_COL_MEDIAN_CB = 1
_COL_MEDIAN_OUT = 2
_COL_MEAN_CB = 3
_COL_MEAN_OUT = 4
_COL_STD_CB = 5
_COL_STD_OUT = 6
_TABLE2_COL_COUNT = 7


class CalibGroupbyStatsDialog(BaseConfigDialog):
    dialog_title = 'Calibration: Groupby Stats Configuration'
    extra_width = 1000

    def _setupUi(self):
        self.groupby_key_input = _addLineInput(
            self._layout, 'Groupby Key Column:', self.node.groupby_key,
        )
        hint = QLabel('(Leave output name blank to auto-generate on save)')
        hint.setWordWrap(True)
        self._layout.addWidget(hint)

        # Table
        self.table = QTableWidget(0, _TABLE2_COL_COUNT)
        self.table.setHorizontalHeaderLabels([
            'Data Column',
            'Median', 'Median Output',
            'Mean', 'Mean Output',
            'Std', 'Std Output',
        ])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        # Repopulate from saved metrics
        if self.node.metrics:
            for value_col, stats_tuple, out_cols_tuple in self.node.metrics:
                row = self.table.rowCount()
                self._addRow()
                # Set value_col
                self.table.item(row, _COL_VALUE).setText(value_col)
                # Build a mapping from stat name -> output col
                stat_out_map = dict(zip(stats_tuple, out_cols_tuple))
                for stat_name, cb_col, out_col in [
                    ('median', _COL_MEDIAN_CB, _COL_MEDIAN_OUT),
                    ('mean', _COL_MEAN_CB, _COL_MEAN_OUT),
                    ('std', _COL_STD_CB, _COL_STD_OUT),
                ]:
                    if stat_name in stat_out_map:
                        cb_widget = self.table.cellWidget(row, cb_col)
                        cb_widget.setChecked(True)
                        out_field = self.table.cellWidget(row, out_col)
                        out_field.setEnabled(True)
                        out_field.setText(stat_out_map[stat_name])
        else:
            self._addRow()

    def _addRow(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        # value_col
        self.table.setItem(row, _COL_VALUE, QTableWidgetItem(''))
        # For each stat: checkbox + output line edit
        for stat_name, cb_col, out_col in [
            ('median', _COL_MEDIAN_CB, _COL_MEDIAN_OUT),
            ('mean', _COL_MEAN_CB, _COL_MEAN_OUT),
            ('std', _COL_STD_CB, _COL_STD_OUT),
        ]:
            cb = QCheckBox()
            out_field = QLineEdit()
            out_field.setEnabled(False)
            out_field.setPlaceholderText('(auto)')
            cb.toggled.connect(self._makeCbToggled(cb, out_field, stat_name, cb_col))
            self.table.setCellWidget(row, cb_col, cb)
            self.table.setCellWidget(row, out_col, out_field)

    def _makeCbToggled(self, cb, out_field, stat_name, cb_col):
        """Return a slot that enables/disables the output field and auto-suggests."""
        def _onToggled(checked):
            out_field.setEnabled(checked)
            if checked and not out_field.text().strip():
                # Determine the current row for this checkbox (rows can be removed).
                row = -1
                for r in range(self.table.rowCount()):
                    if self.table.cellWidget(r, cb_col) is cb:
                        row = r
                        break
                if row < 0:
                    return

                value_col_item = self.table.item(row, _COL_VALUE)
                value_col = value_col_item.text().strip() if value_col_item else ''
                if value_col:
                    out_field.setText(
                        f'Calibration_{_STAT_LABELS[stat_name]}_{value_col}'
                    )
        return _onToggled

    def _removeRow(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def _onSave(self):
        key = self.groupby_key_input.text().strip()
        if not key:
            self.status_label.setText('Error: Groupby key is required')
            return

        row_count = self.table.rowCount()
        if row_count == 0:
            self.status_label.setText('Error: At least one metric row is required')
            return

        metrics = []
        all_output_names = []
        for row in range(row_count):
            value_col_item = self.table.item(row, _COL_VALUE)
            value_col = value_col_item.text().strip() if value_col_item else ''
            if not value_col:
                self.status_label.setText(f'Error: Row {row + 1}: value column is required')
                return

            stats = []
            out_cols = []
            for stat_name, cb_col, out_col in [
                ('median', _COL_MEDIAN_CB, _COL_MEDIAN_OUT),
                ('mean', _COL_MEAN_CB, _COL_MEAN_OUT),
                ('std', _COL_STD_CB, _COL_STD_OUT),
            ]:
                cb = self.table.cellWidget(row, cb_col)
                if cb and cb.isChecked():
                    out_field = self.table.cellWidget(row, out_col)
                    out_name = out_field.text().strip() if out_field else ''
                    if not out_name:
                        out_name = f'Calibration_{_STAT_LABELS[stat_name]}_{value_col}'
                        out_field.setText(out_name)
                    stats.append(stat_name)
                    out_cols.append(out_name)
                    all_output_names.append(out_name)

            if not stats:
                self.status_label.setText(
                    f'Error: Row {row + 1}: at least one stat must be selected'
                )
                return
            metrics.append((value_col, tuple(stats), tuple(out_cols)))

        # Check for duplicate output names
        if len(all_output_names) != len(set(all_output_names)):
            seen = set()
            for name in all_output_names:
                if name in seen:
                    self.status_label.setText(
                        f'Error: Duplicate output name: {name!r}'
                    )
                    return
                seen.add(name)

        self.node.groupby_key = key
        self.node.metrics = metrics
        self.accept()


# Node 3 table columns: column, op, value, connector
_COL3_COLUMN = 0
_COL3_OP = 1
_COL3_VALUE = 2
_COL3_CONNECTOR = 3
_TABLE3_COL_COUNT = 4
_OPS = ['>', '>=', '<', '<=', '==', '!=']


class CalibThresholdFilterDialog(BaseConfigDialog):
    dialog_title = 'Calibration: Threshold Filter Configuration'
    extra_width = 300

    def _setupUi(self):
        self.table = QTableWidget(0, _TABLE3_COL_COUNT)
        self.table.setHorizontalHeaderLabels(['Column', 'Op', 'Value', 'Connector'])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        # Repopulate from saved data
        if self.node.conditions:
            for i, (col, op, val) in enumerate(self.node.conditions):
                self._addRow()
                self.table.item(i, _COL3_COLUMN).setText(col)
                op_combo = self.table.cellWidget(i, _COL3_OP)
                idx = _OPS.index(op) if op in _OPS else 0
                op_combo.setCurrentIndex(idx)
                self.table.item(i, _COL3_VALUE).setText(str(val))
                if i < len(self.node.connectors):
                    conn_combo = self.table.cellWidget(i, _COL3_CONNECTOR)
                    conn_combo.setCurrentText(self.node.connectors[i])
        else:
            self._addRow()

    def _addRow(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Column name
        self.table.setItem(row, _COL3_COLUMN, QTableWidgetItem(''))

        # Op combo
        op_combo = QComboBox()
        op_combo.addItems(_OPS)
        self.table.setCellWidget(row, _COL3_OP, op_combo)

        # Value
        self.table.setItem(row, _COL3_VALUE, QTableWidgetItem(''))

        # Connector combo
        conn_combo = QComboBox()
        conn_combo.addItems(['AND', 'OR'])
        self.table.setCellWidget(row, _COL3_CONNECTOR, conn_combo)

        self._refreshConnectors()

    def _removeRow(self):
        row = self.table.currentRow()
        if row >= 0 and self.table.rowCount() > 0:
            self.table.removeRow(row)
            self._refreshConnectors()

    def _refreshConnectors(self):
        """Enable all connector combos except the last row's (which is disabled)."""
        count = self.table.rowCount()
        for r in range(count):
            combo = self.table.cellWidget(r, _COL3_CONNECTOR)
            if combo:
                combo.setEnabled(r < count - 1)

    def _onSave(self):
        row_count = self.table.rowCount()
        if row_count == 0:
            self.status_label.setText('Error: At least one condition is required')
            return

        conditions = []
        connectors = []
        for row in range(row_count):
            col_item = self.table.item(row, _COL3_COLUMN)
            col = col_item.text().strip() if col_item else ''
            if not col:
                self.status_label.setText(f'Error: Row {row + 1}: column is required')
                return

            val_item = self.table.item(row, _COL3_VALUE)
            val_text = val_item.text().strip() if val_item else ''
            try:
                val = float(val_text)
            except ValueError:
                self.status_label.setText(
                    f'Error: Row {row + 1}: value must be a number'
                )
                return

            op_combo = self.table.cellWidget(row, _COL3_OP)
            op = op_combo.currentText()

            conditions.append((col, op, val))

            if row < row_count - 1:
                conn_combo = self.table.cellWidget(row, _COL3_CONNECTOR)
                connectors.append(conn_combo.currentText())

        self.node.conditions = conditions
        self.node.connectors = connectors
        self.accept()


class CalibRmssdDialog(BaseConfigDialog):
    dialog_title = 'Calibration: Compute RMSSD Configuration'

    def _setupUi(self):
        self.groupby_key_input = _addLineInput(
            self._layout, 'Groupby / Merge Key Column:', self.node.groupby_key,
            'Participant_ID',
        )
        hint = QLabel('(This column is also used to merge the result back onto the Target DF)')
        hint.setWordWrap(True)
        self._layout.addWidget(hint)

        self.data_column_input = _addLineInput(
            self._layout, 'RR Interval Column:', self.node.data_column,
            'Polar_HeartRate_RR_Interval',
        )
        self.output_column_input = _addLineInput(
            self._layout, 'Output Column Name:', self.node.output_column_name,
            'Calibration_RR_Interval_RAW_RMSSD',
        )

    def _onSave(self):
        groupby_key = self.groupby_key_input.text().strip()
        if not groupby_key:
            self.status_label.setText('Error: Groupby / merge key column is required')
            return

        data_column = self.data_column_input.text().strip()
        if not data_column:
            self.status_label.setText('Error: RR interval column is required')
            return

        output_column_name = self.output_column_input.text().strip()
        if not output_column_name:
            self.status_label.setText('Error: Output column name is required')
            return

        self.node.groupby_key = groupby_key
        self.node.data_column = data_column
        self.node.output_column_name = output_column_name
        self.accept()


class CalibRelativeThresholdDialog(BaseConfigDialog):
    dialog_title = 'Calibration: Relative Threshold Filter Configuration'

    def _setupUi(self):
        self.groupby_column_input = _addLineInput(
            self._layout, 'Groupby Column:', self.node.groupby_column,
            'Participant_ID',
        )
        self.age_column_input = _addLineInput(
            self._layout, 'Age Column:', self.node.age_column,
            'Participant_Age',
        )
        self.rr_interval_column_input = _addLineInput(
            self._layout, 'RR Interval Column:', self.node.rr_interval_column,
            'Polar_HeartRate_RR_Interval',
        )

        self._layout.addWidget(QLabel('Max Iterations:'))
        self.max_iterations_input = QSpinBox()
        self.max_iterations_input.setRange(1, 1000)
        self.max_iterations_input.setValue(
            self.node.max_iterations if isinstance(self.node.max_iterations, int) else 20
        )
        self._layout.addWidget(self.max_iterations_input)

    def _onSave(self):
        groupby_column = self.groupby_column_input.text().strip()
        if not groupby_column:
            self.status_label.setText('Error: Groupby column is required')
            return

        age_column = self.age_column_input.text().strip()
        if not age_column:
            self.status_label.setText('Error: Age column is required')
            return

        rr_interval_column = self.rr_interval_column_input.text().strip()
        if not rr_interval_column:
            self.status_label.setText('Error: RR interval column is required')
            return

        self.node.groupby_column = groupby_column
        self.node.age_column = age_column
        self.node.rr_interval_column = rr_interval_column
        self.node.max_iterations = self.max_iterations_input.value()
        self.accept()
