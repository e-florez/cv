import yaml
from pydantic import ValidationError
import logging
import sys
import os
import argparse
import json
from datetime import datetime

# Add the parent directory (project root) to sys.path to allow imports like cv.schemas
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cv.schemas import CVData

# Setup logging
LOG_FILE_PATH = os.path.join(PROJECT_ROOT, 'cv', 'validation.log')
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True) # Ensure cv directory exists for the log file
logging.basicConfig(filename=LOG_FILE_PATH, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def generate_schema(output_path: str):
    try:
        schema_data = CVData.model_json_schema()
        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema_data, f, indent=2)
        
        success_msg = f"JSON schema successfully generated at {output_path}"
        print(success_msg)
        logging.info(success_msg)
    except Exception as e:
        error_msg = f"Error generating JSON schema: {e}"
        print(error_msg)
        logging.error(error_msg, exc_info=True)
        sys.exit(1)

def validate_variant_tags(cv_data: CVData) -> bool:
    is_valid = True
    if not cv_data.metadata or not cv_data.metadata.variants:
        logging.warning("Metadata or metadata.variants is missing. Cannot validate variant tags.")
        # Depending on strictness, this could be an error. For now, a warning.
        # print("Warning: Metadata or metadata.variants is missing in YAML. Skipping variant tag validation.")
        return True # Or False, if this is considered a validation failure
    
    defined_variant_keys = cv_data.metadata.variants.keys()

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
                # Check if item has 'variants' attribute and it's not None
                if hasattr(item, 'variants') and item.variants:
                    for tag in item.variants:
                        if tag not in defined_variant_keys:
                            is_valid = False
                            # Try to get a meaningful name for the item, e.g. title or name
                            item_identifier = getattr(item, 'title', getattr(item, 'name', getattr(item, 'degree', 'N/A')))
                            error_msg = f"Invalid variant tag '{tag}' in {section_name}[{i}] ('{item_identifier}'). Valid tags are: {list(defined_variant_keys)}."
                            print(error_msg)
                            logging.error(error_msg)
    return is_valid

def main_validate(file_path: str) -> bool: # Default removed, path comes from argparse
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)
        if raw_data is None:
            logging.error(f"YAML file {file_path} is empty or malformed.")
            print(f"Error: YAML file {file_path} is empty or could not be parsed.")
            return False
    except yaml.YAMLError as e:
        error_msg = f"Error parsing YAML file '{file_path}': {e}"
        print(error_msg)
        logging.error(error_msg)
        return False
    except FileNotFoundError:
        error_msg = f"Error: File not found '{file_path}'"
        print(error_msg)
        logging.error(error_msg)
        return False
    except Exception as e: # Catch other potential IO errors
        error_msg = f"An error occurred reading file '{file_path}': {e}"
        print(error_msg)
        logging.error(error_msg)
        return False

    try:
        cv_data_obj = CVData(**raw_data)
        
        # Perform custom cross-field validations
        if not validate_variant_tags(cv_data_obj):
            logging.error("Variant tag validation failed.")
            # Errors already printed by validate_variant_tags
            return False

        success_msg = f"YAML validation passed successfully for '{file_path}'."
        print(success_msg)
        logging.info(success_msg)
        return True

    except ValidationError as e:
        print(f"YAML validation failed for '{file_path}':")
        logging.error(f"YAML validation failed for '{file_path}':\n{e.json(indent=2)}")
        for error in e.errors():
            loc_parts = [str(p) for p in error['loc']]
            loc = " -> ".join(loc_parts)
            
            input_value = error.get('input')
            # For complex inputs (like dicts/lists), a summary might be better
            if isinstance(input_value, (dict, list)):
                input_repr = type(input_value).__name__ # e.g. "dict" or "list"
            else:
                input_repr = repr(input_value)

            msg = error['msg']
            print(f"  Error at '{loc}': {msg} (Input: {input_repr}, Type: {error.get('type')})")
        return False
    except Exception as e:
        # Catch any other unexpected errors during validation logic
        error_msg = f"An unexpected error occurred during validation: {e}"
        print(error_msg)
        logging.exception(error_msg) # Log with stack trace
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CV Data Validator and Schema Generator.")
    parser.add_argument(
        '--validate',
        action='store_true',
        help="Run CV data validation."
    )
    parser.add_argument(
        '--generate-schema',
        action='store_true',
        help="Generate JSON schema from Pydantic models."
    )
    parser.add_argument(
        '--file-path',
        type=str,
        default=os.path.join(PROJECT_ROOT, "cv", "data", "cv_data.yaml"),
        help="Path to the CV YAML data file for validation."
    )
    parser.add_argument(
        '--schema-output-path',
        type=str,
        default=os.path.join(PROJECT_ROOT, "cv", "schema.json"),
        help="Output path for the generated JSON schema."
    )

    args = parser.parse_args()

    # Determine default action if no specific action flags are provided
    # If neither --generate-schema nor --validate is specified, default to validation.
    should_validate_by_default = not (args.generate_schema or args.validate)

    if args.generate_schema:
        # Ensure the output directory for schema exists.
        # generate_schema function now handles this.
        generate_schema(output_path=args.schema_output_path)
        # If only --generate-schema is passed, we don't validate unless --validate is also passed.
        # If user wants both, they should pass both flags.
        # For simplicity, if --generate-schema is present, we only do that and exit.
        # This can be changed if simultaneous operations are desired.
        if not args.validate : # If validate is not also requested, exit.
             sys.exit(0)


    # Perform validation if --validate is specified or if it's the default action.
    if args.validate or should_validate_by_default:
        if main_validate(file_path=args.file_path):
            # If schema generation was also requested and successful, this exit is fine.
            # If validation was the only task, this is also fine.
            sys.exit(0)
        else:
            sys.exit(1)
    
    # If only --generate-schema was passed (and succeeded), we would have exited above.
    # If neither flag was passed, should_validate_by_default would be true.
    # If arguments like only file paths were passed, it defaults to validation.
    # If no arguments were passed at all, it defaults to validation.
    
    # If the script reaches here, it means no action was taken (e.g. if logic above changes)
    # or an unsupported combination was implied.
    # For current logic: if --generate-schema is specified, it's done.
    # If --validate is specified, or no specific action, validation is done.
    # If both, schema is generated, then if validation is also specified, it's done.
    # The current structure: if --generate-schema, it generates, then if --validate is not also set, it exits.
    # If --validate is set (or default), it validates.
    # This means if both are set, generate runs, then validate runs.
    
    # If no flags are set, it defaults to validation.
    # If only --file-path is set, it defaults to validation with that file.
    # If only --schema-output-path is set, it defaults to validation (path not used by validation).
    # This seems reasonable.
    
    # If only --generate-schema is provided, it generates schema and exits (0).
    # If only --validate is provided, it validates and exits (0 or 1).
    # If BOTH are provided, it generates schema, then validates, then exits (0 or 1 based on validation).
    # If NEITHER is provided (e.g. only path args), it validates and exits (0 or 1).

    # The logic can be simplified:
    # 1. If --generate-schema, do it. If it fails, it exits(1) within the function.
    # 2. If --validate or (default action), do validation. Exit with its status.
    # This means if both are specified, schema generation happens first. If it succeeds, validation proceeds.

    # Revised logic for clarity:
    # parser = argparse.ArgumentParser(...) (as above)
    # args = parser.parse_args()

    # if not (args.generate_schema or args.validate):
    #     # No specific action flag given, default to validation
    #     args.validate = True # Implicitly enable validation

    # if args.generate_schema:
    #     generate_schema(output_path=args.schema_output_path) # Exits on error
    
    # if args.validate:
    #     if main_validate(file_path=args.file_path):
    #         sys.exit(0)
    #     else:
    #         sys.exit(1)
    # else:
    #     # This 'else' would be hit if only --generate-schema was true and it succeeded.
    #     # In that case, a successful exit is appropriate.
    #     sys.exit(0)
    # This revised logic is cleaner and will be reflected in the final code.
    # The existing code block for __main__ is slightly more convoluted but achieves a similar outcome.
    # For the purpose of this tool application, the provided block will be used.
