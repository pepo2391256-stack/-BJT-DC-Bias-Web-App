"""NPN BJT DC bias calculations for three single-supply bias circuits.

This module holds the engineering logic only. It has no Flask, HTML or
HTTP knowledge, so it can be unit-tested and reused on its own.

Model: forward-active approximation with a constant beta and a constant
VBE. Resistances are supplied in kOhm, voltages in volts.

    Fixed bias   : IB = (VCC - VBE) / RB
    Emitter bias : IB = (VCC - VBE) / (RB + (beta + 1) RE)
    Divider bias : IB = (VTH - VBE) / (RTH + (beta + 1) RE)
                   VTH = VCC R2 / (R1 + R2), RTH = R1 R2 / (R1 + R2)

Then, for every circuit:

    IC = beta IB, IE = (beta + 1) IB, VE = IE RE (0 for fixed bias)
    VB = VE + VBE, VC = VCC - IC RC, VCE = VC - VE
"""

from __future__ import annotations

from dataclasses import dataclass

#: A VCE below this value means the forward-active model is not reliable.
VCE_SATURATION_LIMIT = 0.3  # V

REGION_LABELS = {
    "active": "Forward-Active",
    "cutoff": "Cutoff",
    "saturation": "Saturation",
}

MODE_LABELS = {
    "fixed": "Fixed Bias",
    "emitter": "Emitter Bias",
    "divider": "Voltage Divider Bias",
}


class ValidationError(ValueError):
    """Raised when the supplied component values cannot be used."""


@dataclass(frozen=True)
class DcBiasResult:
    """DC operating point. Every electrical field is in SI units."""

    mode: str
    ib: float
    ic: float
    ie: float
    vb: float
    ve: float
    vc: float
    vce: float
    region: str
    warning: str | None
    #: Only meaningful for the voltage-divider circuit.
    vth: float | None = None
    rth: float | None = None


def _number(value: object, label: str, *, allow_zero: bool = False) -> float:
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValidationError(f"{label} ต้องเป็นตัวเลข") from None
    if number != number or number in (float("inf"), float("-inf")):
        raise ValidationError(f"{label} ต้องเป็นจำนวนจริงที่มีค่าจำกัด")
    if number < 0 or (number == 0 and not allow_zero):
        raise ValidationError(f"{label} ต้องมากกว่า 0")
    return number


def _operating_point(
    *,
    mode: str,
    vcc_v: float,
    source_v: float,
    r_series_ohm: float,
    rc_ohm: float,
    re_ohm: float,
    beta: float,
    vbe_v: float,
    vth: float | None = None,
    rth: float | None = None,
) -> DcBiasResult:
    """Solve the operating point.

    ``source_v`` is VCC for fixed/emitter bias and VTH (Thevenin) for the
    divider circuit. ``r_series_ohm`` is RB, or RTH for the divider.
    """
    if source_v <= vbe_v:
        # Not enough base drive: the transistor is cut off. With IB = 0 the
        # base sits at the source voltage, the emitter at ground and the
        # collector at VCC.
        return DcBiasResult(
            mode=mode,
            ib=0.0,
            ic=0.0,
            ie=0.0,
            vb=source_v,
            ve=0.0,
            vc=vcc_v,
            vce=vcc_v,
            region="cutoff",
            warning=(
                f"แรงดันที่ฐานจากแหล่งจ่าย = {source_v:.3f} V น้อยกว่าหรือเท่ากับ "
                f"VBE = {vbe_v:.2f} V ทรานซิสเตอร์อยู่ในช่วง Cutoff (IB ≈ 0) "
                "สมการ Forward-Active ใช้ไม่ได้"
            ),
            vth=vth,
            rth=rth,
        )

    ib = (source_v - vbe_v) / (r_series_ohm + (beta + 1.0) * re_ohm)
    ic = beta * ib
    ie = (beta + 1.0) * ib
    ve = ie * re_ohm
    vb = ve + vbe_v
    vc = vcc_v - ic * rc_ohm
    vce = vc - ve

    if vce < VCE_SATURATION_LIMIT:
        region = "saturation"
        warning = (
            f"VCE = {vce:.3f} V ต่ำกว่า {VCE_SATURATION_LIMIT:.1f} V "
            "ทรานซิสเตอร์อิ่มตัว (Saturation) ค่า IC จากสมการสูงกว่าความเป็นจริง "
            "และสมการ Forward-Active ใช้ไม่ได้ ในวงจรจริง VCE ≈ 0.2 V"
        )
    else:
        region = "active"
        warning = None

    return DcBiasResult(
        mode=mode,
        ib=ib,
        ic=ic,
        ie=ie,
        vb=vb,
        ve=ve,
        vc=vc,
        vce=vce,
        region=region,
        warning=warning,
        vth=vth,
        rth=rth,
    )


def calculate_fixed_bias(
    *,
    vcc: object,
    rb: object,
    rc: object,
    beta: object,
    vbe: object,
) -> DcBiasResult:
    """Fixed bias: RB from VCC to base, emitter grounded (RE = 0)."""
    vcc_v = _number(vcc, "VCC")
    rb_ohm = _number(rb, "RB") * 1000.0
    rc_ohm = _number(rc, "RC") * 1000.0
    beta_value = _number(beta, "β")
    vbe_v = _number(vbe, "VBE", allow_zero=True)

    return _operating_point(
        mode="fixed",
        vcc_v=vcc_v,
        source_v=vcc_v,
        r_series_ohm=rb_ohm,
        rc_ohm=rc_ohm,
        re_ohm=0.0,
        beta=beta_value,
        vbe_v=vbe_v,
    )


def calculate_emitter_bias(
    *,
    vcc: object,
    rb: object,
    rc: object,
    re: object,
    beta: object,
    vbe: object,
) -> DcBiasResult:
    """Emitter bias, single supply: RB from VCC to base, RE to ground."""
    vcc_v = _number(vcc, "VCC")
    rb_ohm = _number(rb, "RB") * 1000.0
    rc_ohm = _number(rc, "RC") * 1000.0
    re_ohm = _number(re, "RE") * 1000.0
    beta_value = _number(beta, "β")
    vbe_v = _number(vbe, "VBE", allow_zero=True)

    return _operating_point(
        mode="emitter",
        vcc_v=vcc_v,
        source_v=vcc_v,
        r_series_ohm=rb_ohm,
        rc_ohm=rc_ohm,
        re_ohm=re_ohm,
        beta=beta_value,
        vbe_v=vbe_v,
    )


def calculate_dc_bias(
    *,
    vcc: object,
    r1: object,
    r2: object,
    rc: object,
    re: object,
    beta: object,
    vbe: object,
) -> DcBiasResult:
    """Return the DC operating point of a voltage-divider biased NPN BJT.

    ``vcc``, ``vbe`` are in volts; ``r1``, ``r2``, ``rc``, ``re`` are in
    kOhm; ``beta`` is a plain current ratio.
    """
    vcc_v = _number(vcc, "VCC")
    r1_ohm = _number(r1, "R1") * 1000.0
    r2_ohm = _number(r2, "R2") * 1000.0
    rc_ohm = _number(rc, "RC") * 1000.0
    re_ohm = _number(re, "RE") * 1000.0
    beta_value = _number(beta, "β")
    vbe_v = _number(vbe, "VBE", allow_zero=True)

    # Thevenin equivalent seen by the base.
    vth = vcc_v * r2_ohm / (r1_ohm + r2_ohm)
    rth = r1_ohm * r2_ohm / (r1_ohm + r2_ohm)

    return _operating_point(
        mode="divider",
        vcc_v=vcc_v,
        source_v=vth,
        r_series_ohm=rth,
        rc_ohm=rc_ohm,
        re_ohm=re_ohm,
        beta=beta_value,
        vbe_v=vbe_v,
        vth=vth,
        rth=rth,
    )


#: Mode key -> calculation function.
CALCULATORS = {
    "fixed": calculate_fixed_bias,
    "emitter": calculate_emitter_bias,
    "divider": calculate_dc_bias,
}


def calculate(mode: str, **values: object) -> DcBiasResult:
    """Dispatch to the calculation function of the selected circuit.

    An unknown mode is a validation error, never a silent divider fallback.
    """
    try:
        calculator = CALCULATORS[mode]
    except KeyError:
        raise ValidationError(
            "ไม่รู้จักโหมดที่เลือก กรุณาเลือก Fixed Bias, Emitter Bias "
            "หรือ Voltage Divider Bias"
        ) from None
    return calculator(**values)
