# BJT DC Bias Web App

Flask web application for the DC operating point of an NPN BJT
common-emitter amplifier with three single-supply bias circuits:

| Mode | Inputs | Resistor placement |
|---|---|---|
| **Fixed Bias** | RB | RB from VCC to base, emitter grounded |
| **Emitter Bias** | RB, RE | RB from VCC to base, RE from emitter to ground |
| **Voltage Divider Bias** | R1, R2, RE | R1 from VCC to base, R2 from base to ground, RE from emitter to ground |

The browser shows the component form and the circuit for the selected mode;
the Python backend performs every calculation. Nothing is hard-coded in the
HTML and the templates contain no equations.

## Requirements

- Python 3.10 or newer (tested on Python 3.14)
- Git (only for version control)

## Install and run

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

python -m pip install -r requirements.txt
python -m flask --app app run --debug
```

Open <http://127.0.0.1:5000/> in a browser.

## Run the tests

```bash
python -m unittest discover -s tests -v
```

## Project layout

```
.
├── app.py                  # Flask routes (HTTP only)
├── dc_bias.py              # engineering calculations (no Flask)
├── templates/index.html    # form, schematic and results (Jinja)
├── static/style.css        # presentation
├── tests/
│   ├── test_dc_bias.py     # engineering unit tests (divider + regions)
│   ├── test_bias_modes.py  # fixed / emitter / dispatch tests
│   └── test_web.py         # Flask route tests
├── docs/
│   ├── design-note.md
│   ├── validation.md
│   ├── reflection.md
│   ├── acceptance-checklist.md
│   ├── test-log.txt
│   └── screenshot-*.jpeg
├── requirements.txt
└── README.md
```

## Screenshots

| State | File |
|---|---|
| Input form | `docs/screenshot-input.jpeg` |
| Forward-active result | `docs/screenshot-result.jpeg` |
| Validation error (`R1 = 0`) | `docs/screenshot-error.jpeg` |
| Saturation warning | `docs/screenshot-warning.jpeg` |

## Inputs and units

| Input | Unit | Used by |
|-------|------|---------|
| VCC   | V    | every mode |
| RC    | kΩ   | every mode |
| β (hFE) | —  | every mode |
| VBE   | V    | every mode |
| RB    | kΩ   | Fixed Bias, Emitter Bias |
| R1, R2 | kΩ  | Voltage Divider Bias |
| RE    | kΩ   | Emitter Bias, Voltage Divider Bias |

The form only shows the inputs the selected mode needs; resistances are
converted to ohms inside `dc_bias.py` before the calculation.

## Model

Forward-active approximation with constant β and constant VBE:

```
IB = (VCC − VBE) / RB                                  (fixed)
IB = (VCC − VBE) / (RB + (β + 1) RE)                    (emitter)
VTH = VCC R2 / (R1 + R2), RTH = R1 R2 / (R1 + R2)
IB = (VTH − VBE) / (RTH + (β + 1) RE)                   (divider)

IC  = β IB
IE  = (β + 1) IB
VE  = IE RE            (0 V for fixed bias)
VB  = VE + VBE
VC  = VCC − IC RC
VCE = VC − VE
```

## Validation and warnings

- `VCC`, `RB`, `R1`, `R2`, `RC`, `RE`, `β` must be numeric and greater than zero.
- `VBE` must be numeric and not negative.
- An unknown mode is a validation error; it never falls back to the divider.
- The base-drive voltage (`VCC` for fixed/emitter, `VTH` for divider) at or
  below `VBE` → **Cutoff**: `IB = IC = IE = 0`, `VE = 0`, `VC = VCE = VCC`,
  with a warning that the forward-active equations do not apply.
- `VCE < 0.3 V` → **Saturation** warning. The numbers are still shown, but
  they come from the forward-active equations and overestimate the real
  collector current.

## Limitations

This is a DC bias teaching model, not a SPICE simulator. It ignores the
Early effect, leakage, temperature drift, and parasitic elements. Results
outside the forward-active region are flagged and must not be treated as
accurate.

## Rubric mapping (10 points)

| เกณฑ์ | คะแนน | หลักฐานในโปรเจกต์ |
|---|---|---|
| Brainstorm + Planning มีขอบเขตสมเหตุสมผล | 1 | `docs/design-note.md`, `docs/implementation-plan.md` |
| Flask Web App เปิดผ่าน Browser รับ/แสดงผลได้ (multi-file/backend) | 3 | `app.py`, `dc_bias.py`, `templates/`, `static/`, `docs/screenshot-result.jpeg` |
| DC Bias ถูกหลักวงจร มีหน่วยและสมมติฐานชัดเจน | 2 | `docs/validation.md`, ตารางผล + `Calculation details` + `Model Assumptions & Region Limits` บนหน้าเว็บ |
| Automated Tests + Input Validation + Warning | 2 | `tests/` (16 เทสต์), `docs/test-log.txt`, `docs/screenshot-error.jpeg`, `docs/screenshot-warning.jpeg` |
| Review Code, GitHub Commit/Push, README, Reflection | 2 | `docs/code-review.md`, `docs/acceptance-checklist.md`, `docs/reflection.md`, commit history |

## Submission

Commit and push with GitHub Desktop. Paste the repository URL and the
latest commit SHA into Moodle together with a screenshot and the test log.
