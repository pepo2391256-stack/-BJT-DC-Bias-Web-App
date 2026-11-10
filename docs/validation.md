# Validation — Lab 02 BJT DC Bias Web App

## 1. Independent hand calculation

Component values from the lab sheet:

`VCC = 12 V`, `R1 = 100 kΩ`, `R2 = 22 kΩ`, `RC = 2.2 kΩ`, `RE = 1 kΩ`,
`β = 100`, `VBE = 0.70 V`

| Step | Equation | Result |
|------|----------|--------|
| VTH | 12 × 22 / (100 + 22) | 2.164 V |
| RTH | 100 · 22 / (100 + 22) kΩ | 18.03 kΩ |
| IB | (2.164 − 0.70) / (18.03k + 101 · 1k) | 12.30 µA |
| IC | 100 · 12.30 µA | 1.230 mA |
| IE | 101 · 12.30 µA | 1.242 mA |
| VE | 1.242 mA · 1 kΩ | 1.242 V |
| VB | 1.242 + 0.70 | 1.942 V |
| VC | 12 − 1.230 mA · 2.2 kΩ | 9.294 V |
| VCE | 9.294 − 1.242 | 8.052 V |

Region: `VCE = 8.052 V > 0.3 V` → **Forward-Active**.

## 2. Application output

The values above are asserted in `tests/test_dc_bias.py`
(`ReferenceExampleTest`) and in `tests/test_web.py` (the rendered page must
contain `1.230` mA and `9.294` V). The tests therefore prove that the numbers
come from the Python backend, not from the template.

## 3. Boundary cases

| Case | Inputs | Expected |
|------|--------|----------|
| Cutoff | `R2 = 5 kΩ` → `VTH = 0.571 V ≤ VBE` | region `cutoff`, `IC = 0`, warning shown |
| Saturation | `VCC = 5 V`, `R1 = R2 = 10 kΩ`, `RC = 2.2 kΩ`, `RE = 1 kΩ` | `VCE ≈ −0.49 V < 0.3 V`, region `saturation`, warning shown |
| Invalid resistor | `R1 = 0` | HTTP 400, readable error, page still renders |
| Negative β | `β = −5` | HTTP 400, readable error |
| Non-numeric | `VCC = "abc"` | HTTP 400, readable error |

## 4. Test log

Command:

```bash
python -m unittest discover -s tests -v
```

Result:

```
Ran 14 tests in 0.067s

OK
```

Breakdown: 10 engineering tests (reference values, Thevenin equivalent,
cutoff, saturation, three validation cases) and 4 Flask route tests
(GET form, POST `/calculate`, POST `/`, invalid input).

## 5. Known limitations

- Saturation values are produced by the forward-active equations and
  overestimate `IC`; the warning states this explicitly.
- Cutoff assumes an ideal open base (`IB = 0`) and ignores leakage.
- No temperature dependence, Early effect, or component tolerance is
  modelled.
