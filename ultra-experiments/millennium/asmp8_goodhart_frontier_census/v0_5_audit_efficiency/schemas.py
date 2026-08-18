CONDITION_FIELDS = [
    "error_family", "streams", "seed", "instrument_failure_streams", "failure_cp_upper_95"
]
POLICY_FIELDS = [
    "error_family", "policy_id", "optimizer_family", "true_gain",
    "hoeffding_minimum", "hoeffding_median", "empirical_bernstein_minimum",
    "empirical_bernstein_q25", "empirical_bernstein_median",
    "empirical_bernstein_q75", "empirical_bernstein_maximum",
    "empirical_bernstein_censored", "movement_partial_census", "full_census",
]
CDF_FIELDS = [
    "error_family", "policy_id", "optimizer_family", "checkpoint",
    "empirical_bernstein_crossing_fraction_descriptive", "mean_margin",
]
