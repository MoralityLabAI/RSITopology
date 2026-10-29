import verify_theorems_v0_56 as verifier


def test_modular_rank_detects_full_and_deficient_matrices():
    assert verifier.modular_rank([[1, 0], [0, 1]]) == 2
    assert verifier.modular_rank([[1, 2], [2, 4]]) == 1


def test_integer_partitions_cover_registered_gap_boundary():
    for n in range(3, 10):
        partitions = tuple(verifier.integer_partitions(n))
        assert (n,) in partitions
        assert tuple(1 for _ in range(n)) in partitions
        for partition in partitions:
            if len(partition) < 2:
                continue
            cross = sum(
                partition[i] * partition[j]
                for i in range(len(partition))
                for j in range(i + 1, len(partition))
            )
            assert cross > len(partition) - 1


def test_seeded_witness_domain_suite_is_proper_and_stable():
    first = verifier.witness_domains(5, 560026)
    second = verifier.witness_domains(5, 560026)
    assert first == second
    assert len(first) >= len(verifier.menus(5)) + 130
    assert all(set(domain) != set(verifier.menus(5)) for domain in first)
