"""Angle-dependent moment arms via monotone cubic (PCHIP, Fritsch-Carlson).

Self-contained (no scipy): guarantees monotonicity between control points, so
no high-degree-polynomial overshoot. Includes analytic segment integrals so
fiber length follows E-12: L(theta) = Lopt + integral_theta^theta_opt r(s) ds.

Tables load from data/r2_mtus.json. Per-point tags preserved; construction
warns when placeholder ('P') points are present (constitution rule 4).
"""
import math
import warnings
from bisect import bisect_left


def _hermite_antideriv(t, y0, y1, m0, m1, h):
    """Antiderivative of the cubic Hermite interpolant in t (times h folds externally)."""
    return (y0 * (t**4 / 2 - t**3 + t)
            + h * m0 * (t**4 / 4 - 2 * t**3 / 3 + t**2 / 2)
            + y1 * (-t**4 / 2 + t**3)
            + h * m1 * (t**4 / 4 - t**3 / 3))


class Pchip:
    def __init__(self, xs, ys):
        if len(xs) != len(ys) or len(xs) < 2:
            raise ValueError("need >=2 points")
        self.xs = [float(x) for x in xs]
        self.ys = [float(y) for y in ys]
        n = len(xs)
        h = [self.xs[i + 1] - self.xs[i] for i in range(n - 1)]
        if any(v <= 0 for v in h):
            raise ValueError("xs must be strictly increasing")
        delta = [(self.ys[i + 1] - self.ys[i]) / h[i] for i in range(n - 1)]
        m = [0.0] * n
        m[0] = delta[0]
        m[-1] = delta[-1]
        for i in range(1, n - 1):
            if delta[i - 1] * delta[i] <= 0:
                m[i] = 0.0
            else:
                w1 = 2.0 * h[i] + h[i - 1]
                w2 = h[i] + 2.0 * h[i - 1]
                m[i] = (w1 + w2) / (w1 / delta[i - 1] + w2 / delta[i])
        self._h, self._delta, self._m = h, delta, m

    def __call__(self, x):
        xs = self.xs
        if x <= xs[0]:
            i, t = 0, 0.0
        elif x >= xs[-1]:
            i, t = len(xs) - 2, 1.0
        else:
            i = min(max(bisect_left(xs, x) - 1, 0), len(xs) - 2)
            t = (x - xs[i]) / self._h[i]
        h00 = 2 * t**3 - 3 * t**2 + 1
        h10 = t**3 - 2 * t**2 + t
        h01 = -2 * t**3 + 3 * t**2
        h11 = t**3 - t**2
        return (h00 * self.ys[i] + h10 * self._h[i] * self._m[i]
                + h01 * self.ys[i + 1] + h11 * self._h[i] * self._m[i + 1])

    def integrate(self, a, b):
        """Definite integral of the interpolant from a to b (E-12 length law)."""
        if a == b:
            return 0.0
        lo, hi, sign = (a, b, 1.0) if a < b else (b, a, -1.0)
        total = 0.0
        xs = self.xs
        for i in range(len(xs) - 1):
            x0, x1 = xs[i], xs[i + 1]
            if x1 <= lo or x0 >= hi:
                continue
            s0, s1 = max(x0, lo), min(x1, hi)
            h = self._h[i]
            t0, t1 = (s0 - x0) / h, (s1 - x0) / h
            # antiderivative of the Hermite basis in t, times h
            total += h * (_hermite_antideriv(t1, self.ys[i], self.ys[i + 1],
                                             self._m[i], self._m[i + 1], h)
                          - _hermite_antideriv(t0, self.ys[i], self.ys[i + 1],
                                               self._m[i], self._m[i + 1], h))
        return sign * total


class MomentArmTable:
    """One muscle's MA(rad)->m with validity domain + extrapolation flag."""

    ndim = 1

    def __init__(self, name, points_deg_m_tag):
        self.name = name
        degs = [p[0] * math.pi / 180.0 for p in points_deg_m_tag]
        vals = [p[1] for p in points_deg_m_tag]
        self.tags = [p[2] for p in points_deg_m_tag]
        n_p = sum(1 for t in self.tags if t == "P")
        if n_p:
            warnings.warn(
                f"[MomentArmTable:{name}] {n_p}/{len(self.tags)} points are "
                "MODEL_DERIVED-PLACEHOLDER (only E points measured). Replace by "
                "digitizing Murray1995/Amis1979 curves.", UserWarning, stacklevel=2)
        self._pchip = Pchip(degs, vals)
        self.valid_min, self.valid_max = degs[0], degs[-1]

    def __call__(self, theta_rad):
        v = self._pchip(theta_rad)
        if not math.isfinite(v):
            raise ArithmeticError(f"non-finite MA at theta={theta_rad}")
        return v

    def is_extrapolated(self, theta_rad):
        return theta_rad < self.valid_min or theta_rad > self.valid_max

    def fiber_length(self, theta_rad, lopt_m, theta_opt_rad, role=+1.0):
        """E-12 muscle length law with correct extensors/flexors slopes.

        L(theta) = Lopt - role * integral_theta_opt^theta r(s) ds, where
        role = +1 flexor (torque +r*F), -1 extensor (torque -r*F).
        Flexor: dL/dTh = -r (longest at extension) and shortening
        velocity -dL/dt = +r*w. Extensor: dL/dTh = +r (longest in flexion)
        and shortening velocity -dL/dt = -r*w. Both match compute_muscle_state.
        (A role-blind law gets the extensor slope backwards: demonstrable
        first-principles error, fixed here.)
        """
        return lopt_m - role * self._pchip.integrate(theta_opt_rad, theta_rad)


class BilinearTable:
    """2D MA table over (elbow_rows x forearm_cols), meters. Deterministic
    bilinear interpolation (exact at nodes, C0 across cells — documented step
    below PCHIP smoothness; upgrade to bicubic only with denser data).
    Includes fixed-elbow Simpson integration along forearm (E-12, n=200)."""

    ndim = 2

    def __init__(self, name, rows_elbow_deg, cols_forearm_deg, values_m, tags=None):
        import math as _m
        self.name = name
        self.rows = [r * _m.pi / 180.0 for r in rows_elbow_deg]
        self.cols = [c * _m.pi / 180.0 for c in cols_forearm_deg]
        self.vals = [[float(v) for v in row] for row in values_m]
        n_p = sum(1 for row in (tags or []) for t in (row if isinstance(row, list) else [row])
                  if t == "P" or str(t).startswith("P-"))
        total = len(self.rows) * len(self.cols)
        if tags == "all P" or "M:envelope" in str(tags) or n_p:
            warnings.warn(
                f"[BilinearTable:{name}] placeholder-dominated 2D table "
                f"({tags if isinstance(tags, str) else f'{n_p}/{total} P'}). "
                "Shapes honor R2 directional facts only; magnitudes unresolved. "
                "Replace by digitizing Murray1995/Bremer/Haugstvedt.",
                UserWarning, stacklevel=2)

    def __call__(self, theta_e_rad, theta_f_rad):
        if len(self.rows) == 1 or len(self.cols) == 1:
            return self.vals[0][0]  # degenerate (zero-placeholder) table
        r = self.rows
        c = self.cols
        i = self._seg(r, theta_e_rad)
        j = self._seg(c, theta_f_rad)
        t = 0.0 if r[i + 1] == r[i] else (min(max(theta_e_rad, r[0]), r[-1]) - r[i]) / (r[i + 1] - r[i])
        u = 0.0 if c[j + 1] == c[j] else (min(max(theta_f_rad, c[0]), c[-1]) - c[j]) / (c[j + 1] - c[j])
        v = self.vals
        out = (v[i][j] * (1 - t) * (1 - u) + v[i + 1][j] * t * (1 - u)
               + v[i][j + 1] * (1 - t) * u + v[i + 1][j + 1] * t * u)
        if out != out:  # NaN guard
            raise ArithmeticError(f"non-finite 2D MA at ({theta_e_rad},{theta_f_rad})")
        return out

    @staticmethod
    def _seg(grid, x):
        if len(grid) == 1:
            return 0
        if x <= grid[0]:
            return 0
        if x >= grid[-1]:
            return len(grid) - 2
        return min(max(bisect_left(grid, x) - 1, 0), len(grid) - 2)

    def is_extrapolated(self, theta_e_rad, theta_f_rad):
        return not (self.rows[0] <= theta_e_rad <= self.rows[-1]
                    and self.cols[0] <= theta_f_rad <= self.cols[-1])

    def integrate_phi(self, a_phi, b_phi, theta_e_fixed, n=None):
        """Integral of r(theta_e_fixed, phi) dphi from a to b (E-12 forearm part).

        Exact cell-wise integration: along the forearm axis the surface is
        piecewise linear between grid lines, so the trapezoid per overlapping
        cell is exact — no fixed quadrature order, no error knob. (Previous
        fixed Simpson n=24 agreed to ~1e-9 but wasted table evaluations.)
        Out-of-domain segments replicate the clamping in __call__.
        """
        if a_phi == b_phi:
            return 0.0
        lo, hi, sign = (a_phi, b_phi, 1.0) if a_phi < b_phi else (b_phi, a_phi, -1.0)
        r, c = self.rows, self.cols
        v = self.vals
        if len(r) == 1 or len(c) == 1:
            return sign * v[0][0] * (hi - lo)
        i = self._seg(r, theta_e_fixed)
        t = 0.0 if r[i + 1] == r[i] else (min(max(theta_e_fixed, r[0]), r[-1]) - r[i]) / (r[i + 1] - r[i])
        w = [v[i][j] * (1.0 - t) + v[i + 1][j] * t for j in range(len(c))]
        total = 0.0
        # Clamped regions outside the grid (match __call__'s edge behaviour).
        if lo < c[0]:
            total += w[0] * (min(hi, c[0]) - lo)
        if hi > c[-1]:
            total += w[-1] * (hi - max(lo, c[-1]))
        for j in range(len(c) - 1):
            x0, x1 = max(lo, c[j]), min(hi, c[j + 1])
            if x1 <= x0:
                continue
            span = c[j + 1] - c[j]
            wa = w[j] + (w[j + 1] - w[j]) * (x0 - c[j]) / span
            wb = w[j] + (w[j + 1] - w[j]) * (x1 - c[j]) / span
            total += 0.5 * (wa + wb) * (x1 - x0)
        return sign * total


def load_elbow_tables(path):
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)["moment_arms_elbow"]
    return {"biceps": MomentArmTable("biceps_flexion", data["biceps_flexion"]["points_deg_m_tag"]),
            "triceps": MomentArmTable("triceps_extension", data["triceps_extension"]["points_deg_m_tag"])}


class ConstantMA:
    """Constant moment arm (magnitude, meters). MVP-only class with a KNOWN
    ~35% error budget (P051 wrist constant-MA finding — carried, not hidden).
    Upgrades to angle-dependent tables the moment data exist. Always valid
    (no extrapolation concept); integrate() is exact."""

    ndim = 0

    def __init__(self, name, value_m, tag):
        self.name = name
        self.value_m = float(value_m)
        self.tag = tag
        warnings.warn(f"[ConstantMA:{name}] constant MA ({tag}): KNOWN ~35% error class (P051).",
                      UserWarning, stacklevel=2)

    def __call__(self, *angles):
        return self.value_m

    def is_extrapolated(self, *angles):
        return False

    def integrate_length(self, a_rad, b_rad):
        return self.value_m * (b_rad - a_rad)


class WristPassiveTorque:
    """Conservative 1-DOF passive torque from Delp-anchored PCHIP (R3).

    potential(theta) = -integral_0^theta tau(s) ds, so tau = -dV/dtheta
    exactly (up to PCHIP quadrature, exact here via analytic segment integrals).
    """

    def __init__(self, name, points_deg_Nm_tag):
        self.name = name
        degs = [p[0] * math.pi / 180.0 for p in points_deg_Nm_tag]
        vals = [p[1] for p in points_deg_Nm_tag]
        self._pchip = Pchip(degs, vals)

    def __call__(self, theta_rad):
        return self._pchip(theta_rad)

    def potential(self, theta_rad):
        return -self._pchip.integrate(0.0, theta_rad)


def load_wrist_passive(path):
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {"fe": WristPassiveTorque("wrist_fe", data["wrist_fe_Nm"]["points_deg_Nm_tag"]),
            "rud": WristPassiveTorque("wrist_rud", data["wrist_rud_Nm"]["points_deg_Nm_tag"])}


def load_mtu_set(path):
    """Full MTU registry: {name: {roles, elbow_table|None, forearm_table|None, params}}.

    Warns per constitution rule 4: zero-Fmax placeholders, U-pennation, missing slack.
    """
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    elbow_src = data["moment_arms_elbow"]
    fore_src = data.get("moment_arms_forearm_2d", {})
    elbow_tables = {"biceps_long": ("biceps_flexion", elbow_src["biceps_flexion"]["points_deg_m_tag"]),
                    "triceps_long": ("triceps_extension", elbow_src["triceps_extension"]["points_deg_m_tag"]),
                    "pronator_teres": ("pt_flexion", elbow_src["pt_flexion"]["points_deg_m_tag"]),
                    "brachioradialis": ("brd_flexion", elbow_src["brd_flexion"]["points_deg_m_tag"]),
                    "fcr_flexor_carpi_radialis": ("fcr_flexion", elbow_src["fcr_flexion"]["points_deg_m_tag"]),
                    "fcu_flexor_carpi_ulnaris": ("fcu_flexion", elbow_src["fcu_flexion"]["points_deg_m_tag"])}
    fore_tables = {"biceps_long": "biceps_supination", "pronator_teres": "pt_pronation",
                   "pronator_quadratus": "pq_pronation", "supinator": "supinator_sup"}
    out = {}
    wrist_const = data.get("moment_arms_wrist_const", {})
    wrist_key = {"fcr_flexor_carpi_radialis": "fcr", "fcu_flexor_carpi_ulnaris": "fcu",
                 "ecr_extensor_carpi_radialis": "ecr", "ecu_extensor_carpi_ulnaris": "ecu"}
    for name in ("biceps_long", "triceps_long", "pronator_teres", "pronator_quadratus",
                 "supinator", "brachioradialis") + tuple(wrist_key):
        e = data[name]
        fmax = e["Fmax_N"]["value"]
        if fmax == 0.0:
            warnings.warn(f"[mtu:{name}] Fmax=0 ZERO-TORQUE placeholder ({e['Fmax_N']['tag']})",
                          UserWarning, stacklevel=2)
        if "slack_m" not in e:
            warnings.warn(f"[mtu:{name}] tendon slack absent from registry", UserWarning, stacklevel=2)
        et = MomentArmTable(elbow_tables[name][0], elbow_tables[name][1]) if name in elbow_tables else None
        ft = None
        if name in fore_tables:
            fs = fore_src[fore_tables[name]]
            ft = BilinearTable(fore_tables[name], fs["rows_elbow_deg"], fs["cols_forearm_deg"],
                               fs["values_m"], fs.get("tags", ""))
        roles = (e["roles"]["elbow"], e["roles"]["forearm"])
        out[name] = {"roles": roles, "elbow_table": et, "forearm_table": ft, "entry": e}
    return out


def wrist_tables_from_registry(path):
    """ConstantMA wrist tables from moment_arms_wrist_const (PROVISIONAL, P051 class)."""
    import json
    with open(path, encoding="utf-8") as f:
        wc = json.load(f)["moment_arms_wrist_const"]
    key = {"fcr_flexor_carpi_radialis": "fcr", "fcu_flexor_carpi_ulnaris": "fcu",
           "ecr_extensor_carpi_radialis": "ecr", "ecu_extensor_carpi_ulnaris": "ecu"}
    out = {}
    for name, k in key.items():
        out[name] = {"wfe": ConstantMA(k + "_fe", wc[k]["fe_m"][0], wc[k]["fe_m"][1]),
                     "wrud": ConstantMA(k + "_rud", wc[k]["rud_m"][0], wc[k]["rud_m"][1])}
    return out
