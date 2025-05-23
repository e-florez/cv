import pytest
import yaml
import os
import sys
import shutil
import json
import subprocess
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent # cv/tests/ -> cv/ -> project_root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cv.validators import main_validate, generate_schema
from cv.schemas import CVData # For type hinting or direct model use if needed

# Helper to create a YAML file in tmp_path for testing
def make_cv_yaml(base_path: Path, data_dict: dict, filename: str = "cv_data_test.yaml"):
    # No need to create cv/data structure if full path is used by main_validate
    file_path = base_path / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data_dict, f)
    return str(file_path)

# Minimal valid data structure (can be extended by tests)
minimal_metadata = {
    "variants": {
        "ds": {"name": "Data Science", "description": "DS variant", "sections": ["experience", "education", "projects"]},
        "ac": {"name": "Academic", "description": "Academic variant", "sections": ["education", "publications"]},
        "general": {"name": "General", "description": "General purpose", "sections": ["experience", "projects"]}
    }
}

minimal_personal_info = {"name": "Test User", "email": "test@example.com"}
minimal_profile = "A test profile."

def get_valid_cv_data(overrides=None):
    data = {
        "personal_info": minimal_personal_info.copy(),
        "profile": minimal_profile,
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
        "metadata": minimal_metadata.copy()
    }
    if overrides:
        # Simple override, not deep merge. For deep merge, a utility would be needed.
        data.update(overrides)
    return data

def test_successful_validation(tmp_path):
    valid_data = get_valid_cv_data()
    cv_yaml_path = make_cv_yaml(tmp_path, valid_data)
    assert main_validate(file_path=cv_yaml_path) == True

def test_missing_required_field(tmp_path):
    invalid_data = get_valid_cv_data()
    del invalid_data["personal_info"]["name"] # name is required
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate(file_path=cv_yaml_path) == False

def test_incorrect_date_format(tmp_path):
    invalid_data = get_valid_cv_data()
    invalid_data["experience"][0]["start_date"] = "2021 Aug" # Incorrect format
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate(file_path=cv_yaml_path) == False

def test_invalid_email_format(tmp_path):
    invalid_data = get_valid_cv_data()
    invalid_data["personal_info"]["email"] = "not-an-email"
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate(file_path=cv_yaml_path) == False

def test_invalid_url_format(tmp_path):
    invalid_data = get_valid_cv_data()
    invalid_data["personal_info"]["linkedin"] = "not_a_url" # Optional field, but if present, must be valid URL
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate(file_path=cv_yaml_path) == False

def test_invalid_variant_tag(tmp_path):
    invalid_data = get_valid_cv_data()
    invalid_data["experience"][0]["variants"] = ["non_existent_variant"]
    cv_yaml_path = make_cv_yaml(tmp_path, invalid_data)
    assert main_validate(file_path=cv_yaml_path) == False

def test_valid_variant_tag(tmp_path):
    # This is effectively covered by test_successful_validation,
    # but can be more specific if needed.
    valid_data = get_valid_cv_data()
    # Ensure at least one item has a variant tag that is defined
    valid_data["experience"][0]["variants"] = ["ds"]
    valid_data["metadata"]["variants"] = {"ds": {"name": "Data Science", "description": "Test", "sections": ["experience"]}}
    cv_yaml_path = make_cv_yaml(tmp_path, valid_data)
    assert main_validate(file_path=cv_yaml_path) == True

def test_malformed_yaml_file(tmp_path):
    malformed_yaml_content = "personal_info: \n  name: Test\n email: test@example.com" # Incorrect indentation for email
    file_path = tmp_path / "malformed.yaml"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(malformed_yaml_content)
    assert main_validate(file_path=str(file_path)) == False

def test_empty_yaml_file(tmp_path):
    file_path = tmp_path / "empty.yaml"
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("") # Empty file
    assert main_validate(file_path=str(file_path)) == False

def test_schema_generation(tmp_path):
    schema_output_file = tmp_path / "cv_schema.json"
    
    # Capture stdout/stderr to check messages if needed, but problem statement focuses on file
    # For generate_schema, it sys.exits on error. We can run it in a subprocess
    # or rely on pytest to capture SystemExit if not caught by the function.
    # The function itself prints and logs.
    
    # generate_schema might call sys.exit(1) on error.
    # A simple way to test this without subprocess is to expect it to not raise SystemExit for success.
    try:
        generate_schema(output_path=str(schema_output_file))
    except SystemExit as e:
        pytest.fail(f"generate_schema exited unexpectedly: {e}")

    assert schema_output_file.exists()
    with open(schema_output_file, 'r') as f:
        content = json.load(f)
    
    assert "title" in content
    assert content["title"] == "CVData"
    assert "properties" in content
    assert "personal_info" in content["properties"]
    assert "definitions" in content # Pydantic uses "definitions" or "$defs" based on version
                                    # For older Pydantic v1, it's "definitions"
                                    # For Pydantic v2, it might be "$defs"
    # Check for some known models in definitions (actual names might vary with Pydantic settings)
    expected_definitions = ["PersonalInfo", "ExperienceItem", "EducationItem", "Skills"]
    # Pydantic v2 might use "$defs"
    defs_key = "$defs" if "$defs" in content else "definitions"

    for def_name in expected_definitions:
        assert def_name in content[defs_key], f"{def_name} not found in schema {defs_key}"

# Example of how to check log content if needed (requires more setup or modification to validators.py)
# def test_successful_validation_with_log_check(tmp_path, caplog):
#     import logging
#     caplog.set_level(logging.INFO)
#     valid_data = get_valid_cv_data()
#     cv_yaml_path = make_cv_yaml(tmp_path, valid_data)
#     assert main_validate(file_path=cv_yaml_path) == True
#     assert "YAML validation passed successfully" in caplog.text
# Requires validators.py to use a logger that caplog can capture.
# If validators.py configures its own file-based logger directly,
# caplog won't capture it without changes to how logging is set up in validators.py.
# For now, log checking is omitted as per instructions.
# The `PROJECT_ROOT/cv/validation.log` will be written to by the tests.
# This file should be in .gitignore.
# To make tests more isolated regarding logging, validators.py would need to be refactored
# to allow injection of log configuration or path.
```
