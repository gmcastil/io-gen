import pytest
from pathlib import Path
from io_gen import validate, ValidationError


FIXTURES = Path(__file__).parent / "fixtures"
