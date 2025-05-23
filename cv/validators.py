"""CV Data Validator and Schema Generator.

This script provides functionalities to:
1. Validate the structure and content of a CV YAML data file (`cv_data.yaml`)
   against Pydantic models defined in `cv.schemas`.
2. Perform custom validations, such as ensuring all variant tags used in CV items
   are defined in the metadata.
3. Generate a JSON schema from the Pydantic models.

It can be run as a command-line interface (CLI) to perform these actions.
Path configurations assume the script is part of a project structure where
the 'cv' directory is a direct child of the project root.
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Type

import yaml
from pydantic import BaseModel, ValidationError

# Determine PROJECT_ROOT: assumes this script is in 'project_root/cv/'
# So, Path(__file__).resolve() is 'project_root/cv/validators.py'
# .parent is 'project_root/cv/'
# .parent.parent is 'project_root/'
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cv.schemas import CVData # noqa: E402 - Project import after sys.path modification

# --- Logging Configuration ---
LOG_FILE_DIR = PROJECT_ROOT / "cv"
LOG_FILE_DIR.mkdir(parents=True, exist_ok=True) # Ensure 'cv' directory exists for the log
LOG_FILE_PATH = LOG_FILE_DIR / "validation.log"

logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
)
# Add a handler to also print INFO and higher messages to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s: %(message)s') # Simpler format for console
console_handler.setFormatter(console_formatter)
# Get the root logger and add the handler to it
# Avoid adding multiple times if script is re-run in same session (e.g. testing)
if not any(isinstance(h, logging.StreamHandler) and h.stream == sys.stdout for h in logging.getLogger().handlers):
    logging.getLogger().addHandler(console_handler)


# --- File Operations ---

def load_yaml_file(file_path: Path) -> dict[str, Any] | None:
    """Load YAML data from the given file path.

    Parameters
    ----------
    file_path : Path
        The path to the YAML file.

    Returns
    -------
    dict[str, Any] | None
        The loaded data as a dictionary, or None if an error occurs
        (e.g., file not found, YAML parsing error).
    """
    logging.info(f"Attempting to load YAML file: {file_path}")
    try:
        with file_path.open('r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)
        if raw_data is None:
            logging.error(f"YAML file {file_path} is empty or malformed, resulting in None data.")
            print(f"Error: YAML file '{file_path}' is empty or could not be parsed to valid data.")
            return None
        logging.debug(f"Successfully loaded YAML data from {file_path}.")
        return raw_data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}", exc_info=True)
        print(f"Error: File not found '{file_path}'")
        return None
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file '{file_path}': {e}", exc_info=True)
        print(f"Error: Could not parse YAML file '{file_path}'. Details: {e}")
        return None
    except Exception as e: # Catch other potential IO errors
        logging.error(f"An unexpected error occurred while reading file '{file_path}': {e}", exc_info=True)
        print(f"Error: An unexpected error occurred while reading file '{file_path}'.")
        return None

# --- Pydantic Model Parsing ---

def parse_cv_data(raw_data: dict[str, Any] | None, file_path_str: str) -> CVData | None:
    """Parse raw dictionary data into a CVData Pydantic model.

    Parameters
    ----------
    raw_data : dict[str, Any] | None
        The raw data loaded from YAML. If None, parsing is skipped.
    file_path_str : str
        The original file path string, used for error messages.

    Returns
    -------
    CVData | None
        A CVData Pydantic model instance if parsing is successful,
        or None if raw_data is None or a Pydantic ValidationError occurs.
    """
    if raw_data is None:
        logging.warning("Raw data is None, skipping Pydantic parsing.")
        return None

    logging.debug(f"Attempting to parse raw data into CVData model for {file_path_str}.")
    try:
        cv_data_obj = CVData(**raw_data)
        logging.debug(f"Successfully parsed data into CVData model for {file_path_str}.")
        return cv_data_obj
    except ValidationError as e:
        logging.error(f"Pydantic validation failed for '{file_path_str}':\n{e.json(indent=2)}")
        print(f"\nError: Data validation failed for '{file_path_str}':")
        for error in e.errors():
            loc_parts = [str(p) for p in error['loc']]
            loc_str = " -> ".join(loc_parts) if loc_parts else "Top-level"
            input_value = error.get('input', 'N/A')
            input_repr = repr(input_value) if not isinstance(input_value, (dict, list)) else type(input_value).__name__
            msg = error['msg']
            print(f"  - At '{loc_str}': {msg} (Input: {input_repr}, Type: {error.get('type', 'N/A')})")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during Pydantic model parsing for '{file_path_str}': {e}", exc_info=True)
        print(f"Error: An unexpected error occurred during data parsing for '{file_path_str}'.")
        return None

# --- Custom Validations ---

def perform_variant_tag_validation(cv_data: CVData) -> bool:
    """Validate variant tags used in CV items against metadata definitions.

    Assumes `cv_data` is a valid `CVData` object.

    Parameters
    ----------
    cv_data : CVData
        The CVData object containing all CV information.

    Returns
    -------
    bool
        True if all variant tags are valid or if metadata/variants are not defined
        (treated as a warning), False if invalid tags are found.
    """
    logging.debug("Performing variant tag validation.")
    if not cv_data.metadata or not cv_data.metadata.variants:
        logging.warning("Metadata or metadata.variants is missing. Skipping variant tag validation.")
        # This is treated as a non-critical issue for this specific validation function.
        # The overall validation might still fail if metadata is required by the schema.
        return True # Or False, if strictness requires metadata for this check to pass.

    defined_variant_keys = set(cv_data.metadata.variants.keys())
    all_tags_valid = True

    sections_to_check = {
        "experience": cv_data.experience,
        "education": cv_data.education,
        "publications": cv_data.publications,
        "projects": cv_data.projects,
        "awards": cv_data.awards,
    }

    for section_name, items in sections_to_check.items():
        if items:
            for i, item in enumerate(items):
                if hasattr(item, 'variants') and item.variants:
                    for tag in item.variants:
                        if tag not in defined_variant_keys:
                            all_tags_valid = False
                            item_identifier = getattr(item, 'title', getattr(item, 'name', getattr(item, 'degree', f"Item {i}")))
                            error_msg = (f"Invalid variant tag '{tag}' in {section_name}[{i}] "
                                         f"('{item_identifier}'). Valid tags are: {list(defined_variant_keys)}.")
                            print(f"  - Variant Error: {error_msg}")
                            logging.error(error_msg)
    
    if all_tags_valid:
        logging.debug("Variant tag validation passed.")
    else:
        logging.error("Variant tag validation failed.")
    return all_tags_valid

# --- Schema Generation ---

def _generate_json_schema_string(model: Type[BaseModel]) -> str:
    """Generate a JSON schema string from a Pydantic model.

    Parameters
    ----------
    model : Type[BaseModel]
        The Pydantic model class (e.g., CVData).

    Returns
    -------
    str
        The JSON schema as a string, indented for readability.
    """
    logging.debug(f"Generating JSON schema for model: {model.__name__}")
    schema_dict = model.model_json_schema()
    return json.dumps(schema_dict, indent=2)

def _write_schema_to_file(schema_str: str, output_path: Path) -> bool:
    """Write the JSON schema string to the output_path.

    Ensures the output directory exists. Handles potential IOError.

    Parameters
    ----------
    schema_str : str
        The JSON schema string to write.
    output_path : Path
        The file path where the schema should be saved.

    Returns
    -------
    bool
        True on success, False on error.
    """
    logging.debug(f"Attempting to write schema to file: {output_path}")
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open('w', encoding='utf-8') as f:
            f.write(schema_str)
        logging.info(f"JSON schema successfully written to {output_path}")
        return True
    except IOError as e:
        logging.error(f"Error writing JSON schema to file '{output_path}': {e}", exc_info=True)
        print(f"Error: Could not write schema to file '{output_path}'.")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while writing schema to '{output_path}': {e}", exc_info=True)
        print(f"Error: An unexpected error occurred while writing schema to '{output_path}'.")
        return False

# --- CLI Entry Points ---

def main_validate_cli(file_path: Path) -> bool:
    """Orchestrate the CV data validation process.

    Loads, parses, and validates CV data from the specified file.

    Parameters
    ----------
    file_path : Path
        Path to the CV YAML data file.

    Returns
    -------
    bool
        True if validation is successful, False otherwise.
    """
    logging.info(f"Starting validation process for: {file_path}")

    raw_data = load_yaml_file(file_path)
    if raw_data is None:
        logging.error("Validation failed: Could not load YAML file.")
        print(f"\nValidation Result: FAILED for '{file_path}'. Reason: YAML loading error.")
        return False

    cv_data_obj = parse_cv_data(raw_data, str(file_path))
    if cv_data_obj is None:
        logging.error("Validation failed: Pydantic model parsing/validation error.")
        print(f"\nValidation Result: FAILED for '{file_path}'. Reason: Data structure or type error.")
        return False

    if not perform_variant_tag_validation(cv_data_obj):
        logging.error("Validation failed: Variant tag validation error.")
        print(f"\nValidation Result: FAILED for '{file_path}'. Reason: Invalid variant tags.")
        return False

    success_msg = f"CV data validation passed successfully for '{file_path}'."
    logging.info(success_msg)
    print(f"\nValidation Result: SUCCESS for '{file_path}'.")
    return True

def generate_schema_cli(output_path: Path) -> bool:
    """Orchestrate JSON schema generation and writing to file.

    Parameters
    ----------
    output_path : Path
        The file path where the generated schema should be saved.

    Returns
    -------
    bool
        True if schema generation and writing is successful, False otherwise.
    """
    logging.info(f"Starting schema generation. Output path: {output_path}")
    schema_str = _generate_json_schema_string(CVData)
    
    if _write_schema_to_file(schema_str, output_path):
        logging.info(f"Schema generation successful. Schema saved to {output_path}")
        print(f"JSON schema successfully generated at: {output_path}")
        return True
    else:
        logging.error(f"Schema generation failed. Could not write schema to {output_path}")
        print(f"Error: Schema generation failed. Could not write to '{output_path}'.")
        return False

# --- Main CLI Parsing and Execution ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CV Data Validator and JSON Schema Generator.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help="Run CV data validation against the YAML file."
    )
    parser.add_argument(
        '--generate-schema',
        action='store_true',
        help="Generate JSON schema from Pydantic models."
    )
    parser.add_argument(
        '--file-path',
        type=Path,
        default=PROJECT_ROOT / "cv" / "data" / "cv_data.yaml",
        help="Path to the CV YAML data file for validation.\n"
             f"(default: {PROJECT_ROOT / 'cv' / 'data' / 'cv_data.yaml'})"
    )
    parser.add_argument(
        '--schema-output-path',
        type=Path,
        default=PROJECT_ROOT / "cv" / "schema.json",
        help="Output path for the generated JSON schema.\n"
             f"(default: {PROJECT_ROOT / 'cv' / 'schema.json'})"
    )

    args = parser.parse_args()

    action_taken = False
    exit_status = 0 # 0 for success, 1 for failure

    if args.generate_schema:
        action_taken = True
        if not generate_schema_cli(output_path=args.schema_output_path):
            exit_status = 1 # Schema generation failed
    
    if args.validate:
        action_taken = True
        # If schema generation already failed, we still try validation but preserve failure status
        if not main_validate_cli(file_path=args.file_path) and exit_status == 0:
            exit_status = 1 # Validation failed
    
    if not action_taken:
        # Default action: validate if no specific flags are provided
        logging.info("No specific action requested, defaulting to validation.")
        print("Defaulting to validation as no specific action (--validate or --generate-schema) was requested.")
        if not main_validate_cli(file_path=args.file_path):
            exit_status = 1

    if exit_status == 0:
        logging.info("CLI operations completed successfully.")
    else:
        logging.error("CLI operations completed with errors.")
    
    sys.exit(exit_status)
