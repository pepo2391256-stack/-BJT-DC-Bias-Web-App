# Design Note — Lab 02 BJT DC Bias Web App

## Intent

Deliver a small but real Flask web application for the DC operating point
of an NPN BJT common-emitter amplifier with voltage-divider bias. The form
runs in the browser; all mathematics happen in Python on the server, so the
result can be tested and defended during the lab demo.

## Goals

- Accept `VCC`, `R1`, `R2`, `RC`, `RE`, `β`, `VBE` from a web form.
- Return `VB`, `VE`, `VC`, `VCE`, `IC` plus `IB`, `IE`, `VTH`, `RTH` with units.
- Validate input and warn when the forward-active model does not apply.
- Prove the behaviour with automated engineering and HTTP tests.

## Non-goals

- AC analysis, gain, Bode plots, transient simulation.
- SPICE/ngspice integration, load-line plots, multiple bias topologies.
- User accounts, database, deployment to a public server.

## Anti-goals

- Hard-coded answers in the HTML that never reach Python.
- Reporting a result outside the forward-active region as trustworthy.
- A web page that crashes on invalid input.

## Architecture

```
Browser form  →  Flask route (app.py)  →  dc_bias.py  →  Jinja template
```

| File | Responsibility |
|------|----------------|
| `app.py` | HTTP GET/POST, form reading, formatting for display |
| `dc_bias.py` | validation and DC bias mathematics, no Flask import |
| `templates/index.html` | form, warning banner, results table |
| `static/style.css` | layout and presentation |
| `tests/test_dc_bias.py` | engineering math and validation |
| `tests/test_web.py` | routes, rendering, error handling |

## Decisions

1. **One page, two routes.** `GET /` renders the form; `POST /calculate`
   (and `POST /` for convenience) returns the same template with results.
   Fewer pages means fewer things to break in a three-hour lab.
2. **Resistance inputs in kΩ.** This matches how the lab sheet lists
   component values. The conversion to ohms happens once, inside
   `dc_bias.py`.
3. **Region policy: show plus warn.** Outside the forward-active region the
   app still shows the values produced by the equations, but prepends a
   warning banner and a region badge. This keeps the mathematical behaviour
   visible while making the limitation explicit.
4. **Validation errors return HTTP 400** and re-render the form with the
   submitted values, so the user does not have to retype everything.
5. **No client-side mathematics.** JavaScript is limited to nothing; the
   page is server-rendered, which keeps the backend/demo story honest.

## Model boundary

- Cutoff is detected by `VTH ≤ VBE`; in that case the base current is taken
  as zero and the terminal voltages follow the passive network.
- Saturation is flagged when `VCE < 0.3 V`. The reported `IC` still comes
  from `β·IB`, so it is optimistic; the warning says so.

## Left to the builder

- Visual polish beyond the provided stylesheet.
- Additional example presets in the form.
- Any later lab features (bias templates, AC analysis).
