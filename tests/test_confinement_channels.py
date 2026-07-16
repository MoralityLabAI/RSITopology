from __future__ import annotations

import numpy as np
import pytest

from rsi_topology.confinement_experiments.channels import (
    FiniteAlphabet,
    FiniteController,
    LinearPlant,
    ReadSymbol,
    WriteSymbol,
    assert_no_side_channel,
    make_center_cancelling_loop,
)


def test_alphabets_reject_analog_and_out_of_range_symbols():
    alphabet = FiniteAlphabet(2, "read")
    assert alphabet.check(1) == 1
    with pytest.raises(TypeError):
        alphabet.check(0.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        alphabet.check(2)


def test_controller_accepts_only_read_symbols_and_emits_finite_write_symbols():
    read = FiniteAlphabet(2, "read")
    write = FiniteAlphabet(2, "write")
    controller = FiniteController(read, write, (1, 0))
    assert controller.act(ReadSymbol(0)) == WriteSymbol(1)
    with pytest.raises(TypeError):
        controller.act(np.array([0.0]))  # type: ignore[arg-type]


def test_side_channel_audit_rejects_hidden_plant_reference():
    controller = FiniteController(
        FiniteAlphabet(1, "read"), FiniteAlphabet(1, "write"), (0,)
    )
    object.__setattr__(controller, "hidden_plant", LinearPlant(np.eye(1), np.eye(1)))
    with pytest.raises(ValueError, match="side channel"):
        assert_no_side_channel(controller)


def test_center_cancelling_loop_bounds_every_scalar_cell_endpoint():
    loop = make_center_cancelling_loop(
        np.array([[1.2]]),
        np.eye(1),
        [1.0],
        [2],
        read_alphabet_size=2,
        write_alphabet_size=2,
    )
    for state in (-1.0, 0.0, 1.0):
        next_state, read, write = loop.step([state])
        assert isinstance(read, ReadSymbol)
        assert isinstance(write, WriteSymbol)
        assert abs(next_state[0]) <= 0.6 + 1e-12
