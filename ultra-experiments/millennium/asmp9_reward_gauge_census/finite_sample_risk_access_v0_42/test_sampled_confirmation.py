from fractions import Fraction as Q

from sampled_confirmation import (
    exact_bernoulli_count,
    sample_shared_flip_channels,
    seed_from_registration_bytes,
)


def test_registration_seed_is_deterministic_and_content_bound():
    first = seed_from_registration_bytes(b"registration-a")
    assert first == seed_from_registration_bytes(b"registration-a")
    assert first != seed_from_registration_bytes(b"registration-b")


def test_exact_bernoulli_stream_is_deterministic():
    seed = bytes(range(32))
    first = exact_bernoulli_count(seed, "q/t0", 100, Q(1, 3))
    assert first == exact_bernoulli_count(
        seed, "q/t0", 100, Q(1, 3)
    )
    assert first != exact_bernoulli_count(
        seed, "q/t1", 100, Q(1, 3)
    )


def test_exact_bernoulli_endpoints_are_exact():
    seed = bytes(range(32))
    assert exact_bernoulli_count(seed, "zero", 37, Q(0)) == 0
    assert exact_bernoulli_count(seed, "one", 37, Q(1)) == 37


def test_sampled_shared_parameter_is_pooled_over_all_targets():
    channels, receipt = sample_shared_flip_channels(
        samples_per_target=7,
        seed=bytes(range(32)),
    )
    assert len(channels) == 3
    for query in channels:
        row = receipt[query.name]
        assert row["pooled_trials"] == 28
        assert row["pooled_flips"] == sum(
            row["flip_counts_by_target"]
        )
        empirical = Q(row["empirical_error_rate"])
        for target, signature in enumerate(
            (0, 0, 1, 1)
            if query.name == "root_q"
            else (
                (0, 1, 0, 0)
                if query.name == "left_q"
                else (0, 0, 0, 1)
            )
        ):
            expected = (
                (Q(1) - empirical, empirical)
                if signature == 0
                else (empirical, Q(1) - empirical)
            )
            assert query.rows[target] == expected
