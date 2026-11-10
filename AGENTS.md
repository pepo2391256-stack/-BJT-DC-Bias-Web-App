# AGENTS.md

## Project

Flask web app for NPN BJT voltage-divider DC bias (ENG29 2121, Lab 02).

## Conventions

- Engineering mathematics live in `dc_bias.py` and must not import Flask.
- `app.py` handles HTTP only: read the form, call `calculate_dc_bias`,
  format values for the template.
- Templates must not contain physics equations or hard-coded results.
- Resistances are entered in kΩ and converted to ohms inside `dc_bias.py`.
- All displayed values need units.
- Validation errors are readable messages, never tracebacks.
- Results outside the forward-active region must carry a warning.
- Every behaviour change needs a test in `tests/`.
- Commits are made through GitHub Desktop, not the CLI.

## Commands

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows
python -m pip install -r requirements.txt
python -m flask --app app run --debug
python -m unittest discover -s tests -v
```
