"""Integrated elbow dynamics (Part 3) + forearm 2-DOF extension (Milestone 2).

Sign conventions (verified in scripts/sign_check.py):
  th+ = flexion, w+ = flexion velocity, tau+ = flexion torque.
  Flexor (biceps):  torque +r*F,  velocity +r*w/cos(penn) (flexion shortens).
  Extensor (triceps): torque -r*F (magnitude-stored MA), velocity -r*w/cos(penn).

GRAVITY SIGN (spec asked to verify): implemented tau_grav = +m*g*d*cos(th).
Proof: the specified alternative tau=-m*g*d*cos(th) has dTau/dTh>0 on the whole
ROM, i.e. NO stable equilibrium in (0,145deg), making the required 10 s
conservative-pendulum energy test unimplementable. +cos is stable at 90deg with
consistent potential PE = -m*g*d*sin(th). Reference posture: elbow above
shoulder (upper arm vertical-up), forearm horizontal at extension, flexion
rotating downward. Part 2 main.py used the same sign: static path unchanged.
"""
import math
import warnings


class Simulation:
    def __init__(self, segment, joint, muscles, ma_tables, integrator,
                 roles=None, gravity_m_s2=9.81, theta_opt_rad=None,
                 forearm_joint=None, f_roles=None, mtu_tables=None,
                 inertia_ff=None, inertia_ef=0.0, forearm_damping=0.0,
                 phi_opt_rad=None,
                 wrist_fe_joint=None, wrist_rud_joint=None,
                 wfe_roles=None, wrud_roles=None,
                 inertia_wfe=None, inertia_wrud=None,
                 wrist_passive_fe=None, wrist_passive_rud=None,
                 hand=None, lever_wrist_grip_m=0.08, lever_elbow_wrist_m=0.28,
                 hand_offset_m=0.0, wrist_phi_opt_rad=None,
                 include_hand_dynamics=False, grip_model=None, table_planes=None,
                 elbow_rest_z=None, fatigue_enabled=False):
        self.seg = segment
        self.joint = joint
        self.muscles = dict(muscles)
        self.ma = dict(ma_tables)
        self.integrator = integrator
        self.roles = dict(roles) if roles else {"biceps_long": 1.0, "triceps_long": -1.0}
        self.g = float(gravity_m_s2)
        if theta_opt_rad is None:
            self.theta_opt = math.pi / 2
            warnings.warn("[Simulation] THETA_OPT=90deg PROVISIONAL (no corpus value)",
                          UserWarning, stacklevel=2)
        else:
            self.theta_opt = float(theta_opt_rad)
        # ---- 2-DOF forearm extension (additive; legacy 1-DOF path untouched) ----
        self.f_roles = dict(f_roles) if f_roles else {n: 0.0 for n in self.muscles}
        self.wfe_roles = dict(wfe_roles) if wfe_roles else {n: 0.0 for n in self.muscles}
        self.wrud_roles = dict(wrud_roles) if wrud_roles else {n: 0.0 for n in self.muscles}
        self.mt = {}
        for name in self.muscles:
            self.mt[name] = {"elbow": ma_tables.get(name), "forearm": None,
                             "wfe": None, "wrud": None}
        for name, entry in (mtu_tables or {}).items():
            cur = self.mt.setdefault(name, {"elbow": None, "forearm": None,
                                            "wfe": None, "wrud": None})
            cur.update(entry)
        self.f_joint = forearm_joint
        self.phi = 0.0
        self.omega_f = 0.0
        self.I_ff = None if inertia_ff is None else float(inertia_ff)
        self.I_ef = float(inertia_ef)
        self.fc = float(forearm_damping)
        if phi_opt_rad is None:
            self.phi_opt = 0.0
            if forearm_joint is not None:
                warnings.warn("[Simulation] PHI_OPT=neutral UNKNOWN (no corpus value)",
                              UserWarning, stacklevel=2)
        else:
            self.phi_opt = float(phi_opt_rad)
        if forearm_joint is not None:
            warnings.warn("[Simulation] INERTIA COUPLING: forearm rotation changes "
                          "elbow-axis inertia. Treated as constant for MVP. Flag for Milestone 3.",
                          UserWarning, stacklevel=2)
            if self.I_ff is None:
                raise ValueError("inertia_ff is UNKNOWN: pass explicit value (no default manufactured)")
        # ---- 4-DOF wrist extension (additive; 1-DOF and 2-DOF paths untouched) ----
        self.wfe_joint = wrist_fe_joint
        self.wrud_joint = wrist_rud_joint
        self.wrist_active = wrist_fe_joint is not None or wrist_rud_joint is not None
        self.I_wfe = None if inertia_wfe is None else float(inertia_wfe)
        self.I_wrud = None if inertia_wrud is None else float(inertia_wrud)
        self.wp_fe = wrist_passive_fe
        self.wp_rud = wrist_passive_rud
        self.hand = hand
        self.hand_dyn = bool(include_hand_dynamics)
        self.grip_model = grip_model
        self.fatigue_enabled = bool(fatigue_enabled)
        if self.fatigue_enabled:
            warnings.warn("[Simulation] fatigue ON: F_avail integrated per step (PROVISIONAL kf/kr); "
                          "Fmax_N baselines never mutated.", UserWarning, stacklevel=2)
        self.table = dict(table_planes) if table_planes else {}
        self.elbow_rest_z = elbow_rest_z
        if self.hand_dyn:
            if hand is None:
                raise ValueError("include_hand_dynamics needs an attached hand segment")
            warnings.warn("[Simulation] HAND DYNAMICS ON: mass/COM PROVISIONAL (r3 JSON); "
                          "hand gravity INCLUDED via 2-link extension of the locked gravity form; "
                          "wrist inertia += I_hand + m*grip_lever^2 (documented composition).",
                          UserWarning, stacklevel=2)
        self.lever_wg = float(lever_wrist_grip_m)
        self.lever_ew = float(lever_elbow_wrist_m)
        self.hand_offset = float(hand_offset_m)
        if wrist_phi_opt_rad is None:
            self.w_phi_opt = 0.0
            if self.wrist_active:
                warnings.warn("[Simulation] WRIST_PHI_OPT=neutral UNKNOWN (no corpus value)",
                              UserWarning, stacklevel=2)
        else:
            self.w_phi_opt = float(wrist_phi_opt_rad)
        if self.wrist_active:
            warnings.warn("[Simulation] WRIST OBLIQUE AXIS: 26.6deg oblique per R1; modeled orthogonal.",
                          UserWarning, stacklevel=2)
            warnings.warn("[Simulation] INERTIA COUPLING: 4-DOF inertia treated as DIAGONAL; "
                          "cross-coupling neglected. Flag for Milestone 4.",
                          UserWarning, stacklevel=2)
            warnings.warn("[Simulation] lever_wrist_grip PROVISIONAL ~0.08m; lever_elbow_wrist "
                          "UNKNOWN placeholder; hand_offset=0 zeroes forearm external torque.",
                          UserWarning, stacklevel=2)
            if wrist_fe_joint is None or wrist_rud_joint is None:
                raise ValueError("wrist mode needs BOTH fe and rud joints (coupled 2-DOF object)")
            if self.I_wfe is None or self.I_wrud is None:
                raise ValueError("inertia_wfe/wrud UNKNOWN: pass explicit values (no defaults manufactured)")
        self.phi_wfe = 0.0
        self.omega_wfe = 0.0
        self.phi_rud = 0.0
        self.omega_rud = 0.0

    @staticmethod
    def _table_r(table, theta_e, theta_f):
        if table is None:
            return 0.0
        nd = getattr(table, "ndim", 1)
        if nd == 0:
            return table()
        if nd == 1:
            return table(theta_e)
        return table(theta_e, theta_f)

    def _wrist_len(self, table, role, phi, theta_e):
        if table is None or role == 0.0:
            return 0.0
        nd = getattr(table, "ndim", 0)
        if nd == 0:
            return -role * table.integrate_length(self.w_phi_opt, phi)
        if nd == 1:
            return table.fiber_length(phi, 0.0, self.w_phi_opt, role=role)
        return -role * table.integrate_phi(self.w_phi_opt, phi, theta_e)

    def compute_muscle_state(self, theta, omega, theta_f=0.0, omega_f=0.0,
                             theta_wfe=0.0, omega_wfe=0.0,
                             theta_rud=0.0, omega_rud=0.0):
        out = {}
        arms = {}
        for name, mus in self.muscles.items():
            e = self.mt[name]
            re_ = self.roles.get(name, 0.0)
            rf = self.f_roles.get(name, 0.0)
            rwfe = self.wfe_roles.get(name, 0.0)
            rwrud = self.wrud_roles.get(name, 0.0)
            r_e = self._table_r(e["elbow"], theta, theta_f)
            r_f = self._table_r(e["forearm"], theta, theta_f)
            r_w = self._table_r(e["wfe"], theta_wfe, theta_rud)
            r_u = self._table_r(e["wrud"], theta_wfe, theta_rud)
            arms[name] = (r_e, r_f, r_w, r_u)
            v = (re_ * r_e * omega + rf * r_f * omega_f
                 + rwfe * r_w * omega_wfe + rwrud * r_u * omega_rud) / math.cos(mus.pennation_rad)
            L = mus.Lopt_m
            if e["elbow"] is not None:
                L += e["elbow"].fiber_length(theta, 0.0, self.theta_opt, role=re_)
            if e["forearm"] is not None:
                L += -rf * e["forearm"].integrate_phi(self.phi_opt, theta_f, theta)
            L += self._wrist_len(e["wfe"], rwfe, theta_wfe, theta)
            L += self._wrist_len(e["wrud"], rwrud, theta_rud, theta)
            out[name] = (L, v)
        # compute_torques() reuses these — they were being recomputed there.
        self._arms_cache = arms
        return out

    def _forearm_restraint(self, phi, omega_f):
        if self.f_joint is None:
            return 0.0
        return self.f_joint.restraint_torque(phi, omega_f)

    def _hand_gravity(self, theta, theta_wfe):
        if not (self.hand_dyn and self.hand is not None):
            return 0.0, 0.0
        m = self.hand.mass_kg
        te = (m * self.g * (self.lever_ew * math.cos(theta)
                            + self.lever_wg * math.cos(theta + theta_wfe)))
        tw = m * self.g * self.lever_wg * math.cos(theta + theta_wfe)
        return te, tw

    def _wrist_inertia_eff(self):
        if self.hand_dyn and self.hand is not None:
            return self.I_wfe + self.hand.inertia_kgm2 + self.hand.mass_kg * self.lever_wg**2
        return self.I_wfe

    def _update_fatigue(self, activations, states):
        """Per-step capacity integration (forces already used start-of-step
        F_avail). Disabled by default: legacy paths byte-identical."""
        if not self.fatigue_enabled:
            return
        dt = self.integrator.dt
        for name, mus in self.muscles.items():
            L, v = states[name]
            mus.update_fatigue(activations.get(name, 0.0), v, dt)

    def fatigue_snapshot(self):
        return {n: m.fatigue_fraction for n, m in self.muscles.items()}

    def reset_fatigue(self):
        for mus in self.muscles.values():
            mus.reset_fatigue()

    def pad_state(self, z=None):
        """Elbow-pad unilateral query (DEGENERATE in fixed-base MVP: the elbow
        never moves, so penetration is 0 by construction; interface reserved
        for a mobile base in M7+)."""
        zz = self.elbow_rest_z if z is None else z
        if zz is None or "elbow_pad" not in self.table:
            raise ValueError("pad_state needs elbow_rest_z + loaded table planes (fixed-base MVP: pass explicitly)")
        q = self.table["elbow_pad"].query([0.0, 0.0, zz], [0.0, 0.0, 0.0])
        return {**q, "degenerate_fixed_base": True}

    def pad_preload(self):
        """Static arm-weight estimate on the pad (REPORTED ONLY, never fed back:
        closing the loop needs elbow joint-force inverse dynamics, absent)."""
        m = self.seg.mass_kg + (self.hand.mass_kg if (self.hand_dyn and self.hand) else 0.0)
        return {"preload_N": m * self.g, "integrated": False}

    def lift_state(self, elbow_z=None):
        """Elbow-lift detector input (M6): True iff explicit z above rest height.
        Defaults to fixed-base rest (False, documented vacuity — no vertical
        elbow DOF exists). Enforcement is referee/game logic, NOT physics."""
        if elbow_z is None:
            return {"lift": False, "reason": "fixed base: no vertical elbow state"}
        rest = self.elbow_rest_z
        if rest is None:
            raise ValueError("lift_state needs elbow_rest_z (fixed-base MVP: pass explicitly)")
        return {"lift": bool(elbow_z > rest), "reason": "explicit kinematics"}

    def compute_torques(self, theta, omega, activations, external_force_N=0.0,
                        theta_f=0.0, omega_f=0.0,
                        theta_wfe=0.0, omega_wfe=0.0,
                        theta_rud=0.0, omega_rud=0.0,
                        contact=None, grip_activation=0.0, tangential_demand_N=0.0):
        states = self.compute_muscle_state(theta, omega, theta_f, omega_f,
                                           theta_wfe, omega_wfe, theta_rud, omega_rud)
        tau_m, tau_mf, tau_mw, tau_mu, forces = 0.0, 0.0, 0.0, 0.0, {}
        arms = self._arms_cache
        for name, mus in self.muscles.items():
            L, v = states[name]
            F = mus.force(activations.get(name, 0.0), L, v)
            forces[name] = F
            re_ = self.roles.get(name, 0.0)
            rf = self.f_roles.get(name, 0.0)
            rwfe = self.wfe_roles.get(name, 0.0)
            rwrud = self.wrud_roles.get(name, 0.0)
            r_e, r_f, r_w, r_u = arms[name]
            tau_m += re_ * r_e * F
            tau_mf += rf * r_f * F
            tau_mw += rwfe * r_w * F
            tau_mu += rwrud * r_u * F
        tau_g = self.seg.mass_kg * self.g * self.seg.com_m * math.cos(theta)
        tau_p = self.joint.restraint_torque(theta, omega)
        if self.hand is None:
            tau_e = -external_force_N * self.seg.wrist_m
            tau_we, tau_ue, tau_ee = 0.0, 0.0, tau_e
        else:
            tau_we = -external_force_N * self.lever_wg
            tau_ue = -external_force_N * self.hand_offset
            tau_ee = -external_force_N * (self.lever_ew + self.lever_wg)
        tau_pf = self._forearm_restraint(theta_f, omega_f)
        tau_fd = -self.fc * omega_f
        tau_wfe_p = self.wp_fe(theta_wfe) if self.wp_fe is not None else 0.0
        tau_rud_p = self.wp_rud(theta_rud) if self.wp_rud is not None else 0.0
        te_h, tw_h = self._hand_gravity(theta, theta_wfe)
        c_ee = c_we = c_ru = c_roll = 0.0
        if contact is not None:
            if self.hand is None:
                raise ValueError("contact forces need an attached hand (grip point undefined)")
            # Hand-frame force components (documented small-angle-exact projection;
            # full chain kinematics deferred past M5). Normal along hand axis: no planar torque.
            # Ft_roll (M5 grasp shear): effective roll arm = grip lever, the SAME lever
            # as the lateral_hand_position map -> power-consistent pair (F*v = tau*omega).
            c_we = contact.get("Ft_flex", 0.0) * self.lever_wg
            c_ee = contact.get("Ft_flex", 0.0) * (self.lever_ew + self.lever_wg * math.cos(theta_wfe))
            c_ru = contact.get("Ft_lat", 0.0) * self.lever_wg
            c_roll = contact.get("Ft_roll", 0.0) * self.lever_wg
        grip_Fn, grip_slipped = 0.0, None
        if self.grip_model is not None:
            grip_Fn = self.grip_model.normal_force(grip_activation)
            grip_slipped = self.grip_model.slip_state(grip_activation, tangential_demand_N)["slipped"]
        return {"tau_muscle": tau_m, "tau_gravity": tau_g, "tau_passive": tau_p,
                "tau_external": tau_ee, "tau_hand_gravity_elbow": te_h,
                "tau_contact_elbow": c_ee,
                "net": tau_m + tau_g + tau_p + tau_ee + te_h + c_ee,
                "tau_forearm_muscle": tau_mf, "tau_forearm_passive": tau_pf,
                "tau_forearm_damping": tau_fd, "tau_contact_roll": c_roll,
                "tau_forearm": tau_mf + tau_pf + tau_fd + c_roll,
                "tau_wrist_fe_muscle": tau_mw, "tau_wrist_fe_passive": tau_wfe_p,
                "tau_wrist_fe_external": tau_we, "tau_hand_gravity_wrist": tw_h,
                "tau_contact_wrist": c_we,
                "tau_wrist_fe": tau_mw + tau_wfe_p + tau_we + tw_h + c_we,
                "tau_wrist_rud_muscle": tau_mu, "tau_wrist_rud_passive": tau_rud_p,
                "tau_wrist_rud_external": tau_ue,
                "tau_contact_rud": c_ru,
                "tau_wrist_rud": tau_mu + tau_rud_p + tau_ue + c_ru,
                "grip_Fn": grip_Fn, "grip_slipped": grip_slipped,
                "forces": forces, "states": states}

    def step(self, activations, external_force_N=0.0, grip_activation=0.0,
             tangential_demand_N=0.0, contact=None):
        th, om = self.seg.theta, self.seg.omega
        if self.f_joint is None and not self.wrist_active:
            rep = self.compute_torques(th, om, activations, external_force_N,
                                       grip_activation=grip_activation,
                                       tangential_demand_N=tangential_demand_N,
                                       contact=contact)
            self._update_fatigue(activations, rep["states"])
            alpha = rep["net"] / self.seg.inertia_kgm2
            th2, om2 = self.integrator.step_theta(th, om, alpha)
            th2 = self.joint.clamp(th2)
            om2 = self.joint.project_velocity(th2, om2)
            self.seg.theta, self.seg.omega = th2, om2
            return {"theta": th2, "omega": om2, "alpha": alpha,
                    "fatigue": self.fatigue_snapshot(), **rep}
        ph, omf = self.phi, self.omega_f
        pw, omw = (self.phi_wfe, self.omega_wfe) if self.wrist_active else (0.0, 0.0)
        pr, omr = (self.phi_rud, self.omega_rud) if self.wrist_active else (0.0, 0.0)
        rep = self.compute_torques(th, om, activations, external_force_N,
                                   ph, omf, pw, omw, pr, omr,
                                   contact=contact, grip_activation=grip_activation,
                                   tangential_demand_N=tangential_demand_N)
        self._update_fatigue(activations, rep["states"])
        al_f = 0.0
        if self.f_joint is None:
            Iee, al_e = self.seg.inertia_kgm2, rep["net"] / self.seg.inertia_kgm2
        else:
            Iee, Iff, Ief = self.seg.inertia_kgm2, self.I_ff, self.I_ef
            det = Iee * Iff - Ief * Ief
            if det <= 0:
                raise ArithmeticError(f"non-positive-definite inertia (det={det})")
            al_e = (rep["net"] * Iff - Ief * rep["tau_forearm"]) / det
            al_f = (rep["tau_forearm"] * Iee - Ief * rep["net"]) / det
            ph2, omf2 = self.integrator.step_theta(ph, omf, al_f)
            ph2 = self.f_joint.clamp(ph2)
            omf2 = self.f_joint.project_velocity(ph2, omf2)
            self.phi, self.omega_f = ph2, omf2
            rep = {**rep, "alpha_f": al_f}
        th2, om2 = self.integrator.step_theta(th, om, al_e)
        th2 = self.joint.clamp(th2)
        om2 = self.joint.project_velocity(th2, om2)
        self.seg.theta, self.seg.omega = th2, om2
        out = {"theta": th2, "omega": om2, "alpha": al_e,
                 "phi": self.phi, "omega_f": self.omega_f,
                 "fatigue": self.fatigue_snapshot(), **rep}
        if self.f_joint is not None and "alpha_f" not in out:
            out["alpha_f"] = al_f
        if self.wrist_active:
            al_w = rep["tau_wrist_fe"] / self._wrist_inertia_eff()
            al_r = rep["tau_wrist_rud"] / self.I_wrud
            pw2, omw2 = self.integrator.step_theta(pw, omw, al_w)
            pr2, omr2 = self.integrator.step_theta(pr, omr, al_r)
            pw2 = self.wfe_joint.clamp(pw2)
            omw2 = self.wfe_joint.project_velocity(pw2, omw2)
            pr2 = self.wrud_joint.clamp(pr2)
            omr2 = self.wrud_joint.project_velocity(pr2, omr2)
            self.phi_wfe, self.omega_wfe = pw2, omw2
            self.phi_rud, self.omega_rud = pr2, omr2
            out.update({"phi_wfe": pw2, "omega_wfe": omw2, "alpha_wfe": al_w,
                        "phi_rud": pr2, "omega_rud": omr2, "alpha_rud": al_r})
        else:
            out.update({"phi": getattr(self, "phi", 0.0), "omega_f": getattr(self, "omega_f", 0.0)})
            if self.f_joint is not None:
                out["alpha_f"] = al_f
        return out

    def run(self, duration_s, activation_schedule, external_schedule=None,
            grip_schedule=None, demand_schedule=None, contact_schedule=None):
        dt = self.integrator.dt
        n = int(round(duration_s / dt))
        hist = []
        for i in range(n + 1):
            t = i * dt
            acts = activation_schedule(t)
            fext = external_schedule(t) if external_schedule else 0.0
            grip = grip_schedule(t) if grip_schedule else 0.0
            dem = demand_schedule(t) if demand_schedule else 0.0
            con = contact_schedule(t) if contact_schedule else None
            st = self.step(acts, fext, grip_activation=grip,
                           tangential_demand_N=dem, contact=con)
            hist.append({"t": t, **st})
        return hist
