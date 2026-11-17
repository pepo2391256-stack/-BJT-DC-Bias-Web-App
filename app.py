"""Flask entry point for the BJT DC bias web application.

The route layer only reads the form, picks the calculation function for the
selected circuit, and hands formatted strings to the Jinja template.
"""

from __future__ import annotations

from flask import Flask, render_template, request

from dc_bias import (
    MODE_LABELS,
    REGION_LABELS,
    DcBiasResult,
    ValidationError,
    calculate,
)

app = Flask(__name__)

DEFAULT_MODE = "divider"

#: Display metadata per input: (label HTML, unit).
FIELDS = {
    "vcc": ("V<sub>CC</sub>", "V"),
    "r1": ("R<sub>1</sub>", "kΩ"),
    "r2": ("R<sub>2</sub>", "kΩ"),
    "rb": ("R<sub>B</sub>", "kΩ"),
    "rc": ("R<sub>C</sub>", "kΩ"),
    "re": ("R<sub>E</sub>", "kΩ"),
    "beta": ("β (h<sub>FE</sub>)", "—"),
    "vbe": ("V<sub>BE</sub>", "V"),
}

#: Inputs each circuit needs, in form order.
MODE_FIELDS = {
    "fixed": ("vcc", "rb", "rc", "beta", "vbe"),
    "emitter": ("vcc", "rb", "rc", "re", "beta", "vbe"),
    "divider": ("vcc", "r1", "r2", "rc", "re", "beta", "vbe"),
}

DEFAULT_VALUES = {
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rb": "1000",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.7",
}


def _default_form(mode: str) -> dict[str, str]:
    return {name: DEFAULT_VALUES[name] for name in MODE_FIELDS[mode]}


def _form_values(mode: str) -> dict[str, str]:
    return {name: (request.form.get(name) or "").strip() for name in MODE_FIELDS[mode]}


def _display(result: DcBiasResult) -> dict[str, str | None]:
    """Format the SI values for the results table."""
    return {
        "vth": None if result.vth is None else f"{result.vth:.3f} V",
        "rth": None if result.rth is None else f"{result.rth / 1000.0:.2f} kΩ",
        "ib": f"{result.ib * 1e6:.2f} µA",
        "ic": f"{result.ic * 1e3:.3f} mA",
        "ie": f"{result.ie * 1e3:.3f} mA",
        "vb": f"{result.vb:.3f} V",
        "ve": f"{result.ve:.3f} V",
        "vc": f"{result.vc:.3f} V",
        "vce": f"{result.vce:.3f} V",
    }


def _render(
    mode: str,
    form: dict[str, str],
    *,
    result: dict[str, str | None] | None = None,
    errors: list[str] | None = None,
    warning: str | None = None,
    region: str | None = None,
):
    return render_template(
        "index.html",
        mode=mode,
        mode_label=MODE_LABELS.get(mode, MODE_LABELS[DEFAULT_MODE]),
        mode_labels=MODE_LABELS,
        fields=[(name, *FIELDS[name]) for name in MODE_FIELDS.get(mode, MODE_FIELDS[DEFAULT_MODE])],
        form=form,
        result=result,
        errors=errors or [],
        warning=warning,
        region=region,
        region_label=REGION_LABELS.get(region) if region else None,
    )


@app.get("/")
def index():
    mode = request.args.get("mode", DEFAULT_MODE)
    if mode not in MODE_FIELDS:
        mode = DEFAULT_MODE
    return _render(mode, _default_form(mode))


@app.post("/")
@app.post("/calculate")
def calculate_route():
    mode = (request.form.get("mode") or DEFAULT_MODE).strip()
    if mode not in MODE_FIELDS:
        return _render(
            DEFAULT_MODE,
            _default_form(DEFAULT_MODE),
            errors=[f"ไม่รู้จักโหมดที่เลือก: {mode}"],
        ), 400

    form = _form_values(mode)
    try:
        result = calculate(mode, **form)
    except ValidationError as exc:
        # No result block is rendered, so old numbers cannot pass for new input.
        return _render(mode, form, errors=[str(exc)]), 400

    return _render(
        mode,
        form,
        result=_display(result),
        warning=result.warning,
        region=result.region,
    )


if __name__ == "__main__":
    app.run(debug=True)
