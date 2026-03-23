"""
Standalone dtype conversion utilities.

No imports from within this package - safe to import from both nodes.py and
gui_utils.py without causing circular imports.
"""
from enum import Enum
import numpy as np


class ReplacementValueTypes(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"


def toNumpyDtype(
    value_to_change_type_of: int | bool | str,
    replacement_type: str,
) -> "np.int64 | np.float64 | np.bool_ | np.str_ | None":
    new_value = None
    match replacement_type:
        case ReplacementValueTypes.STRING.value:
            new_value = np.str_(value_to_change_type_of)
        case ReplacementValueTypes.INTEGER.value:
            new_value = np.int64(value_to_change_type_of)
        case ReplacementValueTypes.FLOAT.value:
            new_value = np.float64(value_to_change_type_of)
    return new_value

