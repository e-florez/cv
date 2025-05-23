"""Pytest tests for the CV data validation and schema generation scripts.

This module contains a suite of tests to verify the functionality of
`cv/validators.py`. It checks:
- Successful validation of correctly structured CV data.
- Failure for various types of invalid data (missing fields, incorrect formats,
  invalid variant tags).
- Handling of malformed or empty YAML files.
- Successful generation of the JSON schema.

Tests use pytest's `tmp_path` fixture to create temporary files and directories,
ensuring that tests do not interfere with the project's actual data or
generated files and that they are run in an isolated environment.
"""
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

# Add project root to sys.path to allow imports like cv.validators
# PROJECT_ROOT is 'project_root/'
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Assuming validators.py is in project_root/cv/
from cv.validators import main_validate_cli, generate_schema_cli # noqa: E402
# from cv.schemas import CVData # Not strictly needed for these tests if not directly instantiating

# --- Test Data Fixtures and Helpers ---

MINIMAL_METADATA: dict[str, Any] = {
    "variants": {
        "ds": {"name": "Data Science", "description": "DS variant", "sections": ["experience", "education", "projects"]},
        "ac": {"name": "Academic", "description": "Academic variant", "sections": ["education", "publications"]},
        "general": {"name": "General", "description": "General purpose", "sections": ["experience", "projects"]}
    }
}

MINIMAL_PERSONAL_INFO: dict[str, str] = {"name": "Test User", "email": "test@example.com"}
MINIMAL_PROFILE: str = "A test profile."

def make_cv_yaml(base_path: Path, data_dict: dict[str, Any], filename: str = "cv_data_test.yaml") -> Path:
    """Create a YAML file in the specified base path for testing.

    The YAML file is created directly in the `base_path`. Test functions
    then pass the full path to this file to the validation scripts.

    Parameters
    ----------
    base_path : Path
        The base temporary directory (typically pytest's `tmp_path`).
    data_dict : dict[str, Any]
        The Python dictionary to dump as YAML content.
    filename : str, optional
        The name of the YAML file, by default "cv_data_test.yaml".

    Returns
    -------
    Path
        The absolute path to the created YAML file.
    """
    file_path = base_path / filename
    # Ensure parent directory exists, though for tmp_path it usually does.
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open('w', encoding='utf-8') as f:
        yaml.dump(data_dict, f)
    return file_path

def get_valid_cv_data(overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Generate a dictionary representing a valid CV data structure.

    This function provides a baseline of valid CV data that can be
    customized with the `overrides` parameter for specific test cases.

    Parameters
    ----------
    overrides : dict[str, Any] | None, optional
        A dictionary of data to override in the baseline valid data.
        This is a shallow update. Default is None.

    Returns
    -------
    dict[str, Any]
        A dictionary representing valid CV data.
    """
    data: dict[str, Any] = {
        "personal_info": MINIMAL_PERSONAL_INFO.copy(),
        "profile": MINIMAL_PROFILE,
        "experience": [{
            "title": "Test Role", "company": "TestCo", "location": "Test City",
            "start_date": "Jan 2020", "end_date": "Dec 2021", "description": "Tested stuff.", "variants": ["ds"]
        }],
        "education": [{
            "degree": "BSc Test", "institution": "Test University", "location": "Testville",
            "start_date": "Sep 2016", "end_date": "Jul 2019", "variants": ["ds", "ac"]
        }],
        "skills": {"technical": [{"name": "Pytesting", "level": "Expert"}]},
        "projects": [{
            "name": "Test Project", "description": "A project for testing.", "technologies": ["python"], "variants": ["ds"]
        }],
        "publications": [{
            "title": "Test Paper", "authors": "Test Author", "journal": "Test Journal", "year": "2022", "variants": ["ac"]
        }],
        "awards": [{"name": "Test Award", "year": "2021", "variants": ["ac"]}],
        "metadata": MINIMAL_METADATA.copy()
    }
    if overrides:
        data.update(overrides) # Shallow update is sufficient for current test needs
    return data

# --- Test Cases ---

def test_successful_validation(tmp_path: Path) -> None:
    """Test that a well-formed, valid CV YAML file passes validation."""
    valid_data = get_valid_cv_data()
    cv_yaml_path = make_cv_yaml(tmp_path, valid_data)
    assert main_validate_cli(file_path=cv_yaml_path) is True

def test_missing_required_field(tmp_path: Path) -> None:
    """Test validation failure when a required field is missing."""
    invalid_data = get_valid_cv_data()
    del invalid_data["personal_info"]["name"]  # 'name' is a required field
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate_cli(file_path=cv_yaml_path) is False

def test_incorrect_date_format(tmp_path: Path) -> None:
    """Test validation failure for incorrect date string formats."""
    invalid_data = get_valid_cv_data()
    invalid_data["experience"][0]["start_date"] = "2021 August"  # Expected "Aug 2021"
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate_cli(file_path=cv_yaml_path) is False

def test_invalid_email_format(tmp_path: Path) -> None:
    """Test validation failure for invalid email address formats."""
    invalid_data = get_valid_cv_data()
    invalid_data["personal_info"]["email"] = "not-an-email-address"
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate_cli(file_path=cv_yaml_path) is False

def test_invalid_url_format(tmp_path: Path) -> None:
    """Test validation failure for invalid URL formats."""
    invalid_data = get_valid_cv_data()
    # 'linkedin' is optional, but if present, must be a valid HttpUrl
    invalid_data["personal_info"]["linkedin"] = "not_a_valid_url"
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate_cli(file_path=cv_yaml_path) is False

def test_invalid_variant_tag(tmp_path: Path) -> None:
    """Test failure when an item uses a variant tag not defined in metadata."""
    invalid_data = get_valid_cv_data()
    invalid_data["experience"][0]["variants"] = ["non_existent_variant_tag"]
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate_cli(file_path=cv_yaml_path) is False

def test_valid_variant_tag(tmp_path: Path) -> None:
    """Test successful validation with correctly defined and used variant tags."""
    # This is largely covered by test_successful_validation.
    # This test ensures that if metadata and variants are correctly set up, it passes.
    valid_data = get_valid_cv_data()
    # Ensure a specific variant tag is present and defined
    valid_data["experience"][0]["variants"] = ["ds"]
    # Ensure the metadata defines this variant
    valid_data["metadata"]["variants"] = {"ds": {"name": "Data Science Variant", "description":"Test", "sections": ["experience"]}}
    cv_yaml_path = make_cv_yaml(tmp_path, valid_data)
    assert main_validate_cli(file_path=cv_yaml_path) is True

def test_malformed_yaml_file(tmp_path: Path) -> None:
    """Test validation failure for syntactically incorrect YAML files."""
    # Example: Incorrect indentation causing a YAML parsing error
    malformed_yaml_content = "personal_info: \n  name: Test User\n email: test@example.com"
    file_path = tmp_path / "malformed.yaml"
    with file_path.open('w', encoding='utf-8') as f:
        f.write(malformed_yaml_content)
    assert main_validate_cli(file_path=file_path) is False

def test_empty_yaml_file(tmp_path: Path) -> None:
    """Test validation failure for empty YAML files."""
    file_path = tmp_path / "empty.yaml"
    with file_path.open('w', encoding='utf-8') as f:
        f.write("")  # Empty content
    assert main_validate_cli(file_path=file_path) is False

def test_schema_generation(tmp_path: Path) -> None:
    """Test successful generation of the JSON schema file."""
    schema_output_file = tmp_path / "cv_schema.json"
    
    # generate_schema_cli returns True on success, False on failure
    assert generate_schema_cli(output_path=schema_output_file) is True

    assert schema_output_file.exists()
    with schema_output_file.open('r', encoding='utf-8') as f:
        content = json.load(f)
    
    assert "title" in content
    assert content["title"] == "CVData"  # As defined in cv.schemas.CVData
    assert "properties" in content
    assert "personal_info" in content["properties"] # A known field in CVData
    
    # Pydantic v1 uses "definitions", Pydantic v2+ often uses "$defs"
    defs_key = "$defs" if "$defs" in content else "definitions"
    assert defs_key in content, f"Neither '$defs' nor 'definitions' found in schema: {content.keys()}"
    
    # Check for some known model names in definitions/defs
    expected_definitions = ["PersonalInfo", "ExperienceItem", "EducationItem", "Skills"]
    for def_name in expected_definitions:
        assert def_name in content[defs_key], f"'{def_name}' not found in schema {defs_key}."

# Note on log checking:
# The current `validators.py` setup configures logging to a file and console.
# Pytest's `caplog` fixture captures logging to the root logger.
# If `validators.py` uses `logging.getLogger()` for its messages, `caplog` should
# capture them if the level is appropriate.
# For example, to check if a specific INFO message was logged to console/captured by caplog:
# def test_successful_validation_log_output(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
#     """Test that successful validation logs an appropriate message."""
#     import logging
#     caplog.set_level(logging.INFO) # Ensure caplog captures INFO messages
#     valid_data = get_valid_cv_data()
#     cv_yaml_path = make_cv_yaml(tmp_path, valid_data)
#     assert main_validate_cli(file_path=cv_yaml_path) is True
#     # Check for the specific success message from main_validate_cli's logging
#     # This depends on the exact message logged by validators.py
#     assert "CV data validation passed successfully" in caplog.text # Or a more specific logger
#
# This kind of test is currently omitted as per instructions but can be added if log output verification is needed.
# The `validation.log` file will be created in `PROJECT_ROOT/cv/` during tests.
# This file should ideally be in `.gitignore`.
```
