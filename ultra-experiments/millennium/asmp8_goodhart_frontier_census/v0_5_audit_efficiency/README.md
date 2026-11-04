# ASMP-8 v0.5 audit-efficiency frontier

This CPU-only experiment compares the frozen Hoeffding hitting time with a
shared empirical-Bernstein audit, a deterministic policy-movement-ordered
partial census, and complete enumeration.

Every method uses a monotone positive-margin crossing. Crossing fractions are
descriptive and never become decision thresholds.

After prospective registration:

```powershell
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_5_audit_efficiency/run.py
python ultra-experiments/millennium/asmp8_goodhart_frontier_census/v0_5_audit_efficiency/verify_result.py
```
