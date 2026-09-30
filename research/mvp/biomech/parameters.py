"""Canonical MVP parameter subset with evidence tags.

Source of truth remains C:\\Users\\Apoorv\\Downloads\\research\\parameters.json.
This module mirrors ONLY the values the MVP consumes, with status labels:
  EMPIRICAL / MODEL_DERIVED / PROVISIONAL / ASSUMPTION / UNKNOWN
per the task's model-status requirement.
"""
import math

MVP_PARAMETERS = [
    {"id": "P006", "parameter": "elbow_flexion_rom_aaos", "value": "0..145 deg",
     "si": "0..2.531 rad", "status": "EMPIRICAL",
     "notes": "ACTIVE_ROM general human. Anatomical hard stops."},
    {"id": "P017", "parameter": "elbow_feasible_rom_placeholder", "value": "30..130 deg",
     "si": "0.524..2.269 rad", "status": "ASSUMPTION",
     "notes": "ADL-derived placeholder. ARM_WRESTLING_MEASURED_ROM UNKNOWN."},
    {"id": "P026", "parameter": "biceps_long_head PCSA / Lopt",
     "value": "4.6 cm^2 / 23.2 cm", "si": "4.6e-4 m^2 / 0.232 m",
     "status": "EMPIRICAL", "notes": "Cadaveric n=10. Long head only."},
    {"id": "P027", "parameter": "triceps_long_head PCSA / Lopt",
     "value": "10.3 cm^2 / 45.4 cm", "si": "1.03e-3 m^2 / 0.454 m",
     "status": "EMPIRICAL",
     "notes": "Preserved as-written; 45.4 cm unusually long, flagged not corrected."},
    {"id": "P038", "parameter": "biceps peak flexion MA", "value": "4.7 cm",
     "si": "0.047 m", "status": "EMPIRICAL", "notes": "Peak anchor only."},
    {"id": "P041", "parameter": "triceps peak extension MA", "value": "2.3 cm",
     "si": "0.023 m", "status": "EMPIRICAL", "notes": "Peak anchor only."},
    {"id": "P052/P053", "parameter": "tau_a / tau_d", "value": "0.01..0.05 / 0.04 s",
     "si": "same", "status": "EMPIRICAL",
     "notes": "Defaults tau_a=0.03, tau_d=0.04."},
    {"id": "P054/P055", "parameter": "beta / q0", "value": "0.1..1.0 / 0.001..0.05",
     "si": "dimensionless", "status": "MODEL_DERIVED",
     "notes": "Zajac-form params. Defaults 0.5 / 0.01."},
    {"id": "P050", "parameter": "MA variation over ROM", "value": ">=30%",
     "si": "dimensionless", "status": "EMPIRICAL",
     "notes": "Mandates angle-dependent MA; forbids constants."},
    {"id": "P021", "parameter": "elbow restraint 100 Nm/deg",
     "value": "100 Nm/deg + 0.001745 Nms/deg", "si": "as-written",
     "status": "MODEL_DERIVED",
     "notes": "In DB as-written; NOT used directly (intractable). MVP k=15 Nm/rad PROVISIONAL."},
    {"id": "PROV-01", "parameter": "specific tension sigma", "value": "50 N/cm^2",
     "si": "5.0e5 N/m^2", "status": "PROVISIONAL",
     "notes": "NOT from corpus (absent #2). Gives Fmax bic=230 N, tri=515 N."},
    {"id": "PROV-02", "parameter": "FL width sigma_FL", "value": "0.30*Lopt",
     "si": "m", "status": "PROVISIONAL", "notes": "Corpus absent."},
    {"id": "PROV-03", "parameter": "v_max", "value": "10*Lopt/s",
     "si": "m/s", "status": "PROVISIONAL", "notes": "Corpus absent."},
    {"id": "PROV-04", "parameter": "theta_opt (L=Lopt angle)", "value": "90 deg",
     "si": "1.5708 rad", "status": "PROVISIONAL", "notes": "Corpus absent."},
    {"id": "PROV-05", "parameter": "MA shape (interp. layer)", "value": "sin-based C1",
     "si": "m", "status": "PROVISIONAL",
     "notes": "Anchors empirical; shape NOT validated."},
    {"id": "PROV-06", "parameter": "forearm+hand inertia about elbow",
     "value": "0.06 kg*m^2", "si": "same", "status": "PROVISIONAL",
     "notes": "NOT from corpus. Blocks VALIDATED claim."},
    {"id": "PROV-07", "parameter": "forearm mass / COM", "value": "1.5 kg / 0.18 m",
     "si": "same", "status": "PROVISIONAL", "notes": "Gravity torque only."},
    {"id": "PROV-08", "parameter": "joint damping c", "value": "0.3 Nms/rad",
     "si": "same", "status": "PROVISIONAL",
     "notes": "NOT P059 (different quantity)."},
    {"id": "PROV-09", "parameter": "restraint k/c (used)", "value": "15 Nm/rad / 1.0 Nms/rad",
     "si": "same", "status": "PROVISIONAL", "notes": "Stable surrogate for P021."},
    {"id": "UNK-01", "parameter": "ARM_WRESTLING_MEASURED_ROM", "value": "none",
     "si": "-", "status": "UNKNOWN", "notes": "No in-competition goniometry (C-18)."},
    {"id": "UNK-02", "parameter": "MA polynomial coefficients", "value": "none",
     "si": "-", "status": "UNKNOWN", "notes": "Must be fitted per F6 workflow (E-12)."},
    {"id": "UNK-03", "parameter": "fatigue rates / EMG patterns / friction / elite multipliers",
     "value": "none", "si": "-", "status": "UNKNOWN",
     "notes": "Explicitly NOT implemented (req. 10)."},
]


def parameter_status_table() -> str:
    lines = ["| ID | Parameter | Value | Status | Notes |",
             "|---|---|---|---|---|"]
    for p in MVP_PARAMETERS:
        lines.append(f"| {p['id']} | {p['parameter']} | {p['value']} | {p['status']} | {p['notes']} |")
    return "\n".join(lines)
