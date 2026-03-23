UI_library = 'pyside6'

import os
os.environ['QT_API'] = UI_library #need to do this so qtpy knows to act as a wrapper round pyqt6 when we import our node files
import ryven
from ryvencore.Flow import Flow, FlowAlg, executor_from_flow_alg

# Monkey-patch Flow.__init__ so every new flow defaults to exec-flow instead
# of Ryven's built-in default (data-flow).  Our pull-based node design requires
# exec-flow; removing this patch simply restores the application default to
# data-flow, which can still be switched manually via the Ryven GUI.
_original_flow_init = Flow.__init__

def _patched_flow_init(self, session, title: str):
    _original_flow_init(self, session, title)
    self.alg_mode = FlowAlg.EXEC
    self.executor = executor_from_flow_alg(FlowAlg.EXEC)(self)

Flow.__init__ = _patched_flow_init

ryven.run_ryven(qt_api = UI_library, performance_mode = 'fast')
