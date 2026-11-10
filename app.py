"""Flask entry point for the BJT DC bias web application.

The route layer only reads the form, calls the engineering module and
hands formatted strings to the Jinja template.
"""

from __future__ import annotations

from flask import Flask, render_template, request

from dc_bias import (
    REGION_LABELS,
    DcBiasResult,
    ValidationError,
    calculate_dc_bias,
)

app = Flask(__name__)

FORM_FIELDS = ("vcc", "r1", "r2", "rc", "re", "beta", "vbe")

DEFAULT_FORM = {
    "vcc": "12",
    "r1": "100",
    "r2": "22",
    "rc": "2.2",
    "re": "1",
    "beta": "100",
    "vbe": "0.7",
}


def _form_values() -> dict[str, str]:
    return {name: (request.form.get(name) or "").strip() for name in FORM_FIELDS}


def _display(result: DcBiasResult) -> dict[str, str]:
    """Format the SI values for the results table."""
    return {
        "vth": f"{result.vth:.3f} V",
        "rth": f"{result.rth / 1000.0:.2f} kΩ",
        "ib": f"{result.ib * 1e6:.2f} µA",
        "ic": f"{result.ic * 1e3:.3f} mA",
        "ie": f"{result.ie * 1e3:.3f} mA",
        "vb": f"{result.vb:.3f} V",
        "ve": f"{result.ve:.3f} V",
        "vc": f"{result.vc:.3f} V",
        "vce": f"{result.vce:.3f} V",
    }


def _render(
    form: dict[str, str],
    *,
    result: dict[str, str] | None = None,
    errors: list[str] | None = None,
    warning: str | None = None,
    region: str | None = None,
):
    return render_template(
        "index.html",
        form=form,
        result=result,
        errors=errors or [],
        warning=warning,
        region=region,
        region_label=REGION_LABELS.get(region) if region else None,
    )


@app.get("/")
def index():
    return _render(DEFAULT_FORM)


@app.post("/")
@app.post("/calculate")
def calculate():
    form = _form_values()
    try:
        result = calculate_dc_bias(**form)
    except ValidationError as exc:
        return _render(form, errors=[str(exc)]), 400

    return _render(
        form,
        result=_display(result),
        warning=result.warning,
        region=result.region,
    )


if __name__ == "__main__":
    app.run(debug=True)
