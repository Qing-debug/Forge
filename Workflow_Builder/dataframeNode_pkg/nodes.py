"""Ryven dataframe nodes (configuration-only, pull-based execution).

The nodes in ``dataframeNode_pkg`` are configuration-only: they store UI-entered
configuration on the node instance and, when executed, perform their
transformation.

Execution model: There are NO exec ports. Each node has a "Run" button in the
GUI that calls node.update() with inp=-1. When a node runs, it calls
self.input(i) which, in exec mode, triggers a lazy backward pull - if the
upstream node hasn't been updated yet, ryvencore calls its update_event(inp=-1)
first, recursively pulling the whole upstream chain.

Caching: Each node has a ``_has_run`` instance flag. Once ``update_event``
completes, the flag is set to ``True`` and subsequent pulls return instantly.
To force a node to recompute, the user clicks the "Reset Cache" button on that
node's GUI widget, which sets ``_has_run`` back to ``False``.  A status
indicator on each node shows whether it will recompute (``_has_run = False``)
or return cached results (``_has_run = True``) when next pulled.

Node classes are organized into three subpackages:
- ``dataframe_nodes/``   - general pandas transformations (load, merge, sort, etc.)
- ``calibration_nodes/`` - calibration pipeline (threshold filter, RMSSD, pupil dilation, etc.)
- ``physagg_nodes/``     - physiological aggregation (stats, RMSSD, cumulative, etc.)

This module defines the shared base classes and re-exports all node classes
so that Ryven's ``export_nodes()`` can register them from a single location.
"""

from typing import Callable, override
from ryven.node_env import *
import pandas as pd


# ============================================================
# Shared Base Classes
# ============================================================

class myDataFrame(Data):
    @override
    @property
    def payload(self):
        return self._payload.copy()


class DataFrameNodeBase(Node):
    """Base class for all dataframe nodes.

    Provides ``_has_run`` caching so that each node computes at most once per
    run.  Users reset individual nodes via the "Reset Cache" button in the GUI,
    which sets ``_has_run`` back to ``False``.
    """

    def __init__(self, params):
        super().__init__(params)
        self._has_run: bool = False
        self._on_has_run_changed: Callable[[], None] | None = None  # GUI callback, set by ConfigButtonWidget

    def update_event(self, inp=-1):

        if self._has_run:
            return

        try:
            self._doUpdate()
        except Exception as e:
            print(f"An Exception was thrown:{e}. The root cause is the topmost exception (it differs from all the other exception messages shown). Fix the node responsible for the topmost exception.")
            raise
        self._has_run = True
        if self._on_has_run_changed:
            self._on_has_run_changed()

    def isConfigured(self) -> bool:
        """Return True if this node has all required configuration.

        Subclasses override with their specific checks.  The GUI indicator
        and the pre-run validation both call this - single source of truth.
        """
        return False

    def _doUpdate(self):
        """Override in subclasses to perform the actual work."""
        pass


# ============================================================
# GUI Loading (deferred until Ryven GUI initializes)
# ============================================================

@on_gui_load
def load_gui():
    from . import gui


# ============================================================
# Re-export all node classes from subpackages
# ============================================================

from .dataframe_nodes import (
    ReplaceValueNode,
    ComputeColumnNode,
    SortByColumnNode,
    RenameColumnNode,
    ReorderColumnNode,
    MergeNode,
    ConcatNode,
    LoadCSVNode,
    LoadMultiCSVNode,
    PrintNode,
)

from .calibration_nodes import (
    CalibPupilDilationNode,
    CalibGroupbyStatsNode,
    CalibThresholdFilterNode,
    CalibRmssdNode,
    CalibRelativeThresholdNode,
)

from .physagg_nodes import (
    PhysStatsAggNode,
    PhysRmssdAggNode,
    PhysCumulativeAggNode,
)


# ============================================================
# Register all nodes with Ryven
# ============================================================

export_nodes([
    ReplaceValueNode,
    ComputeColumnNode,
    SortByColumnNode,
    RenameColumnNode,
    ReorderColumnNode,
    MergeNode,
    ConcatNode,
    LoadCSVNode,
    LoadMultiCSVNode,
    # PrintNode,  # Removed from UI - use the Preview button and Output section to inspect data
    CalibPupilDilationNode,
    CalibGroupbyStatsNode,
    CalibThresholdFilterNode,
    CalibRmssdNode,
    CalibRelativeThresholdNode,
    PhysStatsAggNode,
    PhysRmssdAggNode,
    PhysCumulativeAggNode,
])
