"""
Structures package initialization.
Exports individual structure modules, descriptors, and dispatcher.
"""

from types import SimpleNamespace
from . import structure_1
from . import structure_2
from . import structure_3
from . import structure_4
from . import structure_custom

PostStructure = SimpleNamespace

# Structure descriptors for UI display
STRUCTURE_1 = SimpleNamespace(
    id=structure_1.STRUCTURE_ID,
    name=structure_1.STRUCTURE_NAME,
    image_folder_name=structure_1.IMAGE_FOLDER_NAME,
    description=structure_1.DESCRIPTION
)

STRUCTURE_2 = SimpleNamespace(
    id=structure_2.STRUCTURE_ID,
    name=structure_2.STRUCTURE_NAME,
    image_folder_name=structure_2.IMAGE_FOLDER_NAME,
    description=structure_2.DESCRIPTION
)

STRUCTURE_3 = SimpleNamespace(
    id=structure_3.STRUCTURE_ID,
    name=structure_3.STRUCTURE_NAME,
    image_folder_name=structure_3.IMAGE_FOLDER_NAME,
    description=structure_3.DESCRIPTION
)

STRUCTURE_4 = SimpleNamespace(
    id=structure_4.STRUCTURE_ID,
    name=structure_4.STRUCTURE_NAME,
    image_folder_name=structure_4.IMAGE_FOLDER_NAME,
    description=structure_4.DESCRIPTION
)

STRUCTURE_CUSTOM = SimpleNamespace(
    id=structure_custom.STRUCTURE_ID,
    name=structure_custom.STRUCTURE_NAME,
    image_folder_name=structure_custom.IMAGE_FOLDER_NAME,
    description=structure_custom.DESCRIPTION
)

STRUCTURE_MODULES = {
    "str-1": structure_1,
    "str-2": structure_2,
    "str-3": structure_3,
    "str-4": structure_4,
    "str-custom": structure_custom
}

def get_structure_module(struct_id: str):
    """Returns the dedicated structure module by its ID."""
    return STRUCTURE_MODULES.get(struct_id, structure_1)

def get_structure_module_by_index(index: int):
    """Returns structure module for 1-based index (1 to 4)."""
    key = f"str-{index}"
    return STRUCTURE_MODULES.get(key, structure_1)

get_structure_by_id = get_structure_module
