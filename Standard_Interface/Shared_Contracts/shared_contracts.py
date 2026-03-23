from enum import Enum
import numpy as np
'''
idea was for this to be used as a SST for both datapresenter and dataview in determining the available types that a user can select when replacing all existing unique values
in a column, but it's only used in dataview right now, we dont use this for any data checking in datapresenter
'''


# maps chosen types but doesn't consider potential subtypes (types within the appropriate type that are more appropriate in terms of the underlying memory space it occupies) when looking at numpy types
def to_numpy_dtype(value_to_change_type_of: int | bool | str, replacement_type: str) -> np.int64 | np.float64 | np.bool_ | np.str_ | None:
    new_value = None
    match replacement_type:
        case ReplacementValueTypes.STRING.value:
            new_value = np.str_(value_to_change_type_of)

        case ReplacementValueTypes.INTEGER.value:
            new_value = np.int64(value_to_change_type_of)

        case ReplacementValueTypes.FLOAT.value:
            new_value = np.float64(value_to_change_type_of)

    return new_value


class ReplacementValueTypes(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"