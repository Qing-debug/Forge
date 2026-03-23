from qtpy.QtCore import Qt
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
)

HINT_STYLE = 'QLabel { color: #888; font-size: 11px; margin-bottom: 2px; }'
SECTION_STYLE = 'QLabel { font-weight: bold; margin-top: 6px; }'
REQUIRED_TAG = ' <span style="color: #c00;">(required)</span>'
OPTIONAL_TAG = ' <span style="color: #888;">(optional)</span>'


def _addHint(layout, text):
    """Add a small hint label below the current widget."""
    hint = QLabel(text)
    hint.setStyleSheet(HINT_STYLE)
    hint.setWordWrap(True)
    layout.addWidget(hint)


def _addSectionHeader(layout, title, required=True):
    """Add a bold section header with a required/optional tag."""
    tag = REQUIRED_TAG if required else OPTIONAL_TAG
    label = QLabel(f'{title}{tag}')
    label.setStyleSheet(SECTION_STYLE)
    label.setTextFormat(Qt.TextFormat.RichText)
    layout.addWidget(label)


def _addDescription(layout, text):
    """Add a node description block at the top of the dialog."""
    desc = QLabel(text)
    desc.setWordWrap(True)
    desc.setStyleSheet(
        'QLabel { background: #f0f4ff; border: 1px solid #ccd; '
        'border-radius: 4px; padding: 8px; margin-bottom: 6px; font-size: 12px; }'
    )
    layout.addWidget(desc)



# ============================================================
# Shared helper functions for physiological aggregation dialogs
# ============================================================

def _buildGroupbyTable(layout, saved_mappings=None):
    """Build a 2-column Groupby Key Mappings table with Add/Remove buttons."""
    _addSectionHeader(layout, 'Groupby Key Mappings')
    _addHint(layout,
        'Maps each target row to exposure rows. '
        'E.g. Target: "Participant_ID" / Exposure: "Participant_ID". '
        'Multiple rows create a compound key.'
    )
    table = QTableWidget(0, 2)
    table.setHorizontalHeaderLabels(['Target Column', 'Exposure Column'])
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    btn_layout = QHBoxLayout()
    add_btn = QPushButton('Add Row')
    remove_btn = QPushButton('Remove Row')
    btn_layout.addWidget(add_btn)
    btn_layout.addWidget(remove_btn)
    layout.addLayout(btn_layout)

    def _add():
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(''))
        table.setItem(row, 1, QTableWidgetItem(''))

    def _remove():
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    add_btn.clicked.connect(_add)
    remove_btn.clicked.connect(_remove)

    if saved_mappings:
        for m in saved_mappings:
            row = table.rowCount()
            _add()
            if isinstance(m, (list, tuple)) and len(m) == 2:
                table.item(row, 0).setText(str(m[0]))
                table.item(row, 1).setText(str(m[1]))
    else:
        _add()

    return table


def _buildExtraFiltersTable(layout, saved_filters=None):
    """Build a 2-column Extra Filters table with Add/Remove buttons."""
    _addSectionHeader(layout, 'Extra Filters', required=False)
    _addHint(layout,
        'Narrow the exposure data before aggregation. '
        'Only rows where the exposure column exactly equals the value are kept. '
        'Leave empty if no filtering is needed.'
    )
    table = QTableWidget(0, 2)
    table.setHorizontalHeaderLabels(['Exposure Column', 'Value'])
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    layout.addWidget(table)

    btn_layout = QHBoxLayout()
    add_btn = QPushButton('Add Row')
    remove_btn = QPushButton('Remove Row')
    btn_layout.addWidget(add_btn)
    btn_layout.addWidget(remove_btn)
    layout.addLayout(btn_layout)

    def _add():
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(''))
        table.setItem(row, 1, QTableWidgetItem(''))

    def _remove():
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)

    add_btn.clicked.connect(_add)
    remove_btn.clicked.connect(_remove)

    if saved_filters:
        for f in saved_filters:
            row = table.rowCount()
            _add()
            if isinstance(f, (list, tuple)) and len(f) == 2:
                table.item(row, 0).setText(str(f[0]))
                table.item(row, 1).setText(str(f[1]))

    return table


def _buildWindowModeSection(layout, node):
    """Build Window Mode combo and conditional 'Before Start' fields.

    Returns (combo, before_start_group, time_window_spin, timestamp_col_input,
             target_match_input, exposure_match_input).
    """
    _addSectionHeader(layout, 'Window Mode', required=False)
    _addHint(layout,
        '"Full Window" uses all matching exposure rows. '
        '"Before Start" uses only rows within a time window before the target event, '
        'useful for baseline measurements.'
    )
    current_mode = getattr(node, 'window_mode', 'full') or 'full'
    combo = _addComboInput(
        layout, 'Window Mode:',
        [('Full Window', 'full'), ('Before Start', 'before_start')],
        current_value=current_mode, default='full',
    )

    # "Before Start" group
    group = QWidget()
    g_layout = QVBoxLayout(group)
    g_layout.setContentsMargins(0, 0, 0, 0)

    g_layout.addWidget(QLabel('Time Window (seconds):'))
    time_spin = QSpinBox()
    time_spin.setRange(1, 999999)
    saved_tw = getattr(node, 'time_window', 60)
    time_spin.setValue(saved_tw if isinstance(saved_tw, int) else 60)
    g_layout.addWidget(time_spin)

    ts_col = _addLineInput(
        g_layout, 'Timestamp Column:',
        getattr(node, 'timestamp_column', None), 'Unity_Timestamp',
    )
    target_match = _addLineInput(
        g_layout, 'Target Match Column:',
        getattr(node, 'target_match_column', None),
    )
    exposure_match = _addLineInput(
        g_layout, 'Exposure Match Column:',
        getattr(node, 'exposure_match_column', None),
    )

    layout.addWidget(group)

    def _toggle(index):
        group.setVisible(combo.currentData() == 'before_start')

    combo.currentIndexChanged.connect(_toggle)
    group.setVisible(current_mode == 'before_start')

    return combo, group, time_spin, ts_col, target_match, exposure_match


def _readGroupbyTable(table):
    """Read groupby key mappings from a QTableWidget. Returns list of tuples."""
    mappings = []
    for row in range(table.rowCount()):
        target = (table.item(row, 0).text().strip() if table.item(row, 0) else '')
        exposure = (table.item(row, 1).text().strip() if table.item(row, 1) else '')
        if target and exposure:
            mappings.append((target, exposure))
    return mappings


def _readExtraFiltersTable(table):
    """Read extra filters from a QTableWidget. Returns list of tuples."""
    filters = []
    for row in range(table.rowCount()):
        col = (table.item(row, 0).text().strip() if table.item(row, 0) else '')
        val = (table.item(row, 1).text().strip() if table.item(row, 1) else '')
        if col and val:
            filters.append((col, val))
    return filters


def _saveWindowModeFields(node, combo, time_spin, ts_col, target_match, exposure_match):
    """Save window-mode related fields onto the node."""
    node.window_mode = combo.currentData()
    if node.window_mode == 'before_start':
        node.time_window = time_spin.value()
        node.timestamp_column = ts_col.text().strip()
        node.target_match_column = target_match.text().strip()
        node.exposure_match_column = exposure_match.text().strip()
    else:
        node.time_window = 60
        node.timestamp_column = 'Unity_Timestamp'
        node.target_match_column = None
        node.exposure_match_column = None


def _parseOptionalFloat(text, field_name):
    """Parse a string as an optional float. Returns (value, error_msg).

    Empty string -> (None, None). Non-numeric -> (None, error_msg).
    """
    text = text.strip()
    if not text:
        return None, None
    try:
        return float(text), None
    except ValueError:
        return None, f'{field_name} must be numeric'


# ---- PhysStatsAggDialog ----

class PhysStatsAggDialog(BaseConfigDialog):
    dialog_title = 'Physiological Stats Aggregation Configuration'
    extra_width = 800

    def _setupUi(self):
        _addDescription(self._layout,
            'Computes descriptive statistics (median, mean, std, min, max) for one or more '
            'columns from the Exposure DF and writes the results into the Target DF.\n\n'
            'For each target row, the node finds matching exposure rows (via groupby keys '
            'and optional filters), then computes the selected stats on each configured column.\n\n'
            'Output columns are named: {Aggregation Name}_{Stat}_{Output Label}'
        )

        # Aggregation name
        _addSectionHeader(self._layout, 'Aggregation Name')
        _addHint(self._layout,
            'Prefix for all output column names. '
            'E.g. "Exposure_Full_Time_Window" produces columns like '
            '"Exposure_Full_Time_Window_Median_EDA".'
        )
        self.agg_name_input = _addLineInput(
            self._layout, 'Aggregation Name:',
            getattr(self.node, 'aggregation_name', None),
        )

        # Shared aggregation tables
        self.groupby_table = _buildGroupbyTable(
            self._layout,
            getattr(self.node, 'groupby_key_mappings', None),
        )
        self.filters_table = _buildExtraFiltersTable(
            self._layout,
            getattr(self.node, 'extra_filters', None),
        )
        (
            self.window_combo, self._bs_group,
            self.time_spin, self.ts_col_input,
            self.target_match_input, self.exposure_match_input,
        ) = _buildWindowModeSection(self._layout, self.node)

        # Column Configs table (5 columns)
        _addSectionHeader(self._layout, 'Column Configs')
        _addHint(self._layout,
            'Each row defines a column to aggregate from the Exposure DF.\n'
            '- Source Column: the exposure column name to read values from (required)\n'
            '- Output Label: suffix for the output column name (required)\n'
            '- Lower/Upper Bound: exclude values outside this range (optional)\n'
            '- Filter Value: exclude rows with this exact value (optional)'
        )
        self.col_table = QTableWidget(0, 5)
        self.col_table.setHorizontalHeaderLabels([
            'Source Column', 'Output Label', 'Lower Bound', 'Upper Bound', 'Filter Value',
        ])
        header = self.col_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.col_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addColRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeColRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        # Populate column configs from saved state
        saved_configs = getattr(self.node, 'column_configs', None)
        if saved_configs:
            for cfg in saved_configs:
                row = self.col_table.rowCount()
                self._addColRow()
                self.col_table.item(row, 0).setText(cfg.get('source_column', ''))
                self.col_table.item(row, 1).setText(cfg.get('output_label', ''))
                lb = cfg.get('lower_bound')
                self.col_table.item(row, 2).setText(str(lb) if lb is not None else '')
                ub = cfg.get('upper_bound')
                self.col_table.item(row, 3).setText(str(ub) if ub is not None else '')
                fv = cfg.get('filter_value')
                self.col_table.item(row, 4).setText(str(fv) if fv is not None else '')
        else:
            self._addColRow()

        # Stats checkboxes
        _addSectionHeader(self._layout, 'Stats to Compute')
        _addHint(self._layout, 'Select at least one statistic to compute for each column.')
        stats_row = QHBoxLayout()
        saved_stats = getattr(self.node, 'stats_to_compute', None) or []
        all_checked = not saved_stats  # default all checked when nothing saved
        self.stat_checkboxes = {}  # Maps data_key -> QCheckBox
        for display_name, data_key in [('Median', 'median'), ('Mean', 'mean'), ('SD', 'std'), ('Min', 'min'), ('Max', 'max')]:
            cb = QCheckBox(display_name)
            if all_checked or data_key in saved_stats:
                cb.setChecked(True)
            stats_row.addWidget(cb)
            self.stat_checkboxes[data_key] = cb
        self._layout.addLayout(stats_row)

    def _addColRow(self):
        row = self.col_table.rowCount()
        self.col_table.insertRow(row)
        for c in range(5):
            self.col_table.setItem(row, c, QTableWidgetItem(''))

    def _removeColRow(self):
        row = self.col_table.currentRow()
        if row >= 0:
            self.col_table.removeRow(row)

    def _onSave(self):
        self._clearErrorStyles()

        agg_name = self.agg_name_input.text().strip()
        if not agg_name:
            self._setErrorStyle(self.agg_name_input)
            self.status_label.setText('Error: Aggregation name is required')
            return

        groupby_mappings = _readGroupbyTable(self.groupby_table)
        if not groupby_mappings:
            self.status_label.setText('Error: At least 1 groupby key mapping is required')
            return

        # Validate column configs
        col_configs = []
        for row in range(self.col_table.rowCount()):
            src = (self.col_table.item(row, 0).text().strip()
                   if self.col_table.item(row, 0) else '')
            label = (self.col_table.item(row, 1).text().strip()
                     if self.col_table.item(row, 1) else '')
            lb_text = (self.col_table.item(row, 2).text().strip()
                       if self.col_table.item(row, 2) else '')
            ub_text = (self.col_table.item(row, 3).text().strip()
                       if self.col_table.item(row, 3) else '')
            fv_text = (self.col_table.item(row, 4).text().strip()
                       if self.col_table.item(row, 4) else '')

            if not src and not label:
                continue  # skip empty rows

            if not src:
                self.col_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: source column is required')
                return
            if not label:
                self.col_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: output label is required')
                return

            lb, err = _parseOptionalFloat(lb_text, f'Row {row + 1} lower bound')
            if err:
                self.col_table.selectRow(row)
                self.status_label.setText(f'Error: {err}')
                return
            ub, err = _parseOptionalFloat(ub_text, f'Row {row + 1} upper bound')
            if err:
                self.col_table.selectRow(row)
                self.status_label.setText(f'Error: {err}')
                return
            fv, err = _parseOptionalFloat(fv_text, f'Row {row + 1} filter value')
            if err:
                self.col_table.selectRow(row)
                self.status_label.setText(f'Error: {err}')
                return

            col_configs.append({
                'source_column': src,
                'output_label': label,
                'lower_bound': lb,
                'upper_bound': ub,
                'filter_value': fv,
            })

        if not col_configs:
            self.status_label.setText('Error: At least 1 column config is required')
            return

        # Stats
        selected_stats = [
            name for name, cb in self.stat_checkboxes.items() if cb.isChecked()
        ]
        if not selected_stats:
            self.status_label.setText('Error: At least 1 stat must be checked')
            return

        # Save
        self.node.aggregation_name = agg_name
        self.node.groupby_key_mappings = groupby_mappings
        self.node.extra_filters = _readExtraFiltersTable(self.filters_table)
        _saveWindowModeFields(
            self.node, self.window_combo, self.time_spin,
            self.ts_col_input, self.target_match_input, self.exposure_match_input,
        )
        self.node.column_configs = col_configs
        self.node.stats_to_compute = selected_stats
        self.accept()


# ---- PhysRmssdAggDialog ----

class PhysRmssdAggDialog(BaseConfigDialog):
    dialog_title = 'Physiological RMSSD Aggregation Configuration'
    extra_width = 600

    def _setupUi(self):
        _addDescription(self._layout,
            'Computes RMSSD (Root Mean Square of Successive Differences) from RR interval '
            'data in the Exposure DF and writes the result into the Target DF.\n\n'
            'RMSSD is a standard heart rate variability (HRV) metric. '
            'Formula: sqrt(mean(diff(rr_intervals)^2))\n\n'
            'RR intervals outside the bounds are excluded before computation '
            '(typical physiologically valid range: 200-2000 ms).\n\n'
            'Output column is named: {Aggregation Name}_{Output Label}'
        )

        # Aggregation name
        _addSectionHeader(self._layout, 'Aggregation Name')
        _addHint(self._layout,
            'Prefix for the output column name. '
            'E.g. "Exposure_Full_Time_Window" produces '
            '"Exposure_Full_Time_Window_RR_RMSSD".'
        )
        self.agg_name_input = _addLineInput(
            self._layout, 'Aggregation Name:',
            getattr(self.node, 'aggregation_name', None),
        )

        # Shared aggregation tables
        self.groupby_table = _buildGroupbyTable(
            self._layout,
            getattr(self.node, 'groupby_key_mappings', None),
        )
        self.filters_table = _buildExtraFiltersTable(
            self._layout,
            getattr(self.node, 'extra_filters', None),
        )
        (
            self.window_combo, self._bs_group,
            self.time_spin, self.ts_col_input,
            self.target_match_input, self.exposure_match_input,
        ) = _buildWindowModeSection(self._layout, self.node)

        # RMSSD-specific fields
        _addSectionHeader(self._layout, 'RR Interval Settings')
        _addHint(self._layout,
            'Column containing RR interval values (in ms) from the Exposure DF.'
        )
        self.rr_col_input = _addLineInput(
            self._layout, 'RR Interval Column:',
            getattr(self.node, 'rr_column', None), 'Polar_RR_Interval',
        )
        _addSectionHeader(self._layout, 'Validity Bounds', required=False)
        _addHint(self._layout,
            'RR intervals outside these bounds are excluded before computing RMSSD. '
            'Defaults: 200-2000 ms. Leave empty to use defaults.'
        )
        saved_lb = getattr(self.node, 'lower_bound', 200)
        saved_ub = getattr(self.node, 'upper_bound', 2000)
        self.lower_bound_input = _addLineInput(
            self._layout, 'Lower Bound (ms):',
            str(saved_lb) if saved_lb is not None else '200', '200',
        )
        self.upper_bound_input = _addLineInput(
            self._layout, 'Upper Bound (ms):',
            str(saved_ub) if saved_ub is not None else '2000', '2000',
        )
        _addSectionHeader(self._layout, 'Output Label')
        _addHint(self._layout,
            'Suffix for the output column. Combined with Aggregation Name to form the full column name.'
        )
        self.output_label_input = _addLineInput(
            self._layout, 'Output Label:',
            getattr(self.node, 'output_label', None) or 'RR_RMSSD', 'RR_RMSSD',
        )

    def _onSave(self):
        self._clearErrorStyles()

        agg_name = self.agg_name_input.text().strip()
        if not agg_name:
            self._setErrorStyle(self.agg_name_input)
            self.status_label.setText('Error: Aggregation name is required')
            return

        groupby_mappings = _readGroupbyTable(self.groupby_table)
        if not groupby_mappings:
            self.status_label.setText('Error: At least 1 groupby key mapping is required')
            return

        rr_col = self.rr_col_input.text().strip()
        if not rr_col:
            self._setErrorStyle(self.rr_col_input)
            self.status_label.setText('Error: RR interval column is required')
            return

        lb_text = self.lower_bound_input.text().strip()
        lb, err = _parseOptionalFloat(lb_text, 'Lower bound')
        if lb_text and err:
            self._setErrorStyle(self.lower_bound_input)
            self.status_label.setText(f'Error: {err}')
            return

        ub_text = self.upper_bound_input.text().strip()
        ub, err = _parseOptionalFloat(ub_text, 'Upper bound')
        if ub_text and err:
            self._setErrorStyle(self.upper_bound_input)
            self.status_label.setText(f'Error: {err}')
            return

        output_label = self.output_label_input.text().strip()
        if not output_label:
            self._setErrorStyle(self.output_label_input)
            self.status_label.setText('Error: Output label is required')
            return

        # Save
        self.node.aggregation_name = agg_name
        self.node.groupby_key_mappings = groupby_mappings
        self.node.extra_filters = _readExtraFiltersTable(self.filters_table)
        _saveWindowModeFields(
            self.node, self.window_combo, self.time_spin,
            self.ts_col_input, self.target_match_input, self.exposure_match_input,
        )
        self.node.rr_column = rr_col
        self.node.lower_bound = lb if lb is not None else 200
        self.node.upper_bound = ub if ub is not None else 2000
        self.node.output_label = output_label
        self.accept()


# ---- PhysCumulativeAggDialog ----

class PhysCumulativeAggDialog(BaseConfigDialog):
    dialog_title = 'Physiological Cumulative Aggregation Configuration'
    extra_width = 700

    def _setupUi(self):
        _addDescription(self._layout,
            'Computes the cumulative sum of positive successive differences for one or more '
            'columns from the Exposure DF and writes the results into the Target DF.\n\n'
            'For each target row, the node finds matching exposure rows, computes successive '
            'differences, keeps only positive changes (increases), and sums them. '
            'Useful for measures like cumulative EDA (electrodermal activity).\n\n'
            'Output columns are named: {Aggregation Name}_{Output Label}'
        )

        # Aggregation name
        _addSectionHeader(self._layout, 'Aggregation Name')
        _addHint(self._layout,
            'Prefix for all output column names. '
            'E.g. "Exposure_Full_Time_Window" produces columns like '
            '"Exposure_Full_Time_Window_Cumulative_EDA".'
        )
        self.agg_name_input = _addLineInput(
            self._layout, 'Aggregation Name:',
            getattr(self.node, 'aggregation_name', None),
        )

        # Shared aggregation tables
        self.groupby_table = _buildGroupbyTable(
            self._layout,
            getattr(self.node, 'groupby_key_mappings', None),
        )
        self.filters_table = _buildExtraFiltersTable(
            self._layout,
            getattr(self.node, 'extra_filters', None),
        )
        (
            self.window_combo, self._bs_group,
            self.time_spin, self.ts_col_input,
            self.target_match_input, self.exposure_match_input,
        ) = _buildWindowModeSection(self._layout, self.node)

        # Column Configs table (3 columns with checkbox)
        _addSectionHeader(self._layout, 'Column Configs')
        _addHint(self._layout,
            'Each row defines a column to aggregate from the Exposure DF.\n'
            '- Source Column: the exposure column name to read values from (required)\n'
            '- Output Label: suffix for the output column name (required)\n'
            '- Use Abs: if checked, use absolute value of differences (counts both increases and decreases)'
        )
        self.col_table = QTableWidget(0, 3)
        self.col_table.setHorizontalHeaderLabels([
            'Source Column', 'Output Label', 'Use Abs',
        ])
        header = self.col_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._layout.addWidget(self.col_table)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton('Add Row')
        add_btn.clicked.connect(self._addColRow)
        btn_layout.addWidget(add_btn)
        remove_btn = QPushButton('Remove Row')
        remove_btn.clicked.connect(self._removeColRow)
        btn_layout.addWidget(remove_btn)
        self._layout.addLayout(btn_layout)

        # Populate column configs from saved state
        saved_configs = getattr(self.node, 'column_configs', None)
        if saved_configs:
            for cfg in saved_configs:
                row = self.col_table.rowCount()
                self._addColRow()
                self.col_table.item(row, 0).setText(cfg.get('source_column', ''))
                self.col_table.item(row, 1).setText(cfg.get('output_label', ''))
                cb = self.col_table.cellWidget(row, 2)
                if cb and cfg.get('use_abs', False):
                    cb.setChecked(True)
        else:
            self._addColRow()

    def _addColRow(self):
        row = self.col_table.rowCount()
        self.col_table.insertRow(row)
        self.col_table.setItem(row, 0, QTableWidgetItem(''))
        self.col_table.setItem(row, 1, QTableWidgetItem(''))
        cb = QCheckBox()
        self.col_table.setCellWidget(row, 2, cb)

    def _removeColRow(self):
        row = self.col_table.currentRow()
        if row >= 0:
            self.col_table.removeRow(row)

    def _onSave(self):
        self._clearErrorStyles()

        agg_name = self.agg_name_input.text().strip()
        if not agg_name:
            self._setErrorStyle(self.agg_name_input)
            self.status_label.setText('Error: Aggregation name is required')
            return

        groupby_mappings = _readGroupbyTable(self.groupby_table)
        if not groupby_mappings:
            self.status_label.setText('Error: At least 1 groupby key mapping is required')
            return

        # Validate column configs
        col_configs = []
        for row in range(self.col_table.rowCount()):
            src = (self.col_table.item(row, 0).text().strip()
                   if self.col_table.item(row, 0) else '')
            label = (self.col_table.item(row, 1).text().strip()
                     if self.col_table.item(row, 1) else '')
            cb = self.col_table.cellWidget(row, 2)
            use_abs = cb.isChecked() if cb else False

            if not src and not label:
                continue  # skip empty rows

            if not src:
                self.col_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: source column is required')
                return
            if not label:
                self.col_table.selectRow(row)
                self.status_label.setText(
                    f'Error: Row {row + 1}: output label is required')
                return

            col_configs.append({
                'source_column': src,
                'output_label': label,
                'use_abs': use_abs,
            })

        if not col_configs:
            self.status_label.setText('Error: At least 1 column config is required')
            return

        # Save
        self.node.aggregation_name = agg_name
        self.node.groupby_key_mappings = groupby_mappings
        self.node.extra_filters = _readExtraFiltersTable(self.filters_table)
        _saveWindowModeFields(
            self.node, self.window_combo, self.time_spin,
            self.ts_col_input, self.target_match_input, self.exposure_match_input,
        )
        self.node.column_configs = col_configs
        self.accept()
