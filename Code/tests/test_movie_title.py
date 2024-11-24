import pytest
from unittest.mock import patch
import re
import sys
sys.path.append('../recommenderapp')
from recommenderapp.app import format_title

@pytest.mark.parametrize("input_title, expected_output", [
    #  Remove the year and parentheses
    ("The Matrix (1999)", "The Matrix"),

    #  Reorder title with a comma
    ("King, Lion (1994)", "Lion King"),

    # Remove special characters
    ("Batman: The Dark Knight (2008)", "Batman The Dark Knight"),

    ("", ""),
])
def test_format_title(input_title, expected_output):
    assert format_title(input_title) == expected_output