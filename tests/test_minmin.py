import re
import tempfile
from unittest.mock import patch
from minpin.minpin import main


def mock_conda_list():
    """Mocked conda list output."""
    return {
        "python": "3.11.10",
        "openssl": "3.4.0",
        "setuptools": "75.5.0",
    }


def run_minpin_forgiving(input_yaml, expected_changes):
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yml", delete=False) as tmp:
        tmp.write(input_yaml)
        tmp.flush()

        with patch("minpin.minpin.get_conda_list", return_value=mock_conda_list()), \
             patch("minpin.minpin.get_pip_list", return_value={}):
            main([tmp.name])  # Call the `main` function with the test argument

        with open(tmp.name, "r") as result_file:
            result = result_file.read()

    for change in expected_changes:
        if not re.search(change, result, re.MULTILINE):
            raise AssertionError(f"Expected change '{change}' not found in:\n{result}")

    return result


def test_core_parsing_logic():
    input_yaml = """
name: test_env
channels:
  - conda-forge
dependencies:
  - python                   # blah blah
  - openssl>=3.3.0           # blah
  - setuptools>=75.0.0
"""
    # Regex patterns to match the expected changes, including dynamic date comment
    expected_changes = [
        r"python>=3\.11\.10.*# auto min pinned.*# blah blah",  # Matches with the auto min pinned tag
        r"openssl>=3\.3\.0.*# blah",  # Pre-pinned package preserved
        r"setuptools>=75\.0\.0",     # Pre-pinned package preserved
    ]
    result = run_minpin_forgiving(input_yaml, expected_changes)
    print(result)
