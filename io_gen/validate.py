import importlib.resources
import json
from pathlib import Path

import jsonschema
import yaml

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .tables.meta_table import MetaTable
from .tables.signal_table import SignalTable
from .exceptions import ValidationError
from .identifiers import is_valid_verilog_identifier, is_valid_vhdl_identifier
from .checks import (
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
    _check_non_ascii,
)

# Top level JSON schema file for validating input YAML stored in schema/
SCHEMA_TOP = "schema.json"
# Referenced JSON files stored in schema/defs
SCHEMA_REFS = [
    "constraints.json",
    "direction.json",
    "buffer.json",
    "pinset.json",
    "iostandard.json",
    "instance.json",
    "pins.json",
]


def _build_resource(schema_path: Path) -> Resource:
    """Create a Resource object from a resolved path to a JSON file"""
    with open(schema_path) as f:
        contents = json.load(f)
    return Resource(contents=contents, specification=DRAFT202012)


def _build_registry() -> Registry:
    """Create a Registry object containing all JSON schema resources

    Resolving references in the top level JSON schema requires pairing each discrete JSON object (including the top
    level schema) with its draft specification to create a referencing.Resource object. The complete set of these
    Resource objects is then associated together as a referencing.Registry object.  That Registry object is then passed
    to the jsonschema validator object.
    """
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
    # This returns None if successful and raises an exception if not
    try:
        validator.validate(doc)
    except jsonschema.ValidationError as e:
        # This exception gives almost no information as to what the offending
        # portion of the JSON is, so we're going to extract it and craft a better
        # message, since users will undoubtedly have to debug their YAML and without
        # knowing the offending signal, they'll be lost.

        # The exception itself has a ton of information in it so grab part of it and convert
        # the deque to a list (set a breakpoint() here if needed to examine this thing in the
        # future)
        path = list(e.absolute_path)

        # If the reason for the exception was a signal (and in this JSON it almost
        # certainly is, since the signals is where all the stuff is at
        if path and path[0] == "signals" and len(path) >= 2:
            # Now we can get the index of the offender
            idx = path[1]
            signals = doc["signals"]
            # Now extract the name of the signal entry that is causing the problem
            # (if there is no name yet, return the index of the offender in the signals list)
            offender = signals[idx].get("name", f"signals[{idx}]")
            raise ValidationError(f"{offender}: {e.message}")

        # If it wasn't a signal that caused the validator to fail, just raise
        raise ValidationError(e.message)


def _validate_semantic(doc: dict) -> None:
    """Validate parsed YAML for domain consistency"""

    # Explicitly assuming that structural validation was successful
    signals = doc["signals"]

    _check_pin_name_format(signals)
    _check_unique_signal_names(signals)
    _check_unique_pins(signals)
    _check_minimum_ports_generated(signals)

    # Now validate each signal individually
    for sig in signals:
        _check_pinset_array_mismatch(sig)
        _check_pins_array_width_match(sig)
        _check_pinset_array_width_match(sig)
        _check_buffer_direction(sig)
        _check_buffer_strategy_match(sig)
        _check_buffer_infer_bypass_mismatch(sig)
        _check_buffer_inferable(sig)


def validate(yaml_file: Path) -> dict:
    """Validate a YAML file for structural and semantical accuracy"""

    # Before doing anything, we check the YAML for non-ascii encoded unicode
    _check_non_ascii(yaml_file)

    # Load the YAML from the provided path - this can fail and raise and
    # exception if the file is missing or the user doesn't have read permissions
    with open(yaml_file) as f:
        try:
            doc = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValidationError(str(e))

    # Each of these can raise a ValidationError
    _validate_structural(doc)
    _validate_semantic(doc)

    return doc


def validate_verilog(signal_table: SignalTable, top: str) -> None:
    """Validate signal names, instance names, and the top module name as legal Verilog identifiers.

    Checks that every signal name and resolved instance name in the signal table is
    a valid Verilog simple identifier, and that the top module name is also valid.
    Raises ValidationError on the first invalid name encountered.

    Parameters
    ----------
    signal_table:
        Constructed signal table to validate.
    top:
        Top-level module name supplied at runtime.
    """
    # Check the top level name
    if not is_valid_verilog_identifier(top):
        raise ValidationError(
            f"Top level module name '{top}' is not a valid Verilog identifier"
        )
    # Check all the signal names
    for sig in signal_table:
        if not is_valid_verilog_identifier(sig["name"]):
            raise ValidationError(f"{sig['name']} is not a valid Verilog identifier")
        if not sig["bypass"] and not is_valid_verilog_identifier(sig["instance"]):
            raise ValidationError(
                f"{sig['instance']} is not a valid Verilog identifier"
            )


def validate_vhdl(signal_table: SignalTable, meta_table: MetaTable, top: str) -> None:
    """Validate signal names, instance names, and the top entity name as legal VHDL identifiers.

    Checks that every signal name and resolved instance name in the signal table is
    a valid VHDL basic identifier, and that the top entity name is also valid.
    Raises ValidationError on the first invalid name encountered.

    Parameters
    ----------
    signal_table:
        Constructed signal table to validate.
    meta_table:
        Constructed meta table to validate.
    top:
        Top-level entity name supplied at runtime.
    """
    # Check the architecture value
    if meta_table.architecture is None:
        raise ValidationError("No architecture was specified")
    if not is_valid_vhdl_identifier(meta_table.architecture):
        raise ValidationError(
            f"Specified architecture '{meta_table.architecture}' is not a valid VHDL identifier"
        )
    # Check the top level name
    if not is_valid_vhdl_identifier(top):
        raise ValidationError(
            f"Top level entity name '{top}' is not a valid VHDL identifier"
        )
    # Check all the signal names
    for sig in signal_table:
        if not is_valid_vhdl_identifier(sig["name"]):
            raise ValidationError(f"{sig['name']} is not a valid VHDL identifier")
        if not sig["bypass"] and not is_valid_vhdl_identifier(sig["instance"]):
            raise ValidationError(f"{sig['instance']} is not a valid VHDL identifier")
