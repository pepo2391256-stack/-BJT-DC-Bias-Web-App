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
Ran 16 tests in 0.044s

OK
```

Breakdown: 12 engineering tests (reference values, independent nodal model,
preview approximation, Thevenin equivalent, cutoff, saturation, three
validation cases) and 4 Flask route tests (GET form, POST `/calculate`,
POST `/`, invalid input).

## 5. Why the illustrative image differs

Section 01B of the lab sheet shows an example result (`VB = 2.20 V`,
`VE = 1.50 V`, `VC = 8.70 V`, `VCE = 7.20 V`, `IB = 15.1 µA`,
`IC = 1.50 mA`) and states that the image is illustrative only. Those numbers
come from the simplified form

```
VB = VTH = VCC · R2 / (R1 + R2) = 2.164 V ≈ 2.2 V
IE = (VB − VBE) / RE       IC ≈ IE
```

which **ignores `RTH` and the base current**. The equations required in
Section 06 of the same sheet are

```
IB = (VTH − VBE) / (RTH + (β + 1)RE)
```

and that is what `dc_bias.py` implements, so the app reports
`VB = 1.942 V` and `IC = 1.230 mA` for the same components. The two differ by
about 11 % in `VB`, which is exactly the base-loading error the full model
removes.

This is verified independently by `IndependentModelTest`, which solves the
same circuit with nodal analysis instead of the module formulas and must
agree to numerical precision (`delta = 1e-9`), and by
`test_preview_approximation_ignores_base_loading`, which asserts
`VTH = 2.164 V` while the module result is `VB = 1.942 V`.

The app deliberately keeps the physics of Section 06 instead of being tuned to
match the picture, and the page states this next to the assumptions.

## 6. Known limitations

- Saturation values are produced by the forward-active equations and
  overestimate `IC`; the warning states this explicitly.
- Cutoff assumes an ideal open base (`IB = 0`) and ignores leakage.
- No temperature dependence, Early effect, or component tolerance is
  modelled.
