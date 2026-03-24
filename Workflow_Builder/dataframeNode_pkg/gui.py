"""
Node GUI registration - main entry point for dataframe node GUIs.
"""
from ryven.gui_env import *
from . import nodes
from .gui_utils import ConfigButtonWidget
from .dataframe_nodes.gui_dialogs import (
    ReplaceValueDialog,
    ComputeColumnDialog,
    SortByColumnDialog,
    RenameColumnDialog,
    ReorderColumnDialog,
    MergeDialog,
    ConcatDialog,
    LoadCSVDialog,
    LoadMultiCSVDialog,
    ExportCSVDialog,
)
from .calibration_nodes.gui_dialogs import (
    CalibPupilDilationDialog,
    CalibGroupbyStatsDialog,
    CalibThresholdFilterDialog,
    CalibRmssdDialog,
    CalibRelativeThresholdDialog,
)
from .physagg_nodes.gui_dialogs import (
    PhysStatsAggDialog,
    PhysRmssdAggDialog,
    PhysCumulativeAggDialog,
)


# ============================================================
# Node GUI Classes
# ============================================================

class ReplaceValueWidget(ConfigButtonWidget):
    dialog_class = ReplaceValueDialog

@node_gui(nodes.ReplaceValueNode)
class ReplaceValueGUI(NodeGUI):
    color = '#3498db'
    main_widget_class = ReplaceValueWidget


class ComputeColumnWidget(ConfigButtonWidget):
    dialog_class = ComputeColumnDialog

@node_gui(nodes.ComputeColumnNode)
class ComputeColumnGUI(NodeGUI):
    color = '#9b59b6'
    main_widget_class = ComputeColumnWidget


class SortByColumnWidget(ConfigButtonWidget):
    dialog_class = SortByColumnDialog


@node_gui(nodes.SortByColumnNode)
class SortByColumnGUI(NodeGUI):
    color = '#e74c3c'
    main_widget_class = SortByColumnWidget


class RenameColumnWidget(ConfigButtonWidget):
    dialog_class = RenameColumnDialog

@node_gui(nodes.RenameColumnNode)
class RenameColumnGUI(NodeGUI):
    color = '#1abc9c'
    main_widget_class = RenameColumnWidget


class ReorderColumnWidget(ConfigButtonWidget):
    dialog_class = ReorderColumnDialog

@node_gui(nodes.ReorderColumnNode)
class ReorderColumnGUI(NodeGUI):
    color = '#f39c12'
    main_widget_class = ReorderColumnWidget


class MergeWidget(ConfigButtonWidget):
    dialog_class = MergeDialog

@node_gui(nodes.MergeNode)
class MergeGUI(NodeGUI):
    color = '#e67e22'
    main_widget_class = MergeWidget


class ConcatWidget(ConfigButtonWidget):
    dialog_class = ConcatDialog

@node_gui(nodes.ConcatNode)
class ConcatGUI(NodeGUI):
    color = '#2ecc71'
    main_widget_class = ConcatWidget


class LoadCSVWidget(ConfigButtonWidget):
    dialog_class = LoadCSVDialog

@node_gui(nodes.LoadCSVNode)
class LoadCSVGUI(NodeGUI):
    color = '#34495e'
    main_widget_class = LoadCSVWidget


class LoadMultiCSVWidget(ConfigButtonWidget):
    dialog_class = LoadMultiCSVDialog

@node_gui(nodes.LoadMultiCSVNode)
class LoadMultiCSVGUI(NodeGUI):
    color = '#2c3e50'
    main_widget_class = LoadMultiCSVWidget


class ExportCSVWidget(ConfigButtonWidget):
    dialog_class = ExportCSVDialog

@node_gui(nodes.ExportCSVNode)
class ExportCSVGUI(NodeGUI):
    color = '#7d3c98'
    main_widget_class = ExportCSVWidget


class CalibPupilDilationWidget(ConfigButtonWidget):
    dialog_class = CalibPupilDilationDialog

@node_gui(nodes.CalibPupilDilationNode)
class CalibPupilDilationGUI(NodeGUI):
    color = '#8e44ad'
    main_widget_class = CalibPupilDilationWidget


class CalibGroupbyStatsWidget(ConfigButtonWidget):
    dialog_class = CalibGroupbyStatsDialog

@node_gui(nodes.CalibGroupbyStatsNode)
class CalibGroupbyStatsGUI(NodeGUI):
    color = '#16a085'
    main_widget_class = CalibGroupbyStatsWidget


class CalibThresholdFilterWidget(ConfigButtonWidget):
    dialog_class = CalibThresholdFilterDialog

@node_gui(nodes.CalibThresholdFilterNode)
class CalibThresholdFilterGUI(NodeGUI):
    color = '#c0392b'
    main_widget_class = CalibThresholdFilterWidget


class CalibRmssdWidget(ConfigButtonWidget):
    dialog_class = CalibRmssdDialog

@node_gui(nodes.CalibRmssdNode)
class CalibRmssdGUI(NodeGUI):
    color = '#2980b9'
    main_widget_class = CalibRmssdWidget


class CalibRelativeThresholdWidget(ConfigButtonWidget):
    dialog_class = CalibRelativeThresholdDialog

@node_gui(nodes.CalibRelativeThresholdNode)
class CalibRelativeThresholdGUI(NodeGUI):
    color = '#d35400'
    main_widget_class = CalibRelativeThresholdWidget


class PhysStatsAggWidget(ConfigButtonWidget):
    dialog_class = PhysStatsAggDialog

@node_gui(nodes.PhysStatsAggNode)
class PhysStatsAggGUI(NodeGUI):
    color = '#27ae60'
    main_widget_class = PhysStatsAggWidget


class PhysRmssdAggWidget(ConfigButtonWidget):
    dialog_class = PhysRmssdAggDialog

@node_gui(nodes.PhysRmssdAggNode)
class PhysRmssdAggGUI(NodeGUI):
    color = '#2471a3'
    main_widget_class = PhysRmssdAggWidget


class PhysCumulativeAggWidget(ConfigButtonWidget):
    dialog_class = PhysCumulativeAggDialog

@node_gui(nodes.PhysCumulativeAggNode)
class PhysCumulativeAggGUI(NodeGUI):
    color = '#1a5276'
    main_widget_class = PhysCumulativeAggWidget


class PrintWidget(ConfigButtonWidget):
    dialog_class = None

@node_gui(nodes.PrintNode)
class PrintGUI(NodeGUI):
    color = '#7f8c8d'
    main_widget_class = PrintWidget

