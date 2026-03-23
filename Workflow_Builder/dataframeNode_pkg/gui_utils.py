"""
GUI utility functions, validation helpers, and base widget classes.
"""
from ryven.gui_env import *
from . import nodes

from qtpy.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from qtpy.QtCore import Qt

OK_CANCEL = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel


# ============================================================
# Validation Helpers
# ============================================================

def _isNonEmpty(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) > 0
    return True


def _listComplete(items):
    return bool(items) and all(_isNonEmpty(item) for item in items)


def _mappingsComplete(mappings):
    if not mappings:
        return False
    for mapping in mappings:
        if not isinstance(mapping, dict):
            return False
        if not _isNonEmpty(mapping.get('old')):
            return False
        if not _isNonEmpty(mapping.get('new')):
            return False
    return True


def _fieldComplete(node, field):
    value = getattr(node, field, None)
    if field in ('mappings', 'rename_mappings'):
        return _mappingsComplete(value)
    if field in ('sort_columns', 'columns_to_move'):
        return _listComplete(value)
    return _isNonEmpty(value)


def isNodeConfigured(node):
    """Backward-compatible wrapper - delegates to ``node.isConfigured()``."""
    return node.isConfigured()


def getInputPortData(node, port_index):
    """Read cached data from an input port without triggering execution.

    Returns:
        (status, df) where status is 'data', 'no_data', or 'not_connected'
    """
    inp = node.inputs[port_index]
    out = node.flow.connected_output(inp)
    if out is None:
        return ('not_connected', None)
    if out.val is None:
        return ('no_data', None)
    return ('data', out.val.payload)


def getOutputPortData(node, port_index):
    """Read cached data from an output port.

    Returns:
        (status, df) where status is 'data' or 'no_data'
    """
    out = node.outputs[port_index]
    if out.val is None:
        return ('no_data', None)
    return ('data', out.val.payload)


def collectUpstreamChain(node, visited=None):
    """Return all nodes feeding into *node*, including *node* itself.

    Walks backward through input connections recursively.
    Returns a deduplicated list in bottom-up order (node itself first).
    Cycle-safe via visited set.
    """
    if visited is None:
        visited = set()
    if id(node) in visited:
        return []
    visited.add(id(node))
    result = [node]
    for inp in node.inputs:
        out = node.flow.connected_output(inp)
        if out is not None:
            result.extend(collectUpstreamChain(out.node, visited))
    return result


def collectDownstreamChain(node, visited=None):
    """Return all nodes downstream of *node*, including *node* itself.

    Walks forward through output connections recursively.
    Returns a deduplicated list in top-down order (node itself first).
    Cycle-safe via visited set.

    Uses node.flow.graph_adj[out_port] -> List[NodeInput], each with .node.
    """
    if visited is None:
        visited = set()
    if id(node) in visited:
        return []
    visited.add(id(node))
    result = [node]
    for out_port in node.outputs:
        for inp_port in node.flow.graph_adj.get(out_port, []):
            result.extend(collectDownstreamChain(inp_port.node, visited))
    return result


# ============================================================
# Configuration Summary (Rendered on Node)
# ============================================================

NODE_CONFIG_FIELDS = {
    nodes.ReplaceValueNode: ('mode', 'column_header', 'replacement_type', 'mappings'),
    nodes.ComputeColumnNode: ('new_column', 'formula'),
    nodes.SortByColumnNode: ('sort_columns', 'ascending_list', 'ignore_index'),
    nodes.RenameColumnNode: ('rename_mappings',),
    nodes.ReorderColumnNode: ('anchor_column', 'columns_to_move'),
    nodes.MergeNode: ('how', 'merge_conditions', 'suffix_left', 'suffix_right'),
    nodes.ConcatNode: ('axis', 'join', 'ignore_index', 'keys'),
    nodes.LoadCSVNode: ('file_path',),
    nodes.LoadMultiCSVNode: ('file_paths',),
    nodes.CalibPupilDilationNode: (
        'merge_key_col', 'shown_gray_col', 'left_median_col',
        'right_median_col', 'grayscale_values',
    ),
    nodes.CalibGroupbyStatsNode: ('groupby_key', 'metrics'),
    nodes.CalibThresholdFilterNode: ('conditions', 'connectors'),
    nodes.CalibRmssdNode: ('groupby_key', 'data_column', 'output_column_name'),
    nodes.CalibRelativeThresholdNode: (
        'groupby_column', 'age_column', 'rr_interval_column', 'max_iterations',
    ),
    nodes.PrintNode: (),
    nodes.PhysStatsAggNode: (
        'aggregation_name', 'groupby_key_mappings', 'extra_filters',
        'window_mode', 'column_configs', 'stats_to_compute',
    ),
    nodes.PhysRmssdAggNode: (
        'aggregation_name', 'groupby_key_mappings', 'extra_filters',
        'window_mode', 'rr_column', 'lower_bound', 'upper_bound', 'output_label',
    ),
    nodes.PhysCumulativeAggNode: (
        'aggregation_name', 'groupby_key_mappings', 'extra_filters',
        'window_mode', 'column_configs',
    ),
}


def nodeConfigSummaryText(node):
    lines = [f"configured = {isNodeConfigured(node)!r}"]

    for cls, fields in NODE_CONFIG_FIELDS.items():
        if isinstance(node, cls):
            for field in fields:
                lines.append(f"{field} = {getattr(node, field, None)!r}")
            break
    else:
        lines.append(f"state = {getattr(node, '__dict__', {})!r}")

    return '\n'.join(lines)


# ============================================================
# UI Builder Helpers
# ============================================================

def _addLineInput(layout, label, value=None, placeholder=None):
    layout.addWidget(QLabel(label))
    field = QLineEdit()
    if value:
        field.setText(value)
    if placeholder:
        field.setPlaceholderText(placeholder)
    layout.addWidget(field)
    return field


def _addTextInput(layout, label, value=None, placeholder=None):
    layout.addWidget(QLabel(label))
    field = QTextEdit()
    if value:
        field.setText(value)
    if placeholder:
        field.setPlaceholderText(placeholder)
    layout.addWidget(field)
    return field


def _addComboInput(layout, label, items, current_value=None, default=None):
    """Add a QLabel + non-editable QComboBox to *layout* and return the combo.

    *items* can be:
    - A list of strings: each string is used as both display text and data.
    - A list of (display_text, raw_value) tuples: display_text is shown,
      raw_value is stored as item data.

    Use ``combo.currentData()`` to retrieve the raw value on save.
    Use ``combo.findData(value)`` to select by raw value on load.
    """
    layout.addWidget(QLabel(label))
    combo = QComboBox()
    combo.setEditable(False)
    for item in items:
        if isinstance(item, tuple):
            display, data = item
            combo.addItem(display, data)
        else:
            combo.addItem(item, item)
    # Select current_value if provided, otherwise use default
    value = current_value if current_value is not None else default
    if value is not None:
        idx = combo.findData(value)
        if idx >= 0:
            combo.setCurrentIndex(idx)
    layout.addWidget(combo)
    return combo


def _parseLines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def _mappingsToText(mappings):
    return '\n'.join(f"{m.get('old', '')}={m.get('new', '')}" for m in mappings)


def _parseMappings(text):
    lines = _parseLines(text)
    if not lines:
        return None, 'Error: At least one mapping is required'
    mappings = []
    for line in lines:
        if '=' not in line:
            return None, 'Error: Each mapping must be in old=new format'
        old, new = line.split('=', 1)
        old = old.strip()
        new = new.strip()
        if not old or not new:
            return None, 'Error: Mapping values cannot be empty'
        mappings.append({'old': old, 'new': new})
    return mappings, None


def _parseBoolList(text):
    values = _parseLines(text)
    if not values:
        return [], None
    bools = []
    for value in values:
        lowered = value.lower()
        if lowered not in ('true', 'false'):
            return None, 'Error: Ascending values must be true/false'
        bools.append(lowered == 'true')
    return bools, None


# ============================================================
# Operational Dialogs (used by ConfigButtonWidget)
# ============================================================

def _nodeLabel(node):
    """Return a display label like 'Sort by Column (#7)'."""
    return f'{node.title} (#{node.global_id})'


class PreRunValidationDialog(QDialog):
    """Shows unconfigured nodes before execution. Blocks until dismissed."""

    def __init__(self, unconfigured_nodes):
        super().__init__()
        self.setWindowTitle('Pre-Run Validation')
        self.setModal(True)
        layout = QVBoxLayout(self)

        header = QLabel('Cannot run - the following nodes are not configured:')
        header.setStyleSheet('font-weight: bold; color: #e74c3c;')
        header.setWordWrap(True)
        layout.addWidget(header)
        for node in unconfigured_nodes:
            layout.addWidget(QLabel(f'  • {_nodeLabel(node)}'))

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.reject)
        layout.addWidget(buttons)


# ============================================================
# Base Widget Classes
# ============================================================

class BaseConfigDialog(QDialog):
    dialog_title = ''
    extra_width = 0

    def __init__(self, node):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.node = node
        self.setWindowTitle(self.dialog_title)
        self.setModal(True)
        self._layout = QVBoxLayout(self)
        self.status_label = QLabel('')
        self.status_label.setWordWrap(True)
        self._error_widgets = set()
        self._setupUi()
        self._finishUi()

        # Dialogs are built dynamically; some dialogs are intentionally widened.
        extra_width = int(getattr(self, 'extra_width', 0) or 0)
        if extra_width:
            self.adjustSize()
            w = self.width()
            h = self.height()
            self.resize(w + extra_width, h)

    def _finishUi(self):
        self._layout.addWidget(self.status_label)
        buttons = QDialogButtonBox(OK_CANCEL)
        buttons.accepted.connect(self._onSave)
        buttons.rejected.connect(self.reject)
        self._layout.addWidget(buttons)

    def _onSave(self):
        raise NotImplementedError

    def _setupUi(self):
        raise NotImplementedError

    def _clearErrorStyles(self):
        """Remove red-border error highlighting from all previously marked widgets."""
        for widget in self._error_widgets:
            widget.setStyleSheet('')
        self._error_widgets.clear()
        self.status_label.setText('')

    def _setErrorStyle(self, widget):
        """Apply red-border error highlighting to a widget."""
        widget.setStyleSheet('border: 2px solid red;')
        self._error_widgets.add(widget)


class ConfigButtonWidget(NodeMainWidget, QWidget):
    button_text = 'Configure'
    dialog_class = None

    def __init__(self, params):
        QWidget.__init__(self)
        NodeMainWidget.__init__(self, params)
        self.setMaximumWidth(320)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)

        # -- Node ID label (top of widget) --
        self.id_label = QLabel(f'#{self.node.global_id}')
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.id_label.setStyleSheet('QLabel { color: #888; font-size: 10px; }')
        self._layout.addWidget(self.id_label)

        # -- Cache status indicator --
        self.cache_indicator = QLabel()
        self.cache_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.cache_indicator)

        # -- Config status indicator --
        self.config_indicator = QLabel()
        self.config_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.config_indicator)

        self.button = QPushButton(self.button_text)
        self.button.clicked.connect(self._openDialog)
        self._layout.addWidget(self.button)

        self.run_button = QPushButton('▶ Run')
        self.run_button.setStyleSheet(
            'QPushButton { background-color: #27ae60; color: white; font-weight: bold; }'
            'QPushButton:hover { background-color: #2ecc71; }'
            'QPushButton:pressed { background-color: #1e8449; }'
        )
        self.run_button.clicked.connect(self._runNode)
        self._layout.addWidget(self.run_button)

        self.reset_cache_button = QPushButton('↻ Reset Cache')
        self.reset_cache_button.setStyleSheet(
            'QPushButton { background-color: #e67e22; color: white; font-weight: bold; }'
            'QPushButton:hover { background-color: #f39c12; }'
            'QPushButton:pressed { background-color: #d35400; }'
        )
        self.reset_cache_button.clicked.connect(self._resetCache)
        self._layout.addWidget(self.reset_cache_button)

        self.preview_input_button = QPushButton('👁 Preview')
        self.preview_input_button.setStyleSheet(
            'QPushButton { background-color: #3498db; color: white; font-weight: bold; }'
            'QPushButton:hover { background-color: #5dade2; }'
            'QPushButton:pressed { background-color: #2c81ba; }'
        )
        self.preview_input_button.clicked.connect(self._previewInput)
        self._layout.addWidget(self.preview_input_button)

        self.status_button = QPushButton('Show Config')
        self.status_button.clicked.connect(self._toggleStatus)
        self._layout.addWidget(self.status_button)

        self.status_label = QLabel('')
        self.status_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.status_label.setTextFormat(Qt.TextFormat.PlainText)
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        self.status_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._layout.addWidget(self.status_label)

        self._syncing_label_size = False
        self._syncing_widget_size = False
        self._updateStatusLabel()
        self._updateCacheIndicator()
        self._updateConfigIndicator()

        # Register callback so the indicator updates when upstream pulls set _has_run
        self.node._on_has_run_changed = self._updateCacheIndicator

    def _openDialog(self):
        if self.dialog_class is None:
            return
        dialog = self.dialog_class(self.node)
        if dialog.exec_() == dialog.DialogCode.Accepted:
            self._resetNodeAndDownstream()
        self._updateStatusLabel()
        self._updateConfigIndicator()
        if self.status_label.isVisible():
            self.update_node_shape()

    def _runNode(self):
        """Manually trigger this node's update_event(inp=-1).

        Validates the upstream chain first:
        - Blocks if any node is not configured.
        """
        chain = collectUpstreamChain(self.node)
        unconfigured = [n for n in chain if not n.isConfigured()]

        if unconfigured:
            dialog = PreRunValidationDialog(unconfigured)
            dialog.exec_()
            return

        self.node.update()
        self._updateCacheIndicator()

    def _previewInput(self):
        self._preview_dialog = PreviewDialog(self.node)
        self._preview_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._preview_dialog.show()

    def _resetNodeAndDownstream(self):
        """Reset cache for this node and all downstream dependents."""
        for n in collectDownstreamChain(self.node):
            n._has_run = False
            for out in n.outputs:
                out.val = None
            cb = getattr(n, '_on_has_run_changed', None)
            if cb is not None:
                cb()

    def _resetCache(self):
        """Reset this node's cache and all downstream dependents."""
        self._resetNodeAndDownstream()

    def _updateCacheIndicator(self):
        """Update the visual indicator showing the node's cache state."""
        if self.node._has_run:
            self.cache_indicator.setText('● Cached')
            self.cache_indicator.setToolTip(
                'This node has computed its output. Reset to recompute.'
            )
            self.cache_indicator.setStyleSheet(
                'QLabel { color: #27ae60; font-weight: bold; }'
            )
        else:
            self.cache_indicator.setText('○ Will Recompute')
            self.cache_indicator.setToolTip(
                'This node will recompute on next run. '
                'Downstream nodes are also marked for recomputation.'
            )
            self.cache_indicator.setStyleSheet(
                'QLabel { color: #e67e22; font-weight: bold; }'
            )

    def _updateConfigIndicator(self):
        """Update the visual indicator showing whether the node is fully configured."""
        if self.node.isConfigured():
            self.config_indicator.setText('✓ Configured')
            self.config_indicator.setStyleSheet(
                'QLabel { color: #27ae60; font-weight: bold; }'
            )
        else:
            self.config_indicator.setText('✗ Not Configured')
            self.config_indicator.setStyleSheet(
                'QLabel { color: #e74c3c; font-weight: bold; }'
            )

    def _toggleStatus(self):
        is_visible = self.status_label.isVisible()
        self.status_label.setVisible(not is_visible)
        self.status_button.setText('Hide Config' if not is_visible else 'Show Config')
        self._updateStatusLabel()
        if not self.status_label.isVisible():
            self.status_label.setFixedHeight(0)
            self.status_label.setFixedWidth(0)
        self._syncWidgetSize()

    def _updateStatusLabel(self):
        summary = nodeConfigSummaryText(self.node)
        self.button.setToolTip(summary)
        self.status_button.setToolTip(summary)

        # Only do the expensive hard-wrap when label is visible
        if not self.status_label.isVisible():
            self.status_label.setText(summary)
            return

        # Compute the available pixel width for the text area
        available_width = min(300, max(120, self.width() - 8))
        margins = self.status_label.contentsMargins()
        text_width = available_width - margins.left() - margins.right()

        # Hard-wrap every line so no text exceeds the available width.
        wrapped = self._hardWrap(summary, text_width)
        self.status_label.setText(wrapped)
        self._syncStatusSize()
        self._syncWidgetSize()

    def _hardWrap(self, text, max_pixel_width):
        """Break *text* into lines that each fit within *max_pixel_width* px.

        Splits on existing newlines first, then force-breaks any line
        that is still wider than the budget character-by-character so
        nothing ever overflows horizontally.
        """
        # Safety: if width is too small, just return original text
        if max_pixel_width < 20:
            return text

        try:
            fm = self.status_label.fontMetrics()
            # Get the text width function (horizontalAdvance in Qt5.11+, width in older)
            get_width = getattr(fm, 'horizontalAdvance', None) or fm.width
        except Exception:
            return text

        result_lines = []
        for line in text.split('\n'):
            if get_width(line) <= max_pixel_width:
                result_lines.append(line)
                continue
            # Force-break this long line
            current = ''
            for ch in line:
                test = current + ch
                if get_width(test) > max_pixel_width and current:
                    result_lines.append(current)
                    current = ch
                else:
                    current = test
            if current:
                result_lines.append(current)
        return '\n'.join(result_lines)

    def _syncStatusSize(self):
        if not self.status_label.isVisible():
            return
        if self._syncing_label_size:
            return
        self._syncing_label_size = True

        try:
            available_width = min(300, max(120, self.width() - 8))
            self.status_label.setFixedWidth(available_width)

            # Height = line_height × number_of_lines + margins
            fm = self.status_label.fontMetrics()
            margins = self.status_label.contentsMargins()
            line_count = self.status_label.text().count('\n') + 1
            text_height = fm.lineSpacing() * line_count + margins.top() + margins.bottom()
            self.status_label.setFixedHeight(text_height)
        except Exception:
            pass
        finally:
            self._syncing_label_size = False

    def _syncWidgetSize(self):
        if self._syncing_widget_size:
            return
        self._syncing_widget_size = True
        try:
            self._layout.invalidate()
            self._layout.activate()
            self.updateGeometry()
            self.adjustSize()
            self.resize(self.sizeHint())
            self.update_node_shape()
        finally:
            self._syncing_widget_size = False


# ============================================================
# Preview Dialog
# ============================================================

class PreviewDialog(QDialog):
    """Read-only dialog showing DataFrames on input and output ports."""

    MAX_PREVIEW_ROWS = 50

    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        self.setWindowTitle(f'Data Preview - {node.__class__.__name__}')
        self.resize(1100, 700)

        layout = QVBoxLayout(self)

        # Top-level tabs: Input / Output
        self.main_tabs = QTabWidget()
        layout.addWidget(self.main_tabs)

        self.main_tabs.addTab(self._buildInputTab(node), 'Input')
        self.main_tabs.addTab(self._buildOutputTab(node), 'Output')

        close_btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        close_btn.rejected.connect(self.reject)
        layout.addWidget(close_btn)

    def _buildInputTab(self, node):
        """Build the Input tab content."""
        num_inputs = len(node.inputs)
        if num_inputs == 0:
            return self._centeredLabel('This node has no input ports.')

        if num_inputs > 1:
            tabs = QTabWidget()
            for i in range(num_inputs):
                label = getattr(node.inputs[i], 'label_str', '') or f'Input {i}'
                status, df = getInputPortData(node, i)
                tabs.addTab(self._buildDataTab(status, df), label)
            return tabs

        # Single input - no sub-tabs
        status, df = getInputPortData(node, 0)
        return self._buildDataTab(status, df)

    def _buildOutputTab(self, node):
        """Build the Output tab content."""
        num_outputs = len(node.outputs)
        if num_outputs == 0:
            return self._centeredLabel('This node has no output ports.')

        if num_outputs > 1:
            tabs = QTabWidget()
            for i in range(num_outputs):
                label = getattr(node.outputs[i], 'label_str', '') or f'Output {i}'
                status, df = getOutputPortData(node, i)
                if status == 'no_data' and not node._has_run:
                    tabs.addTab(
                        self._centeredLabel('No output - run this node first'),
                        label,
                    )
                else:
                    tabs.addTab(self._buildDataTab(status, df), label)
            return tabs

        # Single output - no sub-tabs
        status, df = getOutputPortData(node, 0)
        if status == 'no_data' and not node._has_run:
            return self._centeredLabel('No output - run this node first')
        return self._buildDataTab(status, df)

    def _buildDataTab(self, status, df):
        """Build a widget showing a data table + summary, or a status message."""
        if status == 'not_connected':
            return self._centeredLabel('Port not connected')
        if status == 'no_data':
            return self._centeredLabel('No data available - run upstream nodes first')

        # status == 'data'
        container = QWidget()
        vbox = QVBoxLayout(container)

        # Data table
        preview = df.head(self.MAX_PREVIEW_ROWS)
        rows, cols = preview.shape
        table = QTableWidget(rows, cols)
        table.setHorizontalHeaderLabels([str(c) for c in preview.columns])
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

        for r in range(rows):
            for c in range(cols):
                val = preview.iloc[r, c]
                table.setItem(r, c, QTableWidgetItem(str(val)))

        table.resizeColumnsToContents()
        padding = 20
        for c in range(cols):
            table.setColumnWidth(c, table.columnWidth(c) + padding)

        data_label = QLabel(f'Data Preview (first {rows} of {df.shape[0]} rows)')
        data_label.setStyleSheet('QLabel { font-weight: bold; font-size: 12px; }')
        vbox.addWidget(data_label)
        vbox.addWidget(table)

        # Summary panel
        total_rows, total_cols = df.shape
        meta_label = QLabel(f'Column Info ({total_cols} columns, {total_rows} rows total)')
        meta_label.setStyleSheet('QLabel { font-weight: bold; font-size: 12px; margin-top: 8px; }')
        vbox.addWidget(meta_label)

        summary_table = QTableWidget(total_cols, 3)
        summary_table.setHorizontalHeaderLabels(['Column', 'Dtype', 'Nulls'])
        summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        summary_table.verticalHeader().setVisible(False)
        for i, col_name in enumerate(df.columns):
            dtype = str(df[col_name].dtype)
            nulls = str(int(df[col_name].isna().sum()))
            summary_table.setItem(i, 0, QTableWidgetItem(str(col_name)))
            summary_table.setItem(i, 1, QTableWidgetItem(dtype))
            summary_table.setItem(i, 2, QTableWidgetItem(nulls))
        summary_header = summary_table.horizontalHeader()
        summary_header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        summary_header.setStretchLastSection(True)
        summary_table.resizeColumnsToContents()
        for c in range(3):
            summary_table.setColumnWidth(c, summary_table.columnWidth(c) + padding)
        summary_table.setMaximumHeight(min(total_cols * 30 + 30, 200))
        vbox.addWidget(summary_table)

        return container

    @staticmethod
    def _centeredLabel(text):
        """Return a QLabel centered both horizontally and vertically."""
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet('QLabel { color: #888; font-size: 13px; }')
        return label
