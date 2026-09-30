"""Reaction delay: time-ordered buffer returning state from reaction_time ago.

PROVISIONAL single scalar (visual 150-250 ms, proprioceptive 30-50 ms collapsed
to one number; varies by modality/fatigue in reality). Default 0.2 s.
Zero delay = latest state (backward compatible). Deterministic.
Queries must be nondecreasing in t (control loops always are); old entries
past the delay horizon are pruned, keeping at least one. If no entry is old
enough (e.g., t < reaction_time at match start), the oldest available state
is returned: no reaction can precede perception plus delay.
"""


class ReactionDelay:
    def __init__(self, reaction_time=0.2):
        self.rt = float(reaction_time)
        self.buf = []  # [(t, state)]

    def buffer(self, sensory_state, t):
        self.buf.append((float(t), sensory_state))
        while len(self.buf) > 2 and self.buf[0][0] < t - self.rt:
            self.buf.pop(0)

    def get_delayed(self, t):
        if not self.buf:
            raise ValueError("buffer empty: call buffer() before get_delayed()")
        best = self.buf[0][1]
        for ti, si in self.buf:
            if ti <= t - self.rt:
                best = si
            else:
                break
        return best

    def reset(self):
        self.buf = []
