"""Technique transition state machine (heuristic, M9-flagged).

Conventions: side=+1 (A, own pad at -x): losing = hand_velocity < 0.
side=-1 (B): losing = hand_velocity > 0. In general: losing = v*self.side < 0.
Winning = opponent's hand moving toward opponent's pad = v_opp*self.side > 0.
Thresholds/timings are PROVISIONAL heuristics (tactical planning deferred).
"""
import warnings


class TechniqueTransitioner:
    def __init__(self, offensive=("top_roll", "hook", "press"), defensive="defensive",
                 side=+1, lose_time=0.5, stalemate_time=2.0,
                 opp_speed_threshold=0.1, vel_eps=1e-6, initial="top_roll"):
        self.offensive = list(offensive)
        self.defensive = defensive
        self.side = side
        self.lose_time = float(lose_time)
        self.stale_time = float(stalemate_time)
        self.opp_thresh = float(opp_speed_threshold)
        self.eps = float(vel_eps)
        self.current = initial
        self.preferred = initial
        self.lose_timer = 0.0
        self.stale_timer = 0.0
        self.off_idx = 0
        warnings.warn("[Transitions] heuristic rules (PROVISIONAL timings); tactical planning deferred.",
                      UserWarning, stacklevel=2)

    def reset(self):
        self.current = self.preferred
        self.lose_timer = 0.0
        self.stale_timer = 0.0
        self.off_idx = self.offensive.index(self.preferred) if self.preferred in self.offensive else 0

    def decide(self, sensory, dt):
        v, vo = sensory.hand_velocity, sensory.opponent_hand_velocity
        losing = v * self.side < -self.eps
        winning = vo * self.side > self.eps
        opp_fast = abs(vo) > self.opp_thresh
        stale = abs(v) < self.eps and abs(vo) < self.eps
        self.lose_timer = self.lose_timer + dt if losing else 0.0
        self.stale_timer = self.stale_timer + dt if stale else 0.0
        if self.lose_timer > self.lose_time or opp_fast:
            self.current = self.defensive
            self.stale_timer = 0.0
        elif self.stale_timer > self.stale_time:
            self.off_idx = (self.off_idx + 1) % len(self.offensive)
            self.current = self.offensive[self.off_idx]
            self.stale_timer = 0.0
        elif winning and self.current == self.defensive:
            self.current = self.preferred
        return self.current
