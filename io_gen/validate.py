import importlib.resources
import json
from pathlib import Path

import jsonschema
import yaml

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .exceptions import ValidationError
from io_gen.checks import (
    _check_pin_name_format,
    _check_unique_signal_names,
    _check_unique_pins,
    _check_pinset_array_mismatch,
    _check_pins_array_width_match,
    _check_pinset_array_width_match,
    _check_buffer_direction,
    _check_buffer_strategy_match,
    _check_buffer_infer_bypass_mismatch,
    _check_buffer_inferable,
    _check_minimum_ports_generated,
)

# Top level JSON schema file for validating input YAML stored in schema/
SCHEMA_TOP = "schema.json"
# Referenced JSON files stored in schema/defs
SCHEMA_REFS = [
    "direction.json",
    "buffer.json",
    "pinset.json",
    "iostandard.json",
    "instance.json",
    "pins.json",
]


# Resolving references in the top level JSON schema requires pairing each discrete JSON object (including
# the top level schema) with its draft specification to create a referencing.Resource object. The complete set of these
# Resource objects is then associated together as a referencing.Registry object.  That Registry object is then passed
# to the jsonschema validator object.


def _build_resource(schema_path: Path) -> Resource:
    """Create a Resource object from a resolved path to a JSON file"""
    with open(schema_path) as f:
        contents = json.load(f)
    return Resource(contents=contents, specification=DRAFT202012)


def _build_registry() -> Registry:
    """Create a Registry object containing all JSON schema resources"""

    # Empty registry
    registry = Registry()
    # Add each file indicated by $ref in the top-level schema to the registry as a resource
    for ref in SCHEMA_REFS:
        # Obtain the path to each schema from the package contained inside the io_gen package,
        # regardless of where it was installed on this machine
        with importlib.resources.as_file(
            importlib.resources.files("io_gen.schema") / "defs" / ref
        ) as schema_path:
            resource = _build_resource(schema_path)
            # Registry objects are immutable, so we "add" to it by creating a new one with
            # our new resource added to it using the __matmul__ operator '@'
            registry = resource @ registry

    return registry


def _validate_structural(doc: dict) -> None:
    """Validate parsed YAML against the schema"""

    # Load the schema from wherever it was
    with importlib.resources.as_file(
        importlib.resources.files("io_gen.schema") / SCHEMA_TOP
    ) as schema_path:
        with open(schema_path) as f:
            schema = json.load(f)

    # Create a registry containing the referenced JSON files in io_gen/schema/defs
    registry = _build_registry()

    validator = jsonschema.Draft202012Validator(schema, registry=registry)
    # This returns None if successful and raises an exceptions if not
    try:
        validator.validate(doc)
    except jsonschema.ValidationError as e:
        raise ValidationError(e.message)


def _validate_semantic(doc: dict) -> None:
    """Validate parsed YAML for domain consistency"""

    # Explicitly assuming that structural validation was successful
    signals = doc["signals"]

    # Check that all pin names are valid before any other pin-related checks
    _check_pin_name_format(signals)
    # Check for unique signal names across all signals
    _check_unique_signal_names(signals)
    # Check for unique pins across all signals
    _check_unique_pins(signals)
    # Check that there are actual signals to generate code for
    _check_minimum_ports_generated(signals)

    # Now validate each signal individually
    for sig in signals:
        # Check pinset array mismatch
        _check_pinset_array_mismatch(sig)
        # Check that all pins arrays match their declared width
        _check_pins_array_width_match(sig)
        # Check that all pinset arrays match their declared width
        _check_pinset_array_width_match(sig)
        # Check that the buffer direction matches the buffer type
        _check_buffer_direction(sig)
        # Check that the type is compatible with the pin strategy
        _check_buffer_strategy_match(sig)
        # Check that buffer inference is not requested for bypass
        _check_buffer_infer_bypass_mismatch(sig)
        # Check that buffer inference is allowed
        _check_buffer_inferable(sig)

    return None


def validate(yaml_file: Path) -> dict:
    """Validate a YAML file for structural and semantical accuracy"""

    # Load the YAML from the provided path
    with open(yaml_file) as f:
        doc = yaml.safe_load(f)

    # Each of these can raise a ValidationError, which we just let fail
    _validate_structural(doc)
    _validate_semantic(doc)

    # If we're validated, then we can just return the validated doc
    return doc
