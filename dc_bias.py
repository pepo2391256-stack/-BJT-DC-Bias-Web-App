"""NPN BJT voltage-divider DC bias calculations.

This module holds the engineering logic only. It has no Flask, HTML or
HTTP knowledge, so it can be unit-tested and reused on its own.

Model: forward-active approximation with a constant beta and a constant
VBE. Resistances are supplied in kOhm, voltages in volts.
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


class ValidationError(ValueError):
    """Raised when the supplied component values cannot be used."""


@dataclass(frozen=True)
class DcBiasResult:
    """DC operating point. Every field is in SI units."""

    vth: float
    rth: float
    ib: float
    ic: float
    ie: float
    vb: float
    ve: float
    vc: float
    vce: float
    region: str
    warning: str | None


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

    if vth <= vbe_v:
        # Not enough base drive: the transistor is cut off. With IB = 0 the
        # base sits at VTH, the emitter at ground and the collector at VCC.
        return DcBiasResult(
            vth=vth,
            rth=rth,
            ib=0.0,
            ic=0.0,
            ie=0.0,
            vb=vth,
            ve=0.0,
            vc=vcc_v,
            vce=vcc_v,
            region="cutoff",
            warning=(
                f"VTH = {vth:.3f} V น้อยกว่าหรือเท่ากับ VBE = {vbe_v:.2f} V "
                "ทรานซิสเตอร์อยู่ในช่วง Cutoff (IB ≈ 0) "
                "สมการ Forward-Active ใช้ไม่ได้"
            ),
        )

    ib = (vth - vbe_v) / (rth + (beta_value + 1.0) * re_ohm)
    ic = beta_value * ib
    ie = (beta_value + 1.0) * ib
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
        vth=vth,
        rth=rth,
        ib=ib,
        ic=ic,
        ie=ie,
        vb=vb,
        ve=ve,
        vc=vc,
        vce=vce,
        region=region,
        warning=warning,
    )
