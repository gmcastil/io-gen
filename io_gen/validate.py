import importlib.resources
import json
from pathlib import Path

import jsonschema
import yaml

from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

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


class ValidationError(Exception):
    pass


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


# f"signal '{name}': length mismatch"  (in reg z)


def _check_unique_signal_names(signals: list[dict]) -> None:
    """Check that no two signals share the same name.

    Raises ValidationError identifying the first duplicate name found.
    Applies to all signals, including those with generate: false.
    """
    raise NotImplementedError


def _check_unique_pins(signals: list[dict]) -> None:
    """Check that no physical pin is assigned to more than one signal.

    Checks both pins (scalar and array) and pinset (p and n legs).
    Applies to all signals, including those with generate: false.
    Raises ValidationError identifying the first duplicate pin found.
    """
    raise NotImplementedError


def _check_pinset_array_mismatch(sig: dict) -> None:
    """Check that pinset.p and pinset.n are the same type and length.

    Both must be scalar strings or both must be arrays. If arrays,
    they must have equal length.
    Raises ValidationError identifying the signal and the mismatch.
    Skips signals that do not use pinset.
    """
    raise NotImplementedError


def _check_pins_array_width_match(sig: dict) -> None:
    """Check that the declared width matches the length of the pins array.

    Only applies when pins is an array. Raises ValidationError identifying
    the signal, the declared width, and the actual pin count.
    Skips signals that use scalar pins, pinset, or generate: false.
    """
    raise NotImplementedError


def _check_pinset_array_width_match(sig: dict) -> None:
    """Check that the declared width matches the length of the pinset.p array.

    Only applies when pinset.p is an array. Raises ValidationError identifying
    the signal, the declared width, and the actual pin count.
    Skips signals that use scalar pinset, pins, or generate: false.
    """
    raise NotImplementedError


def _check_buffer_direction(sig: dict) -> None:
    """Check that the buffer type is compatible with the declared direction.

    Required pairings: ibuf->in, obuf->out, ibufds->in, obufds->out, iobuf->inout.
    Raises ValidationError identifying the signal, buffer, and direction.
    Skips signals with generate: false or bypass: true (no buffer required).
    """
    raise NotImplementedError


def _check_buffer_strategy_match(sig: dict) -> None:
    """Check that the buffer type is compatible with the pin assignment strategy.

    ibuf, obuf, and iobuf require pins. ibufds and obufds require pinset.
    Raises ValidationError identifying the signal, buffer, and pin strategy used.
    Skips signals with generate: false or bypass: true (no buffer required).
    """
    raise NotImplementedError


def _check_buffer_infer_bypass_mismatch(sig: dict) -> None:
    """Check that bypass: true and infer: true are not both set on the same signal.

    These are mutually exclusive: bypass means an external component provides
    the buffer, while infer asks the synthesis tool to infer one.
    Raises ValidationError identifying the signal.
    """
    raise NotImplementedError


def _check_buffer_inferable(sig: dict) -> None:
    """Check that infer: true is only used with ibuf or obuf.

    Synthesis inference is predictable and guaranteed correct only for these
    two single-ended buffer types. All other types must be instantiated explicitly.
    Raises ValidationError identifying the signal and buffer type.
    Skips signals where infer is false or not set.
    """
    raise NotImplementedError


def _validate_semantic(doc: dict) -> None:
    """Validate parsed YAML for domain consistency"""

    # Explicitly assuming that structural validation was successful
    signals = doc["signals"]

    # Check for unique signal names across all signals
    _check_unique_signal_names(signals)
    # Check for unique pins across all signals
    _check_unique_pins(signals)

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

    # Semantic validation is complete
    return None


def validate(yaml_file: Path) -> dict:
    """Validate a YAML file for structural and semantical accuracy"""

    # Load the YAML from the provided path
    with open(yaml_file) as f:
        doc = yaml.safe_load(f)

    # Each of these can raise a ValidationException, which you'll just let fail
    _validate_structural(doc)
    _validate_semantic(doc)

    # If we're validated, then we can just return the validated doc
    return doc
