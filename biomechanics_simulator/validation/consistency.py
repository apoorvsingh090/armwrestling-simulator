"""Internal consistency checks: self-consistency only, no external data.

Each check returns {"status": PASS/FAIL/WARNING, "detail": str, "value": float}.
System-level energy/Newton coverage lives in the M4/M5 suites (cited, not
duplicated); here: fast exact checks + a short dissipative no-creation check.
"""
import math


def _result(status, detail, value=None):
    return {"status": status, "detail": detail, "value": value}


class ConsistencyChecker:
    def __init__(self, tol=1e-9):
        self.tol = tol

    def qp_balance(self, recruitment, torque_req, ma_state, baseline=0.1):
        a = recruitment.solve(torque_req, ma_state, baseline=baseline)
        worst = 0.0
        for d, t in torque_req.items():
            got = sum(recruitment.muscles[n]["Fmax"] * recruitment.muscles[n]["roles"].get(d, 0)
                      * ma_state.get(n, {}).get(d, 0.0) * a[n] for n in a)
            worst = max(worst, abs(got - t))
        ok = worst < 1e-6 * max(1.0, max(abs(t) for t in torque_req.values()))
        return _result("PASS" if ok else "FAIL", f"max torque residual {worst:.2e}", worst)

    def fatigue_equilibrium(self, muscle_factory, kf=0.4, kr=0.1, a=0.6):
        m = muscle_factory(kf=kf, kr=kr)
        for _ in range(40000):
            m.update_fatigue(a, 0.0, 0.001)
        expected = m.Fmax_N * kr / (kf * a * 0.8 + kr)
        err = abs(m.F_avail - expected) / expected
        return _result("PASS" if err < 1e-3 else "FAIL", f"rel err {err:.2e}", err)

    def passive_conservatism(self, passive_curve, angles_deg):
        worst = 0.0
        for deg in angles_deg:
            th = math.radians(deg)
            h = 1e-6
            dV = passive_curve.potential(th + h) - passive_curve.potential(th - h)
            worst = max(worst, abs(dV / (2 * h) + passive_curve(th)))
        scale = 1.0
        ok = worst < 1e-6 * scale
        return _result("PASS" if ok else "FAIL", f"max |dV/dth + tau| {worst:.2e}", worst)

    def newton_unit(self, contact_obj, Fn_A=100.0, Fn_B=80.0, v_rel=0.5, dt=0.001):
        con = contact_obj.compute(Fn_A, Fn_B, v_rel, dt)
        ok = con["Ft_on_A"] == -con["Ft_on_B"]
        return _result("PASS" if ok else "FAIL", "exact antisymmetry", abs(con["Ft_on_A"] + con["Ft_on_B"]))

    def dissipative_bound(self, match_factory, duration_s=0.5):
        """Zero-activation spinning grasp: total mechanical energy must not
        INCREASE (contact/bristle/restraint damping only dissipate; every
        conservative term — gravity, muscle elastic, wrist passive, LINEAR
        restraint springs — is budgeted exactly; damper terms correctly excluded
        since they can only remove energy)."""
        import math as _m
        m = match_factory()
        m.A.omega_f, m.B.omega_f = 2.0, -2.0
        hist = m.run_match(duration_s, lambda t: {}, lambda t: {}, 0.0, 0.0)
        E0N = _m.exp(1.0) - 1.0

        def elastic(sim, st):
            v = 0.0
            for name, mus in sim.muscles.items():
                L, _ = st[name]
                u = max(0.0, (L - mus.Lopt_m) / (mus.Lopt_m * (mus.passive_eps0 - 1.0)))
                v += mus.Fmax_N * mus.Lopt_m * (mus.passive_eps0 - 1.0) / E0N * (_m.exp(u) - u - 1.0)
            return v

        def spring(joint, q):
            if q < joint.feas_min:
                return 0.5 * joint.k * (joint.feas_min - q)**2
            if q > joint.feas_max:
                return 0.5 * joint.k * (q - joint.feas_max)**2
            return 0.0

        def total(s, sim, tag):
            st = s[tag]
            Iee, mm, dd, gg = sim.seg.inertia_kgm2, sim.seg.mass_kg, sim.seg.com_m, sim.g
            ke = (0.5 * Iee * st["omega"]**2 + 0.5 * sim.I_ff * st["omega_f"]**2
                  + 0.5 * sim._wrist_inertia_eff() * st["omega_wfe"]**2
                  + 0.5 * sim.I_wrud * st["omega_rud"]**2)
            pe = (-mm * gg * dd * _m.sin(st["theta"]) + elastic(sim, st["states"])
                  + sim.wp_fe.potential(st["phi_wfe"]) + sim.wp_rud.potential(st["phi_rud"])
                  + spring(sim.joint, st["theta"]) + spring(sim.f_joint, st["phi"])
                  + spring(sim.wfe_joint, st["phi_wfe"]) + spring(sim.wrud_joint, st["phi_rud"]))
            return ke + pe

        E = [total(s, m.A, "A") + total(s, m.B, "B") for s in hist]
        growth = max(E) - E[0]
        ok = growth <= 1e-6 * max(1.0, abs(E[0]))
        return _result("PASS" if ok else "FAIL", f"max energy growth {growth:.2e}", growth)

    def run_all(self, ctx):
        """ctx: dict with recruitment/torque_case/muscle_factory/passive_curves/
        contact_obj/match_factory. Returns {check: result}."""
        return {
            "qp_balance": self.qp_balance(ctx["recruitment"], ctx["torque_req"], ctx["ma_state"]),
            "fatigue_equilibrium": self.fatigue_equilibrium(ctx["muscle_factory"]),
            "passive_conservatism": self.passive_conservatism(ctx["passive_curve"], ctx["angles_deg"]),
            "newton_unit": self.newton_unit(ctx["contact_obj"]),
            "dissipative_bound": self.dissipative_bound(ctx["match_factory"]),
        }
