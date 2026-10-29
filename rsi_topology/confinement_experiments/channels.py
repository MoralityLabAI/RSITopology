"""Structurally separated finite read/write channels for linear plants."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class FiniteAlphabet:
    size: int
    name: str

    def __post_init__(self) -> None:
        if isinstance(self.size, bool) or not isinstance(self.size, int) or self.size < 1:
            raise ValueError("alphabet size must be a positive integer")

    def check(self, value: int) -> int:
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
            raise TypeError(f"{self.name} symbol must be an integer")
        result = int(value)
        if not 0 <= result < self.size:
            raise ValueError(f"{self.name} symbol {result} outside [0, {self.size})")
        return result


@dataclass(frozen=True)
class ReadSymbol:
    value: int


@dataclass(frozen=True)
class WriteSymbol:
    value: int


@dataclass(frozen=True)
class LinearPlant:
    A: np.ndarray
    B: np.ndarray

    def __post_init__(self) -> None:
        A = np.asarray(self.A, dtype=float)
        B = np.asarray(self.B, dtype=float)
        if A.ndim != 2 or A.shape[0] != A.shape[1]:
            raise ValueError("A must be square")
        if B.ndim != 2 or B.shape[0] != A.shape[0]:
            raise ValueError("B row dimension must match A")
        if not np.all(np.isfinite(A)) or not np.all(np.isfinite(B)):
            raise ValueError("plant matrices must be finite")
        object.__setattr__(self, "A", A.copy())
        object.__setattr__(self, "B", B.copy())

    def step(self, state: Sequence[float], control: Sequence[float]) -> np.ndarray:
        x = np.asarray(state, dtype=float)
        u = np.asarray(control, dtype=float)
        if x.shape != (self.A.shape[0],):
            raise ValueError("state has wrong dimension")
        if u.shape != (self.B.shape[1],):
            raise ValueError("control has wrong dimension")
        return self.A @ x + self.B @ u


@dataclass(frozen=True)
class UniformBoxSensor:
    """Finite sensor partition in a registered orthogonal coordinate frame."""

    basis: np.ndarray
    half_widths: np.ndarray
    bins_per_axis: tuple[int, ...]
    alphabet: FiniteAlphabet

    def __post_init__(self) -> None:
        basis = np.asarray(self.basis, dtype=float)
        widths = np.asarray(self.half_widths, dtype=float)
        bins = tuple(int(value) for value in self.bins_per_axis)
        if basis.ndim != 2 or basis.shape[0] != basis.shape[1]:
            raise ValueError("sensor basis must be square")
        if widths.shape != (basis.shape[0],) or np.any(widths <= 0):
            raise ValueError("sensor half-widths must be positive and match basis")
        if len(bins) != basis.shape[0] or any(value < 1 for value in bins):
            raise ValueError("bins_per_axis must be positive and match basis")
        if int(np.prod(bins, dtype=object)) > self.alphabet.size:
            raise ValueError("sensor partition exceeds read alphabet")
        if not np.allclose(basis.T @ basis, np.eye(basis.shape[0]), atol=1e-10):
            raise ValueError("sensor basis must be orthogonal")
        object.__setattr__(self, "basis", basis.copy())
        object.__setattr__(self, "half_widths", widths.copy())
        object.__setattr__(self, "bins_per_axis", bins)

    def encode(self, state: Sequence[float]) -> ReadSymbol:
        x = np.asarray(state, dtype=float)
        if x.shape != self.half_widths.shape:
            raise ValueError("state has wrong dimension")
        coordinates = self.basis.T @ x
        normalized = (coordinates + self.half_widths) / (2.0 * self.half_widths)
        indices = np.floor(normalized * np.asarray(self.bins_per_axis)).astype(int)
        indices = np.clip(indices, 0, np.asarray(self.bins_per_axis) - 1)
        flat = int(np.ravel_multi_index(tuple(indices), self.bins_per_axis))
        return ReadSymbol(self.alphabet.check(flat))

    def cell_center(self, symbol: ReadSymbol) -> np.ndarray:
        flat = self.alphabet.check(symbol.value)
        if flat >= int(np.prod(self.bins_per_axis, dtype=object)):
            raise ValueError("read symbol is unused by this sensor")
        index = np.asarray(np.unravel_index(flat, self.bins_per_axis), dtype=float)
        bins = np.asarray(self.bins_per_axis, dtype=float)
        coordinates = -self.half_widths + (index + 0.5) * (2.0 * self.half_widths / bins)
        return self.basis @ coordinates


@dataclass(frozen=True)
class FiniteController:
    """A pure finite-symbol map with no state or plant reference."""

    read_alphabet: FiniteAlphabet
    write_alphabet: FiniteAlphabet
    symbol_map: tuple[int, ...]

    def __post_init__(self) -> None:
        mapping = tuple(int(value) for value in self.symbol_map)
        if len(mapping) != self.read_alphabet.size:
            raise ValueError("controller map must cover the read alphabet")
        for value in mapping:
            self.write_alphabet.check(value)
        object.__setattr__(self, "symbol_map", mapping)

    def act(self, symbol: ReadSymbol) -> WriteSymbol:
        if not isinstance(symbol, ReadSymbol):
            raise TypeError("controller accepts ReadSymbol only")
        read_value = self.read_alphabet.check(symbol.value)
        return WriteSymbol(self.write_alphabet.check(self.symbol_map[read_value]))


@dataclass(frozen=True)
class ActuatorDecoder:
    alphabet: FiniteAlphabet
    codebook: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        if len(self.codebook) != self.alphabet.size:
            raise ValueError("actuator codebook must cover the write alphabet")
        arrays = [np.asarray(value, dtype=float) for value in self.codebook]
        if not arrays or any(array.ndim != 1 for array in arrays):
            raise ValueError("each actuator codeword must be a vector")
        if len({array.shape for array in arrays}) != 1:
            raise ValueError("actuator codewords must share one dimension")
        if any(not np.all(np.isfinite(array)) for array in arrays):
            raise ValueError("actuator codewords must be finite")
        object.__setattr__(self, "codebook", tuple(tuple(map(float, a)) for a in arrays))

    def decode(self, symbol: WriteSymbol) -> np.ndarray:
        if not isinstance(symbol, WriteSymbol):
            raise TypeError("actuator accepts WriteSymbol only")
        value = self.alphabet.check(symbol.value)
        return np.asarray(self.codebook[value], dtype=float)


def _contains_forbidden_reference(value: Any, forbidden: tuple[type, ...], seen: set[int]) -> bool:
    identity = id(value)
    if identity in seen:
        return False
    seen.add(identity)
    if isinstance(value, forbidden):
        return True
    if isinstance(value, np.ndarray):
        return True
    if isinstance(value, Mapping):
        return any(
            _contains_forbidden_reference(item, forbidden, seen) for item in value.values()
        )
    if isinstance(value, (list, tuple, set)):
        return any(_contains_forbidden_reference(item, forbidden, seen) for item in value)
    if is_dataclass(value):
        return any(
            _contains_forbidden_reference(getattr(value, field.name), forbidden, seen)
            for field in fields(value)
        )
    return False


def assert_no_side_channel(controller: Any) -> None:
    """Fail closed on analog state, plant, sensor, actuator, RNG, or callback references."""

    if not isinstance(controller, FiniteController):
        raise TypeError("primary finite-channel runs require FiniteController")
    forbidden = (LinearPlant, UniformBoxSensor, ActuatorDecoder, np.random.Generator)
    for value in vars(controller).values():
        if _contains_forbidden_reference(value, forbidden, set()):
            raise ValueError("controller contains an analog or shared-object side channel")
        if callable(value):
            raise ValueError("controller callbacks are prohibited")


@dataclass(frozen=True)
class SplitChannelLoop:
    plant: LinearPlant
    sensor: UniformBoxSensor
    controller: FiniteController
    actuator: ActuatorDecoder

    def __post_init__(self) -> None:
        assert_no_side_channel(self.controller)
        if self.sensor.alphabet != self.controller.read_alphabet:
            raise ValueError("sensor/controller read alphabets do not match")
        if self.controller.write_alphabet != self.actuator.alphabet:
            raise ValueError("controller/actuator write alphabets do not match")

    def step(self, state: Sequence[float]) -> tuple[np.ndarray, ReadSymbol, WriteSymbol]:
        read = self.sensor.encode(state)
        write = self.controller.act(read)
        control = self.actuator.decode(write)
        return self.plant.step(state, control), read, write


def make_center_cancelling_loop(
    A: np.ndarray,
    basis: np.ndarray,
    half_widths: Sequence[float],
    bins_per_axis: Sequence[int],
    *,
    read_alphabet_size: int,
    write_alphabet_size: int,
) -> SplitChannelLoop:
    """Construct the explicit eigen-box center-cancelling controller."""

    A = np.asarray(A, dtype=float)
    dimension = A.shape[0]
    read_alphabet = FiniteAlphabet(int(read_alphabet_size), "read")
    write_alphabet = FiniteAlphabet(int(write_alphabet_size), "write")
    sensor = UniformBoxSensor(
        np.asarray(basis, dtype=float),
        np.asarray(half_widths, dtype=float),
        tuple(int(value) for value in bins_per_axis),
        read_alphabet,
    )
    used = int(np.prod(sensor.bins_per_axis, dtype=object))
    if used > write_alphabet.size:
        raise ValueError("constructive policy requires one write codeword per used read cell")
    mapping = tuple(index if index < used else 0 for index in range(read_alphabet.size))
    controller = FiniteController(read_alphabet, write_alphabet, mapping)
    codebook = []
    for index in range(write_alphabet.size):
        if index < used:
            center = sensor.cell_center(ReadSymbol(index))
            codebook.append(tuple((-A @ center).tolist()))
        else:
            codebook.append(tuple(np.zeros(dimension)))
    actuator = ActuatorDecoder(write_alphabet, tuple(codebook))
    plant = LinearPlant(A, np.eye(dimension))
    return SplitChannelLoop(plant, sensor, controller, actuator)
