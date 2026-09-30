"""Minimum-effort muscle recruitment (exact small-set QP, M9).

min ||a - a0||^2 s.t. M a = tau, 0 <= a <= 1, with M[d,i] = Fmax_i * r_i(d)
(signed via roles). Solved by active-set iterations over box constraints with
exact affine projections (tiny Gaussian elimination, m<=4 DOFs). Deterministic,
no iteration tuning, no learning.

Baseline a0 (default 0.1) yields low-level co-contraction at tau~=0 and cancels
Fmax asymmetry (the M7 0.5/0.5 drift fix). Zero-Fmax/zero-MA muscles are
EXCLUDED (reported in skipped, never crash). Infeasible rows (demand with no
capable muscle) are DROPPED with warning (documented best-effort).

Flag: minimum-effort criterion for MVP; fatigue/joint-load criteria deferred.
"""
import warnings


def _solve_small(A, b):
    """Gaussian elimination, n<=4, partial pivot. Pure-python, deterministic."""
    n = len(A)
    M = [list(A[i]) + [b[i]] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12:
            M[c][c] = 1e-12 if M[c][c] >= 0 else -1e-12
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


class MuscleRecruitment:
    def __init__(self, muscles, dofs):
        """muscles: {name: {"Fmax": N, "roles": {dof: +1/-1/0}}}.
        dofs: ordered list."""
        self.muscles = dict(muscles)
        self.dofs = list(dofs)
        self.skipped = {}
        self.last_residual = 0.0

    def solve(self, torque_req, ma_state, baseline=0.1):
        """torque_req: {dof: Nm}. ma_state: {name: {dof: r(m)}}.
        Returns {name: activation in [0,1]}."""
        names = [n for n in self.muscles if self.muscles[n]["Fmax"] > 0]
        self.skipped = {n: "zero-Fmax" for n in self.muscles if self.muscles[n]["Fmax"] <= 0}
        rows, taus = [], []
        for d in self.dofs:
            row = [self.muscles[n]["Fmax"] * self.muscles[n]["roles"].get(d, 0)
                   * ma_state.get(n, {}).get(d, 0.0) for n in names]
            if all(abs(v) < 1e-15 for v in row):
                if abs(torque_req.get(d, 0.0)) > 1e-12:
                    warnings.warn(f"[Recruitment] DOF '{d}' demand {torque_req[d]} has no capable muscle: dropped.",
                                  UserWarning, stacklevel=2)
                continue
            rows.append(row)
            taus.append(torque_req.get(d, 0.0))
        a = {n: 0.0 for n in self.muscles}
        if not rows:
            self.last_residual = 0.0
            return {**a, **{n: baseline for n in names}}
        m = len(rows)
        x = [baseline] * len(names)
        clamped = [False] * len(names)
        for _ in range(50):
            r = [t - sum(rows[d][i] * x[i] for i in range(len(names))) for d, t in enumerate(taus)]
            if max(abs(v) for v in r) < 1e-9:
                break
            free = [i for i in range(len(names)) if not clamped[i]]
            if not free:
                break
            G = [[sum(rows[d][i] * rows[d][j] for d in range(m)) + (1e-9 if i == j else 0.0)
                  for j in free] for i in free]
            try:
                lam = _solve_small(G, [sum(rows[d][i] * r[d] for d in range(m)) for i in free])
            except ArithmeticError:
                break
            step = [0.0] * len(names)
            for k, i in enumerate(free):
                step[i] = lam[k]
            alpha = 1.0
            for i in free:
                if step[i] > 0:
                    alpha = min(alpha, (1.0 - x[i]) / step[i] if step[i] > 1e-15 else 1.0)
                elif step[i] < 0:
                    alpha = min(alpha, (0.0 - x[i]) / step[i] if step[i] < -1e-15 else 1.0)
            alpha = max(0.0, min(1.0, alpha))
            for i in free:
                x[i] += alpha * step[i]
                x[i] = min(1.0, max(0.0, x[i]))
            for i in free:
                if x[i] <= 0.0 or x[i] >= 1.0:
                    clamped[i] = True
        for i, n in enumerate(names):
            a[n] = min(1.0, max(0.0, x[i]))
        full_r = [t - sum(rows[d][i] * a[names[i]] for i in range(len(names)))
                  for d, t in enumerate(taus)]
        self.last_residual = max([abs(v) for v in full_r] + [0.0])
        return a
