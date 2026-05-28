#    "Commons Clause" License Condition v1.0
#   #
#    The Software is provided to you by the Licensor under the License, as defined
#    below, subject to the following condition.
#
#    Without limiting other conditions in the License, the grant of rights under the
#    License will not include, and the License does not grant to you, the right to
#    Sell the Software.
#
#    For purposes of the foregoing, "Sell" means practicing any or all of the rights
#    granted to you under the License to provide to third parties, for a fee or other
#    consideration (including without limitation fees for hosting) a product or service whose value
#    derives, entirely or substantially, from the functionality of the Software. Any
#    license notice or attribution required by the License must also include this
#    Commons Clause License Condition notice.
#
#   Add-ons and extensions developed for this software may be distributed
#   under their own separate licenses.
#
#    Software: Revolution EDA
#    License: Mozilla Public License 2.0
#    Licensor: Revolution Semiconductor (Registered in the Netherlands)
#

"""
Schema validation for Revolution EDA JSON design files.

Provides JSON Schema definitions and validation utilities for symbol,
schematic, and layout files. Validates files on load to provide clear
error messages instead of cryptic exceptions.
"""

import logging
from typing import Any, List, Optional, Tuple

import jsonschema
from jsonschema import ValidationError, SchemaError

logger = logging.getLogger(__name__)

# Current schema version for future migration support
SCHEMA_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Common schema fragments
# ---------------------------------------------------------------------------

_POINT_SCHEMA = {
    "type": "array",
    "items": {"type": "number"},
    "minItems": 2,
    "maxItems": 2,
}

_FLIP_TUPLE_SCHEMA = {
    "type": "array",
    "items": {"type": ["number", "integer"]},
    "minItems": 2,
    "maxItems": 2,
}

_RECT_COORDS_SCHEMA = {
    "type": "array",
    "items": {"type": "number"},
    "minItems": 4,
    "maxItems": 4,
}

# ---------------------------------------------------------------------------
# Symbol item schemas
# ---------------------------------------------------------------------------

_SYMBOL_RECT_ITEM = {
    "type": "object",
    "required": ["type", "rect", "loc"],
    "properties": {
        "type": {"const": "rect"},
        "rect": _RECT_COORDS_SCHEMA,
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SYMBOL_LINE_ITEM = {
    "type": "object",
    "required": ["type", "st", "end", "loc"],
    "properties": {
        "type": {"const": "line"},
        "st": _POINT_SCHEMA,
        "end": _POINT_SCHEMA,
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SYMBOL_CIRCLE_ITEM = {
    "type": "object",
    "required": ["type", "cen", "end", "loc"],
    "properties": {
        "type": {"const": "circle"},
        "cen": _POINT_SCHEMA,
        "end": _POINT_SCHEMA,
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SYMBOL_ARC_ITEM = {
    "type": "object",
    "required": ["type", "st", "end", "loc", "at"],
    "properties": {
        "type": {"const": "arc"},
        "st": _POINT_SCHEMA,
        "end": _POINT_SCHEMA,
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
        "at": {"type": "integer", "minimum": 0},
    },
}

_SYMBOL_POLYGON_ITEM = {
    "type": "object",
    "required": ["type", "ps"],
    "properties": {
        "type": {"const": "polygon"},
        "ps": {"type": "array", "items": _POINT_SCHEMA, "minItems": 2},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SYMBOL_PIN_ITEM = {
    "type": "object",
    "required": ["type", "st", "nam", "pd", "pt", "loc", "ang"],
    "properties": {
        "type": {"const": "pin"},
        "st": _POINT_SCHEMA,
        "nam": {"type": "string"},
        "pd": {"type": "string"},
        "pt": {"type": "string"},
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SYMBOL_TEXT_ITEM = {
    "type": "object",
    "required": ["type", "st", "tc", "ff", "fs", "th", "ta", "to", "loc"],
    "properties": {
        "type": {"const": "text"},
        "st": _POINT_SCHEMA,
        "tc": {"type": "string"},
        "ff": {"type": "string"},
        "fs": {"type": "string"},
        "th": {"type": ["number", "integer"]},
        "ta": {"type": "string"},
        "to": {"type": "string"},
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SYMBOL_LABEL_ITEM = {
    "type": "object",
    "required": ["type", "st", "nam", "def", "txt", "val", "vis",
                 "lt", "ht", "al", "or", "use", "loc"],
    "properties": {
        "type": {"const": "label"},
        "st": _POINT_SCHEMA,
        "nam": {"type": "string"},
        "def": {"type": "string"},
        "txt": {"type": "string"},
        "val": {"type": "string"},
        "vis": {"type": "boolean"},
        "lt": {"type": "string"},
        "ht": {"type": ["number", "integer"]},
        "al": {"type": "string"},
        "or": {"type": "string"},
        "use": {"type": "string"},
        "loc": _POINT_SCHEMA,
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SYMBOL_ATTR_ITEM = {
    "type": "object",
    "required": ["type", "nam", "def"],
    "properties": {
        "type": {"const": "attr"},
        "nam": {"type": "string"},
        "def": {"type": "string"},
    },
}

_SYMBOL_ITEM_SCHEMA = {
    "oneOf": [
        _SYMBOL_RECT_ITEM,
        _SYMBOL_LINE_ITEM,
        _SYMBOL_CIRCLE_ITEM,
        _SYMBOL_ARC_ITEM,
        _SYMBOL_POLYGON_ITEM,
        _SYMBOL_PIN_ITEM,
        _SYMBOL_TEXT_ITEM,
        _SYMBOL_LABEL_ITEM,
        _SYMBOL_ATTR_ITEM,
    ]
}

# ---------------------------------------------------------------------------
# Schematic item schemas
# ---------------------------------------------------------------------------

_SCHEMATIC_SYMBOL_ITEM = {
    "type": "object",
    "required": ["type", "lib", "cell", "view", "nam", "ic", "ld", "loc"],
    "properties": {
        "type": {"const": "sys"},
        "lib": {"type": "string"},
        "cell": {"type": "string"},
        "view": {"type": "string"},
        "nam": {"type": "string"},
        "ic": {"type": "integer"},
        "ld": {"type": "object"},
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "ign": {"type": "integer"},
        "br": _RECT_COORDS_SCHEMA,
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SCHEMATIC_NET_ITEM = {
    "type": "object",
    "required": ["type", "st", "end", "nam", "ns"],
    "properties": {
        "type": {"const": "scn"},
        "st": _POINT_SCHEMA,
        "end": _POINT_SCHEMA,
        "nam": {"type": "string"},
        "ns": {"type": "integer"},
    },
}

_SCHEMATIC_PIN_ITEM = {
    "type": "object",
    "required": ["type", "st", "pn", "pd", "pt"],
    "properties": {
        "type": {"const": "scp"},
        "st": _POINT_SCHEMA,
        "pn": {"type": "string"},
        "pd": {"type": "string"},
        "pt": {"type": "string"},
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SCHEMATIC_TEXT_ITEM = {
    "type": "object",
    "required": ["type", "st", "tc", "ff", "fs", "th", "ta", "to"],
    "properties": {
        "type": {"const": "txt"},
        "st": _POINT_SCHEMA,
        "tc": {"type": "string"},
        "ff": {"type": "string"},
        "fs": {"type": "string"},
        "th": {"type": ["number", "integer"]},
        "ta": {"type": "string"},
        "to": {"type": "string"},
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_SCHEMATIC_ITEM_SCHEMA = {
    "oneOf": [
        _SCHEMATIC_SYMBOL_ITEM,
        _SCHEMATIC_NET_ITEM,
        _SCHEMATIC_PIN_ITEM,
        _SCHEMATIC_TEXT_ITEM,
    ]
}

# ---------------------------------------------------------------------------
# Layout item schemas
# ---------------------------------------------------------------------------

_LAYOUT_INSTANCE_ITEM = {
    "type": "object",
    "required": ["type", "lib", "cell", "view", "loc"],
    "properties": {
        "type": {"const": "Inst"},
        "lib": {"type": "string"},
        "cell": {"type": "string"},
        "view": {"type": "string"},
        "nam": {"type": "string"},
        "ic": {"type": ["integer", "null"]},
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_LAYOUT_PCELL_ITEM = {
    "type": "object",
    "required": ["type", "lib", "cell", "view", "loc"],
    "properties": {
        "type": {"const": "Pcell"},
        "lib": {"type": "string"},
        "cell": {"type": "string"},
        "view": {"type": "string"},
        "nam": {"type": "string"},
        "ic": {"type": ["integer", "null"]},
        "loc": _POINT_SCHEMA,
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
        "params": {"type": "object"},
    },
}

_LAYOUT_RECT_ITEM = {
    "type": "object",
    "required": ["type", "tl", "br", "ln"],
    "properties": {
        "type": {"const": "Rect"},
        "tl": _POINT_SCHEMA,
        "br": _POINT_SCHEMA,
        "ln": {"type": "integer", "minimum": 0},
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_LAYOUT_PATH_ITEM = {
    "type": "object",
    "required": ["type", "dfl1", "dfl2", "ln", "w", "se", "ee", "md"],
    "properties": {
        "type": {"const": "Path"},
        "dfl1": _POINT_SCHEMA,
        "dfl2": _POINT_SCHEMA,
        "ln": {"type": "integer", "minimum": 0},
        "w": {"type": "number"},
        "se": {"type": "number"},
        "ee": {"type": "number"},
        "md": {"type": "string"},
        "nam": {"type": "string"},
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_LAYOUT_VIA_ITEM = {
    "type": "object",
    "required": ["type", "st", "via", "xs", "ys", "xn", "yn"],
    "properties": {
        "type": {"const": "Via"},
        "st": _POINT_SCHEMA,
        "via": {"type": "object"},
        "xs": {"type": "number"},
        "ys": {"type": "number"},
        "xn": {"type": "integer"},
        "yn": {"type": "integer"},
    },
}

_LAYOUT_PIN_ITEM = {
    "type": "object",
    "required": ["type", "tl", "br", "pn", "pd", "pt", "ln"],
    "properties": {
        "type": {"const": "Pin"},
        "tl": _POINT_SCHEMA,
        "br": _POINT_SCHEMA,
        "pn": {"type": "string"},
        "pd": {"type": "string"},
        "pt": {"type": "string"},
        "ln": {"type": "integer", "minimum": 0},
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_LAYOUT_LABEL_ITEM = {
    "type": "object",
    "required": ["type", "st", "lt", "ff", "fs", "fh", "la", "lo", "ln"],
    "properties": {
        "type": {"const": "Label"},
        "st": _POINT_SCHEMA,
        "lt": {"type": "string"},
        "ff": {"type": "string"},
        "fs": {"type": "string"},
        "fh": {"type": ["number", "integer"]},
        "la": {"type": "string"},
        "lo": {"type": "string"},
        "ln": {"type": "integer", "minimum": 0},
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_LAYOUT_POLYGON_ITEM = {
    "type": "object",
    "required": ["type", "ps", "ln"],
    "properties": {
        "type": {"const": "Polygon"},
        "ps": {"type": "array", "items": _POINT_SCHEMA, "minItems": 3},
        "ln": {"type": "integer", "minimum": 0},
        "ang": {"type": "number"},
        "fl": _FLIP_TUPLE_SCHEMA,
    },
}

_LAYOUT_RULER_ITEM = {
    "type": "object",
    "required": ["type", "dfl1", "dfl2", "md"],
    "properties": {
        "type": {"const": "Ruler"},
        "dfl1": _POINT_SCHEMA,
        "dfl2": _POINT_SCHEMA,
        "md": {"type": "string"},
        "ang": {"type": "number"},
    },
}

_LAYOUT_ITEM_SCHEMA = {
    "oneOf": [
        _LAYOUT_INSTANCE_ITEM,
        _LAYOUT_PCELL_ITEM,
        _LAYOUT_RECT_ITEM,
        _LAYOUT_PATH_ITEM,
        _LAYOUT_VIA_ITEM,
        _LAYOUT_PIN_ITEM,
        _LAYOUT_LABEL_ITEM,
        _LAYOUT_POLYGON_ITEM,
        _LAYOUT_RULER_ITEM,
    ]
}

# ---------------------------------------------------------------------------
# View header schema
# ---------------------------------------------------------------------------

_VIEW_HEADER_SCHEMA = {
    "type": "object",
    "required": ["viewType"],
    "properties": {
        "viewType": {"type": "string", "enum": ["symbol", "schematic", "layout"]},
        "schemaVersion": {"type": "string"},
    },
}

_GRID_SETTINGS_SCHEMA = {
    "type": "object",
    "properties": {
        "snapGrid": {
            "type": "array",
            "items": {"type": ["number", "integer"]},
            "minItems": 2,
            "maxItems": 2,
        }
    },
}

# ---------------------------------------------------------------------------
# Top-level file schemas
# ---------------------------------------------------------------------------

SYMBOL_FILE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Revolution EDA Symbol File",
    "description": "Schema for symbol design files",
    "type": "array",
    "minItems": 2,
    "items": [
        _VIEW_HEADER_SCHEMA,
        _GRID_SETTINGS_SCHEMA,
    ],
    "additionalItems": _SYMBOL_ITEM_SCHEMA,
}

SCHEMATIC_FILE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Revolution EDA Schematic File",
    "description": "Schema for schematic design files",
    "type": "array",
    "minItems": 2,
    "items": [
        _VIEW_HEADER_SCHEMA,
        _GRID_SETTINGS_SCHEMA,
    ],
    "additionalItems": _SCHEMATIC_ITEM_SCHEMA,
}

LAYOUT_FILE_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Revolution EDA Layout File",
    "description": "Schema for layout design files",
    "type": "array",
    "minItems": 2,
    "items": [
        _VIEW_HEADER_SCHEMA,
        _GRID_SETTINGS_SCHEMA,
    ],
    "additionalItems": _LAYOUT_ITEM_SCHEMA,
}

# Mapping from viewType to schema
_VIEW_TYPE_SCHEMAS = {
    "symbol": SYMBOL_FILE_SCHEMA,
    "schematic": SCHEMATIC_FILE_SCHEMA,
    "layout": LAYOUT_FILE_SCHEMA,
}


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


class DesignFileValidationError(Exception):
    """Raised when a design file fails schema validation.

    Attributes:
        file_path: Path to the invalid file (if available).
        errors: List of human-readable error descriptions.
    """

    def __init__(self, message: str, file_path: str = "",
                 errors: Optional[List[str]] = None):
        super().__init__(message)
        self.file_path = file_path
        self.errors = errors or []


def _format_validation_error(error: ValidationError) -> str:
    """Convert a jsonschema ValidationError to a human-friendly message."""
    path = " -> ".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
    return f"At '{path}': {error.message}"


def validate_design_data(
    data: Any,
    file_path: str = "",
    strict: bool = False,
) -> Tuple[bool, List[str]]:
    """Validate loaded JSON data against the appropriate design file schema.

    Performs structural validation of the top-level array, view header,
    and grid settings. Individual item validation is done only in strict mode
    to allow forward-compatible file loading.

    Args:
        data: The parsed JSON data (expected to be a list).
        file_path: Optional file path for error reporting.
        strict: If True, validate every item against the item schema.
                If False, only validate the structure/header (faster).

    Returns:
        A tuple of (is_valid, error_messages).
        If is_valid is True, error_messages is empty.
    """
    errors: List[str] = []

    # Basic structure check
    if not isinstance(data, list):
        errors.append(
            f"Design file must be a JSON array, got {type(data).__name__}"
        )
        return False, errors

    if len(data) < 2:
        errors.append(
            "Design file must contain at least a view header and grid "
            "settings (minimum 2 elements)"
        )
        return False, errors

    # Validate view header
    view_header = data[0]
    if not isinstance(view_header, dict):
        errors.append(
            f"First element (view header) must be an object, "
            f"got {type(view_header).__name__}"
        )
        return False, errors

    view_type = view_header.get("viewType")
    if view_type not in ("symbol", "schematic", "layout"):
        errors.append(
            f"Invalid or missing 'viewType' in header. "
            f"Expected 'symbol', 'schematic', or 'layout', got: {view_type!r}"
        )
        return False, errors

    # Validate grid settings
    grid_settings = data[1]
    if grid_settings is not None and not isinstance(grid_settings, dict):
        errors.append(
            f"Second element (grid settings) must be an object or null, "
            f"got {type(grid_settings).__name__}"
        )
        return False, errors

    if grid_settings and "snapGrid" in grid_settings:
        snap_grid = grid_settings["snapGrid"]
        if not (isinstance(snap_grid, (list, tuple)) and len(snap_grid) == 2):
            errors.append(
                f"'snapGrid' must be a 2-element array, got: {snap_grid!r}"
            )
            return False, errors

    # Validate items in strict mode
    if strict:
        schema = _VIEW_TYPE_SCHEMAS.get(view_type)
        if schema:
            try:
                jsonschema.validate(instance=data, schema=schema)
            except ValidationError as e:
                # Collect up to 10 errors for user feedback
                validator = jsonschema.Draft7Validator(schema)
                for i, err in enumerate(validator.iter_errors(data)):
                    if i >= 10:
                        errors.append("... (additional errors truncated)")
                        break
                    errors.append(_format_validation_error(err))
                return False, errors
            except SchemaError as e:
                # Internal schema error - log but don't block loading
                logger.warning(f"Schema definition error: {e.message}")

    # Non-strict item validation: check that items have a 'type' field
    if not strict:
        for idx, item in enumerate(data[2:], start=2):
            if isinstance(item, dict) and "type" not in item:
                errors.append(
                    f"Item at index {idx} is missing required 'type' field"
                )

    if errors:
        return False, errors

    return True, []


def validate_design_file(
    data: Any,
    view_type: str,
    file_path: str = "",
    strict: bool = False,
) -> Tuple[bool, List[str]]:
    """Validate design file data with an expected view type.

    This is a convenience wrapper that also verifies the viewType matches
    the expected type.

    Args:
        data: The parsed JSON data.
        view_type: Expected view type ('symbol', 'schematic', 'layout').
        file_path: Optional file path for error reporting.
        strict: If True, run full jsonschema validation.

    Returns:
        A tuple of (is_valid, error_messages).
    """
    is_valid, errors = validate_design_data(data, file_path, strict)
    if not is_valid:
        return False, errors

    actual_type = data[0].get("viewType")
    if actual_type != view_type:
        return False, [
            f"Expected view type '{view_type}', but file contains "
            f"'{actual_type}'"
        ]

    return True, []


def get_schema_version(data: Any) -> Optional[str]:
    """Extract the schema version from design file data.

    Returns None if no schema version is present (pre-versioning files).
    """
    if isinstance(data, list) and len(data) >= 1 and isinstance(data[0], dict):
        return data[0].get("schemaVersion")
    return None
