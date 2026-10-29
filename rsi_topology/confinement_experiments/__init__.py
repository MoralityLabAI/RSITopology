"""CPU-only validation instruments for evaluator-relative confinement width."""

from .channels import (
    ActuatorDecoder,
    FiniteAlphabet,
    FiniteController,
    LinearPlant,
    ReadSymbol,
    SplitChannelLoop,
    UniformBoxSensor,
    WriteSymbol,
    assert_no_side_channel,
)
from .linear import (
    aligned_box_cover_bits,
    classify_split_rate,
    finite_horizon_volume_lower_bits,
    unstable_entropy_bits,
)

__all__ = [
    "ActuatorDecoder",
    "FiniteAlphabet",
    "FiniteController",
    "LinearPlant",
    "ReadSymbol",
    "SplitChannelLoop",
    "UniformBoxSensor",
    "WriteSymbol",
    "aligned_box_cover_bits",
    "assert_no_side_channel",
    "classify_split_rate",
    "finite_horizon_volume_lower_bits",
    "unstable_entropy_bits",
]
