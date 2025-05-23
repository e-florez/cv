# CV Generation System

This directory contains a YAML-based multi-format CV generation system.
It allows maintaining a single source of truth in `data/cv_data.yaml` and generating multiple CV variants (e.g., Data Science, Academic, General) in PDF, HTML, and Markdown formats.

## Features (Planned & Implemented)

*   **Single Source of Truth**: CV content is managed in `data/cv_data.yaml`.
*   **YAML Validation**: Schema validation for `cv_data.yaml` is implemented in `validators.py` using Pydantic models defined in `schemas.py`. A JSON schema can be generated via `python cv/validators.py --generate-schema`.
*   **Multi-Variant Support**: Define different CV versions by selecting sections and content.
*   **Multi-Format Output**: Generate CVs in PDF, HTML, and Markdown.
*   **Templating Engine**: Uses Jinja2 for flexible template customization (`templates/`).
*   **Automated Build Process**: (Future) A script to orchestrate the generation of all formats and variants.
*   **CI/CD Integration**: (Future) GitHub Actions for automated builds and deployment.

## Directory Structure

*   `data/`: Contains the primary `cv_data.yaml` file.
*   `docs/`: (Future) For GitHub Pages deployment.
*   `generators/`: (Future) Python scripts for generating each output format (PDF, HTML, Markdown).
*   `output/`: Default directory for generated CV files. (Gitignored)
*   `schemas.py`: Pydantic models defining the YAML schema.
*   `templates/`: (Future) Jinja2 templates for each output format.
*   `tests/`: Pytest tests for the system.
*   `validators.py`: Script for validating `cv_data.yaml` and generating its JSON schema.
*   `validation.log`: Log file for validation results. (Gitignored)
*   `schema.json`: JSON representation of the YAML schema. (Gitignored)
*   `pyproject.toml`: Project metadata, dependencies, and tool configurations.
*   `.pre-commit-config.yaml`: Configuration for pre-commit hooks.

## Usage

### Validation

To validate the `cv_data.yaml` file:
```bash
python cv/validators.py --validate --file-path cv/data/cv_data.yaml
# Or, if running from the project root and cv/validators.py handles paths correctly:
# python cv/validators.py
```

To generate the JSON schema:
```bash
python cv/validators.py --generate-schema --schema-output-path cv/schema.json
# Or, if running from the project root:
# python cv/validators.py --generate-schema
```

## Development

Install dependencies (preferably in a virtual environment):
```bash
pip install -e .[dev] # Install in editable mode with dev dependencies from cv/pyproject.toml
```

Run tests:
```bash
pytest cv/tests/
```

Set up pre-commit hooks:
```bash
pre-commit install
```
