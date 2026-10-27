"""Print a reproducible, explicitly synthetic risk-comparison receipt."""
from __future__ import annotations

import json
from rsi_topology.catastrophe_decision import (
    CausalDeltas, Governance, Interval, LossModel, audit_comparison,
    finite_frc_tail_audit,
)


def main() -> None:
    data = CausalDeltas(Interval(-0.08, -0.06), Interval(0.005, 0.01),
                        ("fixture:A", "fixture:B"), "toy-v1", "assessed")
    governance = Governance(True, True, True, True)
    model = LossModel(10, 15, Interval(.01, .02))
    result = {
        "synthetic_example": audit_comparison(data, governance, model, asserted="benefit"),
        "frc_observed_only": finite_frc_tail_audit([1, .9, .6, .95]),
    }
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
